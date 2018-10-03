import json
import time
import pika
import sqlalchemy as sqlalchemy
from sqlalchemy import Table, MetaData, Column, String, Integer


class RabbitConsumer:
    def __init__(self, rabbit_server_addr, rabbit_server_port, sqlhost, sqluser, sqlpasswd):
        # Establish incoming connection
        credentials = pika.PlainCredentials('orange', 'test5243')
        connection_params = pika.ConnectionParameters(host=rabbit_server_addr, port=rabbit_server_port,
                                                      virtual_host='/', credentials=credentials)
        connection = pika.BlockingConnection(connection_params)
        self.channel_in = connection.channel()
        self.channel_in.queue_declare(queue='bt_wardrive', durable=True)
        self.channel_in.exchange_declare(exchange='bt_wardrive', exchange_type='direct')

        self.sqlhost = sqlhost
        self.sqluser = sqluser
        self.sqlpasswd = sqlpasswd

    # Document received message
    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        self.insert_data(bytes(body).decode())
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def construct_database(self):  # passwd: mysql
        engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}'.format(self.sqluser, self.sqlpasswd, self.sqlhost))
        engine.execute('CREATE DATABASE IF NOT EXISTS wardrive')
        engine.execute('USE wardrive')
        engine.execute(
            'CREATE TABLE IF NOT EXISTS website(row_id INT(11) NOT NULL AUTO_INCREMENT, capture_time varchar(32),'
            ' location varchar(32), ip_addr varchar(32), mac_addr varchar(32), ssid varchar(64), PRIMARY KEY (row_id))')

    def insert_data(self, body):
        """Given the message data, parse the data and store it into the database"""
        # Parse the JSON data
        parsed_json = json.loads(body)
        timestamp = parsed_json['timestamp']
        location = parsed_json['location']
        ip_addr = parsed_json['ip_addr']
        mac_pairs = parsed_json['mac_pairs']

        # Create the cursor for the table
        engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}'.format(self.sqluser, self.sqlpasswd, self.sqlhost))

        # Creating a table cast so raw sql isn't needed
        engine.execute('USE wardrive')
        meta = MetaData(engine)
        table = Table(
            'website', meta,
            Column('row_id', Integer, primary_key=True),
            Column('capture_time', String),
            Column('location', String),
            Column('ip_addr', String),
            Column('mac_addr', String),
            Column('ssid', String))

        # Insert the values for each mac pair
        for mac_addr in mac_pairs:
            ins = table.insert().values(capture_time=timestamp, location=location, ip_addr=ip_addr,
                                        mac_addr=mac_addr, ssid=mac_pairs[mac_addr])
            engine.connect().execute(ins)

    def deconstruct_database(self):
        # # TODO: Refactor this to be more class-oriented
        engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}'.format(self.sqluser, self.sqlpasswd, self.sqlhost))
        engine.execute('DROP DATABASE wardrive')


if __name__ == '__main__':
    server_addr = "129.114.111.193"
    port = 5672
    sql_host = '127.0.0.1'
    sql_user = 'root'
    sql_password = 'mysql'
    consumer = RabbitConsumer(rabbit_server_addr=server_addr, rabbit_server_port=port, sqlhost=sql_host,
                              sqluser=sql_user, sqlpasswd=sql_password)
    consumer.construct_database()
    try:
        print(' [*] Waiting for messages. To exit, press CTRL+C')
        consumer.channel_in.basic_consume(consumer.callback, queue='bt_wardrive')
        consumer.channel_in.start_consuming()
    except KeyboardInterrupt:
        print("\nExiting consumer script...")
        exit()
