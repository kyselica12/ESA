from collections import namedtuple
from dataclasses import dataclass



WrapperResult = namedtuple('WrapperResult', 'result noise log message code')
Step = namedtuple('Step', 'code x y')