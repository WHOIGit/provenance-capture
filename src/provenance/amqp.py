import json
import pika


def amqp_publish(host, user, password, exchange_name, message):
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    channel.basic_publish(exchange=exchange_name,
                          routing_key='',
                          body=json.dumps(message))

    connection.close()


def amqp_subscribe(host, user, password, exchange_name, callback):
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    def on_message(ch, method, properties, body):
        callback(json.loads(body))

    channel.basic_consume(queue=queue_name,
                          on_message_callback=on_message,
                          auto_ack=True)

    channel.start_consuming()


class Subscriber(object):
    """receive messages from an amqp queue and log them to a provenance capture Logger. assume msgs are json"""
    def __init__(self, host, user, password, exchange_name, logger):
        self.host = host
        self.user = user
        self.password = password
        self.exchange_name = exchange_name
        self.logger = logger

    def start(self):
        def callback(entry):
            self.logger.log(entry)
        amqp_subscribe(self.host, self.user, self.password, self.exchange_name, callback)
