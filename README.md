# Bluetooth Wardrive Environment
This project polls devices from multiple clients for bluetooth device information. That information is then sent to a centralized RabbitMQ broker. The broker passes the data to a dockerized webserver which performs analysis and displays the digested data to the user.

The project is composed of two sections: "Client Setup" & "Server Setup". The client setup is intended to run on a raspberry pi with minimal user interaction. The server setup currently is running on a Digital Ocean service.