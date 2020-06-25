import json
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


class Database:

    def __init__(self, init_value, nrows, ncols, col_names):
        self.data = np.ones((nrows, ncols)) * init_value
        self.ncols = ncols

        self.col_names = col_names

    def nrows(self):
        return self.data.shape[0]

    def update(self, current, thrs):

        if self.nrows() == 0:
            self.add(current)
            return -1

        dist = np.array([np.sqrt((self.data[i][0] - current[0]) ** 2 + (self.data[i][1] - current[1]) ** 2) for i in
                         range(self.nrows())])

        close_rows = dist < thrs

        if np.sum(close_rows) == 0:
            self.data = np.concatenate((self.data, [current]))
            return 0

        d = np.concatenate((self.data[close_rows], [current]))
        id = np.argmax(d[:, 3])
        best = d[id]

        not_close_rows = np.logical_not(close_rows)
        self.data = np.concatenate((self.data[not_close_rows], [best]))

        return 1

    def add(self, data):
        self.data = np.concatenate((self.data, [data]))

    def concatenate(self, other):
        new = Database(0, 0, self.ncols, self.col_names)
        new.data = np.concatenate((self.data, other.data))

        return new

    def write_tsv(self, filename):

        ordered = self.data[np.argsort(self.data[:, 0])]

        filename = filename + '.tsv'
        with open(filename, 'w') as f:
            if self.col_names is not None:
                print('\t'.join(self.col_names), file=f)
            for line in ordered:
                print('\t'.join(list(map(str, line))), file=f)

    def size(self):
        return len(self.data)

    def write_json(self, filename):


        with open(filename + '.json', 'w') as f:
            for line in self.data:
                print(json.dumps({n: v for n, v in zip(self.col_names, line)}), file=f)



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

        col_names = ('cent.x', 'cent.y', 'sum', 'cat.x', 'cat.y', 'cat.sum')

        d = Database(init_value=0, nrows=0, ncols=0, col_names=col_names)
        d.data = data
        d.write_tsv(filename+'_matched')

    def write_json(self, filename, database):

        matched_database = database.data[self.matched[:, 0]][:, [0, 1, 4]]
        matched_model = self.model[self.matched[:, 1]]
        data = np.concatenate((matched_database, matched_model), axis=1)

        col_names = ('cent.x', 'cent.y', 'sum', 'cat.x', 'cat.y', 'cat.sum')

        d = Database(init_value=0, nrows=0, ncols=0, col_names=col_names)
        d.data = data
        d.write_json(filename + '_matched')





@dataclass
class Configuration:
    input: str
    width: float
    height: float
    angle: float
    noise_dim: float
    local_noise: float
    delta: float
    start_iter: int
    max_iter: int
    min_iter: int
    snr_lim: int
    color: int
    model: str
    output: str
    cent_pix_perc: float
    init_noise_removal: float
    fine_iter: int
    method: str
    parallel: int
    verbose: int
    json_config: str
    sobel_threshold: float
    fit_function: str
    bkg_iterations: int
    psf: bool

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)
