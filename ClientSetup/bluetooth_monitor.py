import ast
import json

import bluetooth
from bs4 import BeautifulSoup
from datetime import datetime
import pika
from time import sleep
import urllib3


class BluetoothScanner:
    def __init__(self, rabbit_server_addr, rabbit_server_port):

        print("Initializing website monitor client...")

        self.ip_addr = None
        self.location = None
        self.capture = None
        self.get_relative_location()

        print("Initial IP Address: {}".format(self.ip_addr))
        print("Initial Location: {}".format(self.location))

        # Credentials for external server
        credentials = pika.PlainCredentials('orange', 'test5243')
        connection_params = pika.ConnectionParameters(host=rabbit_server_addr, port=rabbit_server_port,
                                                      virtual_host='/', credentials=credentials)
        connection = pika.BlockingConnection(connection_params)
        self.channel = connection.channel()
        self.channel.queue_declare(queue='bt_wardrive', durable=True)
        self.channel.exchange_declare(exchange='bt_wardrive', exchange_type='direct')

    class MonitorCapture:
        """Inner class used to store the capture data as an object"""

        def __init__(self, timestamp, structure, ip_addr, location):
            self.timestamp = timestamp
            self.mac_pairs = dict()
            self.ip_addr = ip_addr
            self.location = location
            # Given a tuple, create a dictionary of the website devices.
            for entry in structure:
                if isinstance(entry, tuple):
                    self.mac_pairs[entry[0]] = entry[1]

    def get_relative_location(self):
        """Using an ISP locator, get the location closest to the the client"""
        http = urllib3.PoolManager()
        url = 'http://ipinfo.io/json'
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="html5lib")
        soup = str(soup).split("body")[1][1:-2]
        try:
            soup = ast.literal_eval(soup)
            self.ip_addr = soup['ip']
            self.location = soup['loc']
        except Exception as e:
            print("Approximate address can not be determined...")
            self.ip_addr = None
            self.location = None

    def scan_bluetooth(self):
        """Scan nearby website networks"""
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        print("Found {} devices at {}".format(len(nearby_devices), datetime.now()))
        timestamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        self.capture = self.MonitorCapture(timestamp=timestamp, structure=nearby_devices, ip_addr=self.ip_addr,
                                           location=self.location)
        for name, addr in nearby_devices:
            print(" %s - %s" % (addr, name))

        self.capture = json.dumps(self.capture.__dict__)

    def transmit_to_server(self):
        """Send the capture object to the RabbitMQ broker"""
        # If a server argument was not given then exit the program
        self.channel.basic_publish(exchange='', routing_key='bt_wardrive', body=self.capture,
                                   properties=pika.BasicProperties(delivery_mode=2))


if __name__ == '__main__':
    server_addr = "129.114.111.193"
    port = 5672
    btscanner = BluetoothScanner(rabbit_server_addr=server_addr, rabbit_server_port=port)
    try:
        while True:
            btscanner.scan_bluetooth()
            btscanner.transmit_to_server()
            sleep(15)
    except KeyboardInterrupt:
        print("\nExiting client script...")
        exit()
