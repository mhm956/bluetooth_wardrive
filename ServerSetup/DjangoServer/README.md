# Django, uWSGI and Nginx in a container, using Supervisord

## Build Process
#### Build & Run
* `docker build -t webapp .`
* `docker run -d -p 80:80 webapp`
* go to 127.0.0.1 to see if works

_Final operational webserver is located on Docker Hub:_
```bash
docker pull roadrunner2014/orangewebserver:works
```
