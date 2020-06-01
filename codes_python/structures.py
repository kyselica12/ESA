from collections import namedtuple
from dataclasses import dataclass
from typing import List, Tuple
from database import Database
import numpy as np



# WrapperResult = namedtuple('WrapperResult', 'result noise log message code')
# Step = namedtuple('Step', 'code x y')

# Stats = namedtuple('Stat', 'started nulldata notenough notbright nocentre maxiter miniter lowsnr ok notright')

# SerialResult = namedtuple('SerialRestul', 'database discarded stats')


@dataclass
class WrapperResult:
    result: List
    noise: int
    log: List
    message: str
    code: int

@dataclass
class Step:
    code: int = -1
    x: int = -1
    y: int = -1

@dataclass
class Stats:
    started: int = 0
    nulldata: int = 0
    notenough: int = 0
    notbright: int = 0
    nocentre: int = 0
    maxiter: int = 0
    miniter: int = 0
    lowsnr: int = 0
    ok: int = 0
    notright: int = 0

@dataclass
class SerialResult:
    database: Database
    discarded: Database
    stats: Stats

@dataclass
class GravityCentreResult:
    center: Tuple
    X_pixels: np.ndarray
    Y_pixels: np.ndarray
    Z_pixels: np.ndarray
