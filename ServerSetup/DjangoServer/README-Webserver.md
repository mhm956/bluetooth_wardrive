Notes for installing the Webserver

* Installed Docker
* ```sudo usermod -a -G docker $USER```

Removed Apache
* ```sudo apt-get purge apache2 apache2-utils apache2.2-bin apache2-common```

Build the webserver
* ```docker build -t webapp .```

Run the webserver
* ```docker run -d -p 80:80 webapp```

