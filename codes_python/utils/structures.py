import json
from dataclasses import dataclass
from typing import List, Tuple
from abc import ABC, abstractmethod
import numpy as np
from utils import run_functions


class DatabaseItem:

    def __init__(self, cent_x=0, cent_y=0, snr=0, iter=0, sum=0, mean=0, var=0, std=0, skew=0, kurt=0, bckg=0,
                 fwhm_x=None, fwhm_y=None, rms=None, skew_x=None, skew_y=None,
                 kurt_x=None, kurt_y=None, bri_error=None):
        self.data = [cent_x, cent_y, snr, iter, sum, mean, var, std, skew, kurt, bckg,
                     fwhm_x, fwhm_y, rms, skew_x, skew_y,
                     kurt_x, kurt_y, bri_error]


class Database:
    col_names = ('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg',
                'fwhm_x', 'fwhm_y', 'fit_rms', 'skew_x', 'skew_y', 'kurt_x', 'kurt_y', 'bri_error')

    def __init__(self, psf=False):
        self.data = np.zeros((0, len(self.col_names))).astype(object)
        self.psf_enabled = psf

    def psf_data_mode(self):
        return not np.any(self.data[11:18] == None)

    def nrows(self):
        return self.data.shape[0]

    def update(self, current: DatabaseItem, thrs):

        current = current.data

        if self.nrows() == 0:
            self.add(current)
            return -1

        dist = np.array(
            [np.sqrt((self.data[i][0] - current[0]) ** 2 + (self.data[i][1] - current[1]) ** 2) for i in
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
        if isinstance(data, DatabaseItem):
            data = data.data
        self.data = np.concatenate((self.data, [data]))

    def concatenate(self, other):
        new = Database()
        new.data = np.concatenate((self.data, other.data))

        return new

    def write_tsv(self, filename):

        sorted_idx = np.argsort(self.data[:, 0])

        ordered = self.data[sorted_idx][:,:11].astype(str)

        if self.psf_data_mode():
            ordered[:, 9] =  list(map(lambda x: f'{x[0]}|{x[1]}|s', self.data[:,16:18]))


        filename = filename
        col_names = self.col_names[:11]

        run_functions.write_tsv(filename, col_names, ordered)

    def compute_brightness_error(self, n_ipx, n_b):
        return

    def size(self):
        return len(self.data)

    def write_json(self, filename):
        tmp = self.data.copy().astype(object)
        if self.psf_data_mode():
            tmp[:, [3, 5, 6, 7, 8, 9]] = None

        run_functions.write_json(filename,self.col_names, tmp)

@dataclass
class WrapperResult:
    result: DatabaseItem
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

        data = np.ones((0,6))
        if len(self.matched) > 0:
            matched_database = database.data[self.matched[:, 0]][:, [0, 1, 4]]
            matched_model = self.model[self.matched[:, 1]]
            data = np.concatenate((matched_database, matched_model), axis=1)

        col_names = ('cent.x', 'cent.y', 'sum', 'cat.x', 'cat.y', 'cat.sum')
        run_functions.write_tsv(filename+'_matched', col_names, data.astype(np.float32))


    def write_json(self, filename, database):

        data = np.ones((0, 6))
        if len(self.matched) > 0:
            matched_database = database.data[self.matched[:, 0]][:, [0, 1, 4]]
            matched_model = self.model[self.matched[:, 1]]
            data = np.concatenate((matched_database, matched_model), axis=1)

        col_names = ('cent.x', 'cent.y', 'sum', 'cat.x', 'cat.y', 'cat.sum')

        run_functions.write_json(filename + '_matched', col_names, data)


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
    match_limit: float
    centre_limit: float
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
