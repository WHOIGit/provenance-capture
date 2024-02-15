# Simple provenance capture

This module is designed to do simple provenance logging in JSONL.

The simplest way to use it is with the `Step` context manager, as in this overly simple example:

```python
import random

from provenance.capture import Step

with Step() as step:
    step.add_input('input1', 'input1_id', 'input1_description')
    step.add_output('output1', 'output1_id', 'output1_description')
    step.add_parameter('param1', 'param1_value')
    if random.random() < 0.5:
        raise ValueError('Random failure')
```

The result will be to print a one-line JSON record describing the run (or failure, if it randomly fails).
