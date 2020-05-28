# import external modules
import numpy as np
from astropy.io import fits
from collections import namedtuple

# import internal modules
import run_options
import run_functions
import run_call
import run_parallel
import run_serial




args = run_options.read_arguments() # parse arguments

run_call.save_call(args)  # writes call arguments to file

image = fits.getdata(args.input)

#switch X is not neede because in python dimensions are in proper order

ALG_PARS = {"CENTRE_LIMIT" : 0, "MATCH_LIMIT"  : 1 }

if args.parallel == 1: # run serial
    log_file = ''
    if args.verbose == 1:
        log_file=f'{args.output}.log'

    process = run_serial.Serial(args, image, log_file=log_file)
    result = process.execute(index=0)
        
else:
    process = run_parallel.Parallel(args, image)
    result = process.execute()









