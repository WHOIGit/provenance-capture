import time
from provenance.capture import Logger
from provenance.amqp import Subscriber


logger = Logger.stdout()

subscriber = Subscriber('localhost', 'provenance', logger)

subscriber.start()

# now go into an infinite loop to keep the subscriber running

while True:
    time.sleep(1)
