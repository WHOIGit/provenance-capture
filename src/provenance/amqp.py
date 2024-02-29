import json
import pika


def amqp_publish(host, queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)

    connection.close()


def amqp_subscribe(host, queue_name, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    def on_message(ch, method, properties, body):
        callback(json.loads(body))

    channel.basic_consume(queue=queue_name,
                          on_message_callback=on_message,
                          auto_ack=True)

    channel.start_consuming()


class Subscriber(object):
    """receive messages from an amqp queue and log them to a provenance capture Logger. assume msgs are json"""
    def __init__(self, host, queue_name, logger):
        self.host = host
        self.queue_name = queue_name
        self.logger = logger

    def start(self):
        def callback(entry):
            self.logger.log(entry)
        amqp_subscribe(self.host, self.queue_name, callback)
