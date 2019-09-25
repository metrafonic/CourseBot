# CourseBot
A discord bot for notifying about new courses

## Installing
### Docker image:
https://hub.docker.com/r/metrafonic/coursebot
```
docker pull metrafonic/coursebot
```
```
docker run --env "TOKEN=yourdiscordtoken metrafonic/coursebot"
```
### Source
1. Clone:
  ```
  git clone https://github.com/metrafonic/CourseBot
  cd CourseBot
  ```
2. Run in virtual env with python 3
  ```
  virtualen venv -p python3
  ```
3. Install reuirements
  ```
  pip install -r requirements.txt
  ```
## Running
You need a discord bot token: https://discordapp.com/developers/applications
```
python CourseBot yourtokengoeshere
```
