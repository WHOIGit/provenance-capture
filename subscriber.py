import time
from provenance.capture import Logger
from provenance.amqp import Subscriber


logger = Logger.stdout()

subscriber = Subscriber('localhost', 'provenance', logger)

subscriber.start()
