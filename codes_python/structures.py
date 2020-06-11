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

    def print_stats(self):
        print('\n-------- Stats ------------\n')
        print(f'Started iterations: {self.stats.started}')
        print(f'   OK             : {self.stats.ok}')
        print(f'   Null data      : {self.stats.nulldata}')
        print(f'   No data        : {self.stats.notenough}')
        print(f'   No bright      : {self.stats.notbright}')
        print(f'   No centre      : {self.stats.nocentre}')
        print(f'   Max iter       : {self.stats.maxiter}')
        print(f'   Min iter       : {self.stats.miniter}')
        print(f'   Low SNR        : {self.stats.lowsnr}')
        print(f'   Not right      : {self.stats.notright}')

@dataclass
class GravityCentreResult:
    center: Tuple
    X_pixels: np.ndarray
    Y_pixels: np.ndarray
    Z_pixels: np.ndarray

@dataclass
class Report:
    matched: np.ndarray
    unmatched: np.ndarray
    model: np.ndarray
    X: float
    Y: float
    rms_x: float
    rms_y: float

    def print(self):

        if self.model is None:
            print(f'Matched starts: 0 out of 0')
        else:
            print(f'Matched starts: {len(self.matched)} out of {len(self.model)}')
            print(f'\taverage error X: {self.X:.4f}')
            print(f'\taverage error Y: {self.Y:.4f}')
            print(f'\tRMS X: {self.rms_x:.4f}')
            print(f'\tRMS Y: {self.rms_y:.4f}')
        print()

    def write_tsv(self, filename, database):

        matched_database = database.data[self.matched[:, 0]][:,[0,1,4]]
        matched_model = self.model[self.matched[:, 1]]
        data = np.concatenate((matched_database, matched_model), axis=1)

        d = Database(init_value=0, nrows=0, ncols=0, col_names=None)
        d.data = data
        d.write_tsv(filename+'_matched')







