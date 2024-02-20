import json
import datetime

import traceback

from uuid import uuid4

class Step(object):
    def __init__(self, name=None, id=None, version=None, description=None, reraise=True):
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
        self.reraise = reraise
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exception_traceback):
        if exc_type is not None:
            self.fail(exception=exc_value)
            self.log()
            return not self.reraise
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

    def log(self):
        log_entry = {
            "stepId": self.step_id,
            "name": self.step_name,
            "version": self.version,
            "description": self.description,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "succeeded": self.succeeded,
            "errorMessage": self.error_message,
            "errorTraceback": self.error_traceback,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters
        }
        # dump json to a single line
        print(json.dumps(log_entry))
