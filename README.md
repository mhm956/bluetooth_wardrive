# Setting up the Bluetooth Scanner Client
## Dependencies
```bash
sudo apt upgrade
sudo apt install python3-pip python3-dev ipython
sudo apt install bluetooth libbluetooth-dev
pip3 install pybluez pika
```

## Running the client
```bash
python3 ./ClientSetup/bluetooth_monitor.py
```

# Consumer Setup
```bash
sudo apt-get install python3-dev libmysqlclient-dev mysql-server
sudo pip3 install pymysql sqlalchemy
mysql_secure_installation
```

*Alternatively, you can use:*
```sudo easy_install sqlalchemy```

Check that the service is running
```
systemctl status mysql.service
```

## To Expose MySQL to the external port 
```
vim /etc/mysql/my.cnf
# Change "bind-address = 127.0.0.1" --> "bind-address = 0.0.0.0"

sudo service mysql stop
sudo service mysql start
mysql -u root -p
```
In the mysql terminal
```mysql
CREATE USER 'root'@'%' IDENTIFIED BY 'mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```