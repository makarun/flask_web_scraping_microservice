import app
import unittest
import json

class MyTestCase(unittest.TestCase):

	def setUp(self):
		app.app.testing = True
		self.app = app.app.test_client()

	def test_download_img(self):
		result = self.app.get('/api/download_img/http://google.com')

		assert result.status == '200 OK'

		answer = json.loads(result.data)

		assert answer['path'] == 'http://google.com'
		assert answer['is_done'] == False

	def test_download_text(self):
		result = self.app.get('/api/download_text/http://google.com')

		assert result.status == '200 OK'

		answer = json.loads(result.data)

		assert answer['path'] == 'http://google.com'
		assert answer['is_done'] == False

	def test_check_status(self):
		task_id = json.loads(self.app.get('/api/download_img/http://google.com').data)['id']
		result = self.app.get('/api/check_status/'+str(task_id))
		answer = json.loads(result.data)

		assert answer['task_id'] == task_id
		assert answer['is_done'] == False
		assert answer['path'] == 'http://google.com'

