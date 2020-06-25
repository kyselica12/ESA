import argparse
from utils.structures import Configuration
import os

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
                        type = bool,
                        default= False,
                        help = "Flag for using PSF fitting method")


    args = parser.parse_args()

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

    return cfg


