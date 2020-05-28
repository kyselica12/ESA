import numpy as np


class Database:

    def __init__(self, init_value, nrows, ncols, col_names):

        self.data = np.zeros((nrows, ncols))
        self.nrows = nrows
        self.ncols = ncols

        self.col_names = col_names

    def update(self,current, thrs):

        if self.nrows == 0:
            self.data = np.concatenate((self.data, [current]))
            return -1
        
        dist = np.array([np.sqrt((self.data[i][0]-current[0])**2 + (self.data[i][1]-current[1])**2)  for i in range(self.nrows)])

        close_rows = dist < thrs

        if np.sum(close_rows) == 0:
            self.data = np.concatenate((self.data, [current]))
            return 0

        d = np.concatenate((self.data[close_rows], [current]))
        id = np.argmax(d[:,3])
        best = d[id]

        not_close_rows = np.logical_not(close_rows)
        self.data = np.concatenate((self.data[not_close_rows], [best]))

        return 1

    def add(self, data):

        self.data = np.concatenate((self.data, [data]))
