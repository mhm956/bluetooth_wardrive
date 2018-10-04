import json
import time

import pika
from django.core.management import BaseCommand
from django.core.management import call_command

from website.models import Bluetooth


class Command(BaseCommand):
    help = "Receives data from RabbitMQ broker"

    def add_arguments(self, parser):
        # parser.add_argument('host_ip', nargs="")
        # parser.add_argument('host_port', nargs="")
        pass

    def handle(self, *args, **options):
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
        consumer = RabbitConsumer(rabbit_server_addr="129.114.111.193", rabbit_server_port=5672)
        try:
            print(' [*] Waiting for messages. To exit, press CTRL+C')
            consumer.channel_in.basic_consume(consumer.callback, queue='bt_wardrive')
            consumer.channel_in.start_consuming()
        except KeyboardInterrupt:
            print("\nExiting consumer script...")
            exit()


class RabbitConsumer:
    def __init__(self, rabbit_server_addr, rabbit_server_port):
        # Establish incoming connection
        credentials = pika.PlainCredentials('orange', 'test5243')
        connection_params = pika.ConnectionParameters(host=rabbit_server_addr, port=rabbit_server_port,
                                                      virtual_host='/', credentials=credentials)
        connection = pika.BlockingConnection(connection_params)
        self.channel_in = connection.channel()
        self.channel_in.queue_declare(queue='bt_wardrive', durable=True)
        self.channel_in.exchange_declare(exchange='bt_wardrive', exchange_type='direct')

    # Document received message
    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        self.insert_data(bytes(body).decode())
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    def insert_data(body):
        """Given the message data, parse the data and store it into the database"""
        # Store the data in the database
        parsed_json = json.loads(body)
        mac_pairs = parsed_json['mac_pairs']
        for mac_addr in mac_pairs:
            Bluetooth.objects.create(
                capture_time=parsed_json['timestamp'],
                location=parsed_json['location'],
                ip_address=parsed_json['ip_addr'],
                mac_addr=mac_addr,
                ssid=mac_pairs[mac_addr]
            )
        if mac_pairs == "":
            print("No devices detected")
            Bluetooth.objects.create(
                capture_time=parsed_json['timestamp'],
                location=parsed_json['location'],
                ip_address=parsed_json['ip_addr'],
                mac_addr=parsed_json['mac_pairs'],
                ssid="None"
            )
