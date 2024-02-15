import random

from provenance.capture import Step

with Step() as step:
    step.add_input('input1', 'input1_id', 'input1_description')
    step.add_output('output1', 'output1_id', 'output1_description')
    step.add_parameter('param1', 'param1_value')
    if random.random() < 0.5:
        raise ValueError('Random failure')
