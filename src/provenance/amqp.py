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
