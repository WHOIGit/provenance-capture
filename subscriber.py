import time
from provenance.capture import Logger, Subscriber


logger = Logger.stdout()

subscriber = Subscriber(logger, 'localhost', 'guest', 'guest', 'provenance')

subscriber.start()
