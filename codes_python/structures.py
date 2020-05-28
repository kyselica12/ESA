from collections import namedtuple
from dataclasses import dataclass



WrapperResult = namedtuple('WrapperResult', 'result noise log message code')
Step = namedtuple('Step', 'code x y')

Stats = namedtuple('Stat', 'started nulldata notenough notbright nocentre maxiter miniter lowsnr ok notright')

SerialResult = namedtuple('SerialRestul', 'database discarded stats')
