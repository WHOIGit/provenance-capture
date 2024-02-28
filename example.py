import random

from provenance.capture import Step, Logger


# log to a JSONL file
logger = Logger.file('example.log')


# containing step is the whole job
with Step(name='processing job', logger=logger) as job:
    # process a few inputs as part of that job
    for i in range(5):
        try:
            # associate this step with the parent job and hence its logger
            with Step(parent=job) as step:
                # add inputs and outputs
                step.add_input(id=f'input{i}')
                step.add_output(id=f'output{i}')
                # simulate some processing including failure
                if random.random() < 0.5:
                    # failure will cause the step to log the failure and re-raise the exception
                    raise ValueError('Random failure')
        except: # catch and handle the re-raised exception
            print('error processing step')
