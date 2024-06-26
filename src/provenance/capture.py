import json
import datetime

import traceback

from uuid import uuid4

from amqp.rabbit import publish, subscribe


class Logger(object):
    def __init__(self, callback):
        self.callback = callback

    def log(self, entry):
        self.callback(entry)

    @staticmethod
    def stdout():
        return Logger(print)

    @staticmethod
    def file(path):
        def log_to_file(entry):
            with open(path, "a") as file:
                file.write(json.dumps(entry) + "\n")
        return Logger(log_to_file)
    
    @staticmethod
    def cache(appendable):
        def log_to_cache(entry):
            appendable.append(entry)
        return Logger(log_to_cache)

    @staticmethod
    def amqp(host, user, password, exchange_name, exchange_type='fanout', routing_key=''):
        def log_to_amqp(entry):
            publish(entry, host, user, password, exchange_name, exchange_type, routing_key)
        return Logger(log_to_amqp)
    
    @staticmethod
    def fanout(loggers):
        def log_to_fanout(entry):
            for logger in loggers:
                logger.log(entry)
        return Logger(log_to_fanout)
    
    @staticmethod
    def filter(logger, filter=lambda entry: True):
        def log_to_filtered(entry):
            if filter(entry):
                logger.log(entry)
        return Logger(log_to_filtered)


class Step(object):
    def __init__(self, name=None, id=None, version=None, description=None, parent=None, logger=None):
        self.step_id = id if id is not None else str(uuid4())
        self.step_name = name
        self.description = description
        self.version = version
        self.inputs = []
        self.outputs = []
        self.parameters = {}
        self.start_time = None
        self.end_time = None
        self.succeeded = False
        self.error_message = None
        self.error_traceback = None
        self.logger = logger
        if parent is not None:
            try:
                self.parent_id = parent.step_id
                self.parent = parent
            except AttributeError: # assume parent is a parent ID because the Step object is not available locally
                self.parent_id = parent
                self.parent = None
        else:
            self.parent_id = None
            self.parent = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exception_traceback):
        if exc_type is not None:
            self.fail(exception=exc_value)
        else:
            self.end()
        self.log()

    def add_input(self, name=None, id=None, description=None):
        input = {
            "name": name,
            "id": id if id is not None else str(uuid4()),
            "description": description
        }
        self.inputs.append(input)

    def add_output(self, name=None, id=None, description=None):
        output = {
            "name": name,
            "id": id if id is not None else str(uuid4()),
            "description": description
        }
        self.outputs.append(output)
    
    def add_parameter(self, name, value):
        self.parameters[name] = value

    def start(self):
        self.start_time = datetime.datetime.utcnow().isoformat()
    
    def end(self):
        self.end_time = datetime.datetime.utcnow().isoformat()
        self.succeeded = True
    
    def fail(self, message=None, exception=None):
        self.end_time = datetime.datetime.now().isoformat()
        self.succeeded = False
        if message is None and exception is not None:
            self.error_message = str(exception)
            if traceback is not None:
                self.error_traceback = traceback.format_exception(exception)
        self.outputs = []

    def log(self, entry=None):
        if entry is None:
            entry = {
               "stepId": self.step_id,
                "name": self.step_name,
                "version": self.version,
                "description": self.description,
                "parent": self.parent_id,
                "startTime": self.start_time,
                "endTime": self.end_time,
                "succeeded": self.succeeded,
                "errorMessage": self.error_message,
                "errorTraceback": self.error_traceback,
                "inputs": self.inputs,
                "outputs": self.outputs,
                "parameters": self.parameters
            }

        if self.logger is None:
            if self.parent is not None:
                self.parent.log(entry)
            else:
                print(json.dumps(entry))
        else:
            self.logger.log(entry)


class Subscriber(object):
    """receive messages from an amqp queue and log them to a provenance capture Logger. Assumes msgs are json"""
    def __init__(self, logger, host, user, password, exchange_name, exchange_type='fanout', routing_key='', queue_name=''):
        self.host = host
        self.user = user
        self.password = password
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.queue_name = queue_name
        self.logger = logger

    def start(self):
        def callback(entry):
            self.logger.log(entry)
        subscribe(callback, self.host, self.user, self.password, self.exchange_name, self.exchange_type, self.routing_key, self.queue_name)

