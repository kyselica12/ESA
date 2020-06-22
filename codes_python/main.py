# import external modules

from utils.run_preamble import import_packages
from time import time

t_init = time()
import_packages()

import numpy as np
from astropy.io import fits
# import internal modules
from utils import run_call, report, run_options
from processing import run_serial, run_parallel

args = run_options.read_arguments()  # parse arguments
run_call.save_call(args)  # writes call arguments to file

t_load = time()
image = fits.getdata(args.input)
print('Image loaded')





# switch X is not neede because in python dimensions are in proper order
ALG_PARS = {"CENTRE_LIMIT": 0, "MATCH_LIMIT": 1}

t_cmp = time()
if args.parallel == 1:  # run serial
    log_file = ''
    if args.verbose == 1:
        log_file = f'{args.output}.log'

    print('start serial process')

    process = run_serial.Serial(args, image, log_file='log1.log')
    start = time()
    result = process.execute(index=(0, image.shape[0] - 1, 0, image.shape[1] - 1))
else:
    process = run_parallel.Parallel(args, image)
    start = time()
    result = process.execute()

result.print_stats()
if result.database.size() == 0:
    print('\nNo stars found!')
else:
    t_wrt = time()
    result.database.write_tsv(f'{args.output}_s')
    result.discarded.write_tsv(f'{args.output}_discarded')

    print(f'\nIdentified stars: {len(result.database.data)}')
    print(f'Discarded stars: {len(result.discarded.data)}')

    report_result = report.generate_report(result.database, image, args)

    report_result.print()
    report_result.write_tsv(args.output, result.database)

    t_end = time()

    print("\n------- Time ---------\n")
    print(f'Init time      : {t_load-t_init:.4f} sec')
    print(f'Loading time   : {t_cmp-t_load:.4f} sec')
    print(f'Computing time : {t_wrt-t_cmp:.4f} sec')
    print(f'Write time     : {t_end - t_wrt:.4f} sec')





