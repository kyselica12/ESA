# import external modules
import numpy as np

from run_preamble import import_packages

import_packages()

from astropy.io import fits
# import internal modules
import run_options
import run_functions
import run_call
import run_parallel
import run_serial
from time import time

args = run_options.read_arguments()  # parse arguments
run_call.save_call(args)  # writes call arguments to file

image = fits.getdata(args.input)
print('Image loaded')

# switch X is not neede because in python dimensions are in proper order
ALG_PARS = {"CENTRE_LIMIT": 0, "MATCH_LIMIT": 1}

if args.parallel == 1:  # run serial
    log_file = ''
    if args.verbose == 1:
        log_file = f'{args.output}.log'

    print('start serial process')

    process = run_serial.Serial(args, image, log_file='log1.log')
    start = time()
    result = process.execute(index=(0, image.shape[0] - 1, 0, image.shape[1] - 1))
    end = time() - start
else:
    process = run_parallel.Parallel(args, image)
    start = time()
    result = process.execute()
    end = time() - start

result.print_stats()
if len(result.database) == 0:
    print('\nNo stars found!')

print(f'\nSUCESS in {end}')

