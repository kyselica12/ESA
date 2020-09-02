import argparse
from utils.structures import Configuration
import os
import sys

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def read_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-F', '--input',
                        type=str,
                        default=None,
                        help="Input FITS file")

    parser.add_argument("-A", "--width",
                        type    = float,
                        default = None,
                        help    = "Width of the centroiding rectangle in pixels (default 3)")

    parser.add_argument("-B", "--height",
                        type    = float,
                        default = None,
                        help    = "Height of the centroiding rectangle in pixels (default 3)")

    parser.add_argument("-C", "--angle",
                        type    = float,
                        default = None,
                        help    = "Angle [deg] of the centroiding rectangle from 0 to 90 (default 0)")

    parser.add_argument("-N", "--noise-dim",
                        type    = float,
                        default = None,
                        help    = "Width of noise rim in pixels (default 10)")

    parser.add_argument("-L", "--local-noise",
                        type    = float,
                        default = None,
                        help    = "=0 for no local noise, =1 for local noise computation, =X for given local noise X (default 0)")

    parser.add_argument("-D", "--delta",
                        type    = float,
                        default = None,
                        help    = "Desired precision of the centre in pixels (when the iterations should stop)  (default 0.001)")

    parser.add_argument("-X", "--start-iter",
                        type    = int,
                        default = None,
                        help    = "Min value of brightest pixel to start iterating  (default 1000)"),

    parser.add_argument("-M", "--max-iter",
                        type    = int,
                        default = None,
                        help    = "Max number of iterations  (default 10)")

    parser.add_argument("-I", "--min-iter",
                        type    = int,
                        default = None,
                        help    = "Min number of iterations  (default 2)")

    parser.add_argument("-S", "--snr-lim",
                        type    = int,
                        default = None,
                        help    = "Min signal-to-noise ratio  (default 2)")

    parser.add_argument("-Z", "--color",
                        type    = int,
                        default = None,
                        help    = "3=SNR, 4=iter, 5=sum, 6=mu, 7=var, 8=sd, 9=skew, 10=kurt, 11=BCKG  (default 3)")

    parser.add_argument("-E", "--model",
                        type    = str,
                        default = None,
                        help    = "tsv file with model stars")

    parser.add_argument("-O", "--output",
                        type    = str,
                        default = None,
                        help    = "Path and basename for the result files (default ./results/new)")

    parser.add_argument("-Y", "--cent-pix-perc",
                        type    = float,
                        default = None,
                        help    = "Proportion (in %) of brightest pixels used for centering (default 100)")

    parser.add_argument("-G", "--init-noise-removal",
                        type    = float,
                        default =  None,
                        help    = ">0 to subtract median(IMAGE) from the whole IMAGE, and replace negative values with a given value; =0 to do nothing (default 0)")

    parser.add_argument("-H", "--fine-iter",
                        type    = int,
                        default = None,
                        help    = "Number of fine interations of centroiding after local background was removed but -L (or --local-noise) cannot be zero (default 0)")

    parser.add_argument("-K", "--method",
                        type    = str,
                        default = None,
                        help    = "How to search the image for objects (sweep, max, clusters) (default sweep)")

    parser.add_argument("-P", "--parallel",
                        type    = int,
                        default = None,
                        help    = "Split image into PxP parts and process parallely (default 1)")

    parser.add_argument("-V", "--verbose",
                        type    = int,
                        default = None,
                        help    = "Set 1 to save iteration log if parallel is 1 (default 0)")

    parser.add_argument("-J", "--json-config",
                        type    = str,
                        default = None,
                        help    = "Json file with default configuration.")

    parser.add_argument("--sobel-threshold",
                        type    = float,
                        default = None,
                        help    = "Sobel threshold for sobel segmentation")

    parser.add_argument("--bkg-iterations",
                        type    = int,
                        default = None,
                        help    ="Number of iteration for backgound extraction if PSF is used")

    parser.add_argument("--fit-function",
                        type    = str,
                        default = None,
                        help    = "Fit function for PSF fitting method ('gauss' / 'veres')")

    parser.add_argument('--psf',
                        type = str2bool,
                        default= None,
                        help = "Flag for using PSF fitting method")

    parser.add_argument('--match-limit',
                        type=float,
                        default=None,
                        help= "Accepted distance between stars while matching with .cat")
    parser.add_argument('--centre-limit',
                        type=float,
                        default=None,
                        help="Minimal accepted distance between two found stars")
    parser.add_argument('--pixscale',
                        type=float,
                        default=None,
                        help="Pixel scale")

    args : Configuration = parser.parse_args()

    if args.json_config is None:
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, f'../resources/default_config.json')
        args.json_config = path

    cfg = None
    with open(args.json_config, 'r') as f:
        json_string = f.read()
        cfg = Configuration.from_json(json_string)


    for name in args.__dict__:
        if args.__dict__[name] is not None:
            cfg.__dict__[name] = args.__dict__[name]

    if args.width is None and args.angle is None:
        try:
            width, angle = read_from_fits_header(cfg)
            cfg.width = width
            cfg.angle = angle
        except Exception as e:
            pass

    fields = ["width", "height", "angle", "pixscale"]
    terminate = False
    for name in fields:
        if cfg.__dict__[name] is None:
            print(f'Missing input parameter {name}')
            terminate = True

    if terminate:
        sys.exit(1)

    return cfg

def read_from_fits_header(cfg : Configuration):
    from astropy.io import fits
    import numpy as np

    filename = cfg.input

    hdul = fits.open(filename)
    hdr = hdul[0].header

    exptime = float(hdr['EXPTIME'])
    cfg.pixscale = float(hdr['PIXSCALE'] if hdr['PIXSCALE'] is not None else cfg.pixscale)
    ratrack = float(hdr['RATRACK'])
    detrack = float(hdr['DECTRACK'])

    width = np.sqrt(ratrack**2 + detrack**2) / (cfg.pixscale**2) + cfg.height
    angle = np.degrees(np.pi - np.arctan2(ratrack, detrack))

    return width, angle




