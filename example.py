import random

from provenance.capture import Step, Logger

logger = Logger.file('example.log')

with Step(name='processing job', logger=logger) as job:
    for i in range(5):
        try:
            with Step(parent=job) as step:
                step.add_input(id=f'input{i}')
                step.add_output(id=f'output{i}')
                if random.random() < 0.5:
                    raise ValueError('Random failure')
        except:
            print('error processing step')
