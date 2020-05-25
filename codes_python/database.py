


class Database:

    def __init__(self, init_value, nrows, ncols, col_names):

        self.data = [[ init_value for c in range(ncols) ] for r in range(nrows)]
        self.nrows = nrows
        self.ncols = ncols

        self.col_names = col_names
