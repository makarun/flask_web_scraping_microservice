from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.parse	# łaczenie linków
import os #do zapisywania na dysku
import re
import requests # do pobierania


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'pictures'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
	os.makedirs(app.config['UPLOAD_FOLDER'])

class Task(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	path = db.Column(db.String)
	is_done = db.Column(db.Boolean)
	images = db.relationship('Image', backref='task', lazy=True)
	webpages = db.relationship('WebPage', backref='task', lazy=True)

class Image(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String)
	alt = db.Column(db.String)
	task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
	path = db.Column(db.String)

	def serialize(self):
		return {
			'id': self.id,
			'name': self.name, 
			'alt': self.alt,
			'path': self.path,
		}

class WebPage(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	text = db.Column(db.Text)
	task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

	def serialize(self):
		return {'id': self.id, 'text': self.text,}


@app.route('/api/download_img/<path:path>')
def download_img(path):
	
	task = Task(path = path, is_done = False)
	db.session.add(task)
	db.session.commit()

	html_page = urlopen(task.path)
	soup = BeautifulSoup(html_page)
	img_tag_list = soup.findAll('img', src=True)
	os.makedirs(app.config['UPLOAD_FOLDER']+'/'+str(task.id))
	for img in img_tag_list:
		r = requests.get(urllib.parse.urljoin(task.path, img['src']))
		img_name = img['src'].split('/')[-1]

		try:
			img_alt = img['alt'] 
		except Exception:
			img_alt=''

		local_adress = os.path.join(app.config['UPLOAD_FOLDER'], str(task.id), img_name)

		with open(local_adress, 'wb') as f:
			f.write(r.content)

		image = Image(task_id = task.id, 
			name = img_name,
			path = os.path.join(str(task.id), img_name),
			alt = img_alt)

		db.session.add(image)
		db.session.commit()

	return jsonify({'path':task.path, 'is_done':task.is_done, 'id':task.id})

@app.route('/api/download_text/<path:path>')
def download_text(path):

	task = Task(path = path, is_done = False)

	db.session.add(task)
	db.session.commit()

	html_page = urlopen(task.path)
	soup = BeautifulSoup(html_page)

	for script in soup(["script", "style"]):
		script.extract()
	text = soup.get_text()
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	text = '\n'.join(chunk for chunk in chunks if chunk)
	
	webpage = WebPage(task_id = task.id, text = text)

	db.session.add(webpage)
	db.session.commit()

	return jsonify({'path':task.path, 'is_done':task.is_done, 'id':task.id})
	
@app.route('/api/check_status/<int:task_id>')
def check_status(task_id):

	task = Task.query.filter_by(id=task_id).first()
	
	return jsonify({'task_id':task.id, 'is_done':task.is_done, 'path':task.path})

@app.route('/api/get_data/<int:task_id>')
def get_data(task_id):

	images = Image.query.filter_by(task_id=task_id).all()

	return jsonify(images=[i.serialize() for i in images])

@app.route("/api/get_pictures/<path:path>")
def get_pictures(path):
	return send_from_directory(app.config['UPLOAD_FOLDER'], path, as_attachment=True)

@app.route("/api/get_text/<int:task_id>")
def get_text(task_id):
	webpages = WebPage.query.filter_by(task_id=task_id).all()
	return jsonify(webpages=[w.serialize() for w in webpages])

if __name__ == '__main__':
	app.run()
