# PTSD Flask Microservice

## ToDo
- write crawler to search entire website for subpages (with modification to models: Task - WebSite -< WebPage/Image)
- use celery to run task in the background
- add redis or external db server to store data
- add authentication with tokens
- add multiprocessing to speed up webscraping
- write tests

## Instruction
docker build -t ptsd_flask_microservice:latest .
docker run -d -p 5000:5000 ptsd_flask_microservice:latest