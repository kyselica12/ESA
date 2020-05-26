import numpy as np
import run_options
import run_functions
import run_call
from astropy.io import fits


args = run_options.read_arguments() # parse arguments

run_call.save_call(args)  # writes call arguments to file

IMAGE = fits.getdata(args.input)

#switch X is not neede because in python dimensions are in proper order

ALG_PARS = {"CENTRE_LIMIT" : 0, "MATCH_LIMIT"  : 1 }

if args.parallel == 1: # run serial
    pass
    











