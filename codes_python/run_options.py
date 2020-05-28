import argparse

def read_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-F', '--input',
                type=str,
                default='',
                help="Input FITS file")

    parser.add_argument("-A", "--width",
                type    = float, 
                default = 3, 
                help    = "Width of the centroiding rectangle in pixels (default 3)")
                    
    parser.add_argument("-B", "--height",
                type    = float, 
                default = 3, 
                help    = "Height of the centroiding rectangle in pixels (default 3)")
                
    parser.add_argument("-C", "--angle",
                type    = float, 
                default = 0, 
                help    = "Angle [deg] of the centroiding rectangle from 0 to 90 (default 0)")
                
    parser.add_argument("-N", "--noise-dim", 
                type    = float, 
                default = 10, 
                help    = "Width of noise rim in pixels (default 10)")
                
    parser.add_argument("-L", "--local-noise", 
                type    = float, 
                default = 0, 
                help    = "=0 for no local noise, =1 for local noise computation, =X for given local noise X (default 0)")
                
    parser.add_argument("-D", "--delta",
                type    = float, 
                default = 0.001, 
                help    = "Desired precision of the centre in pixels (when the iterations should stop)  (default 0.001)")
                
    parser.add_argument("-X", "--start-iter", 
                type    = int, 
                default = 1000, 
                help    = "Min value of brightest pixel to start iterating  (default 1000)"),
                
    parser.add_argument("-M", "--max-iter", 
                type    = int, 
                default = 10, 
                help    = "Max number of iterations  (default 10)")
                
    parser.add_argument("-I", "--min-iter", 
                type    = int, 
                default = 2, 
                help    = "Min number of iterations  (default 2)")
                
    parser.add_argument("-S", "--snr-lim", 
                type    = int, 
                default = 2, 
                help    = "Min signal-to-noise ratio  (default 2)")
                
    parser.add_argument("-Z", "--color", 
                type    = int, 
                default = 3, 
                help    = "3=SNR, 4=iter, 5=sum, 6=mu, 7=var, 8=sd, 9=skew, 10=kurt, 11=BCKG  (default 3)")
                
    parser.add_argument("-E", "--model", 
                type    = str, 
                default = '', 
                help    = "tsv file with model stars")
                
    parser.add_argument("-O", "--output", 
                type    = str, 
                default = './results/new', 
                help    = "Path and basename for the result files (default ./results/new)")
                
    parser.add_argument("-Y", "--cent-pix-perc", 
                type    = float, 
                default = '100', 
                help    = "Proportion (in %) of brightest pixels used for centering (default 100)")
                
    parser.add_argument("-G", "--init-noise-removal", 
                type    = float, 
                default =  0, 
                help    = ">0 to subtract median(IMAGE) from the whole IMAGE, and replace negative values with a given value; =0 to do nothing (default 0)")
                
    parser.add_argument("-H", "--fine-iter", 
                type    = int, 
                default = '0', 
                help    = "Number of fine interations of centroiding after local background was removed but -L (or --local-noise) cannot be zero (default 0)")
                
    parser.add_argument("-K", "--method", 
                type    = str, 
                default = 'sweep', 
                help    = "How to search the image for objects (sweep, max, clusters) (default sweep)")
                
    parser.add_argument("-P", "--parallel",
                type    = int, 
                default = 1, 
                help    = "Split image into PxP parts and process parallely (default 1)")
                
    parser.add_argument("-V", "--verbose",
                type    = int, 
                default = 0, 
                help    = "Set 1 to save iteration log if parallel is 1 (default 0)")



    args = parser.parse_args()


    return args


