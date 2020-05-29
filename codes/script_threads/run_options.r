
option_list = list(
# used letters ABCDEFGHIKLMNOPSVXYZ
    make_option(c("-F", "--input"),
                type    = "character",
                default = "14068A_R_1-001_d_m.fit",
                help    = "Input FITS file"),

    make_option(c("-A", "--width"),
                type    = "numeric",
                default = 6.0,
                help    = "Width of the centroiding rectangle in pixels (default 3)"),

    make_option(c("-B", "--height"),
                type    = "numeric",
                default = 6,
                help    = "Height of the centroiding rectangle in pixels (default 3)"),

    make_option(c("-C", "--angle"),
                type    = "numeric",
                default = 0,
                help    = "Angle [deg] of the centroiding rectangle from 0 to 90 (default 0)"),

    make_option(c("-N", "--noise-dim"),
                type    = "numeric",
                default = 10,
                help    = "Width of noise rim in pixels (default 10)"),

    make_option(c("-L", "--local-noise"),
                type    = "numeric",
                default = 1,
                help    = "=0 for no local noise, =1 for local noise computation, =X for given local noise X (default 0)"),

    make_option(c("-D", "--delta"),
                type    = "numeric",
                default = 0.001,
                help    = "Desired precision of the centre in pixels (when the iterations should stop)  (default 0.001)"),

    make_option(c("-X", "--start-iter"),
                type    = "integer",
                default = 22,
                help    = "Min value of brightest pixel to start iterating  (default 1000)"),

    make_option(c("-M", "--max-iter"),
                type    = "integer",
                default = 20,
                help    = "Max number of iterations  (default 10)"),

    make_option(c("-I", "--min-iter"),
                type    = "integer",
                default = 2,
                help    = "Min number of iterations  (default 2)"),

    make_option(c("-S", "--snr-lim"),
                type    = "integer",
                default = 3,
                help    = "Min signal-to-noise ratio  (default 2)"),

    make_option(c("-Z", "--color"),
                type    = "integer",
                default = 3,
                help    = "3=SNR, 4=iter, 5=sum, 6=mu, 7=var, 8=sd, 9=skew, 10=kurt, 11=BCKG  (default 3)"),

    make_option(c("-E", "--model"),
                type    = "character",
                default = NULL,
                help    = "tsv file with model stars"),

    make_option(c("-O", "--output"),
                type    = "character",
                default = '14068A_R_1-001_d_m',
                help    = "Path and basename for the result files (default ./results/new)"),

    make_option(c("-Y", "--cent-pix-perc"),
                type    = "numeric",
                default = '25',
                help    = "Proportion (in %) of brightest pixels used for centering (default 100)"),

    make_option(c("-G", "--init-noise-removal"),
                type    = "numeric",
                default = '10',
                help    = ">0 to subtract median(IMAGE) from the whole IMAGE, and replace negative values with a given value; =0 to do nothing (default 0)"),

    make_option(c("-H", "--fine-iter"),
                type    = "numeric",
                default = '1',
                help    = "Number of fine interations of centroiding after local background was removed but -L (or --local-noise) cannot be zero (default 0)"),

    make_option(c("-K", "--method"),
                type    = "character",
                default = 'sweep',
                help    = "How to search the image for objects (sweep, max, clusters) (default sweep)"),

    make_option(c("-P", "--parallel"),
                type    = "integer",
                default = '1',
                help    = "Split image into PxP parts and process parallely (default 1)"),

    make_option(c("-V", "--verbose"),
                type    = "integer",
                default = '0',
                help    = "Set 1 to save iteration log if parallel is 1 (default 0)")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

# conditions:
stopifnot(sum(opt$method == c('sweep', 'max', 'clusters')) == 1)



#
#option_list = list(
## used letters ABCDEFGHIKLMNOPSVXYZ
#    make_option(c("-F", "--input"),
#                type    = "character",
#                default = NULL,
#                help    = "Input FITS file"),
#
#    make_option(c("-A", "--width"),
#                type    = "numeric",
#                default = 3,
#                help    = "Width of the centroiding rectangle in pixels (default 3)"),
#
#    make_option(c("-B", "--height"),
#                type    = "numeric",
#                default = 3,
#                help    = "Height of the centroiding rectangle in pixels (default 3)"),
#
#    make_option(c("-C", "--angle"),
#                type    = "numeric",
#                default = 0,
#                help    = "Angle [deg] of the centroiding rectangle from 0 to 90 (default 0)"),
#
#    make_option(c("-N", "--noise-dim"),
#                type    = "numeric",
#                default = 10,
#                help    = "Width of noise rim in pixels (default 10)"),
#
#    make_option(c("-L", "--local-noise"),
#                type    = "numeric",
#                default = 0,
#                help    = "=0 for no local noise, =1 for local noise computation, =X for given local noise X (default 0)"),
#
#    make_option(c("-D", "--delta"),
#                type    = "numeric",
#                default = 0.001,
#                help    = "Desired precision of the centre in pixels (when the iterations should stop)  (default 0.001)"),
#
#    make_option(c("-X", "--start-iter"),
#                type    = "integer",
#                default = 1000,
#                help    = "Min value of brightest pixel to start iterating  (default 1000)"),
#
#    make_option(c("-M", "--max-iter"),
#                type    = "integer",
#                default = 10,
#                help    = "Max number of iterations  (default 10)"),
#
#    make_option(c("-I", "--min-iter"),
#                type    = "integer",
#                default = 2,
#                help    = "Min number of iterations  (default 2)"),
#
#    make_option(c("-S", "--snr-lim"),
#                type    = "integer",
#                default = 2,
#                help    = "Min signal-to-noise ratio  (default 2)"),
#
#    make_option(c("-Z", "--color"),
#                type    = "integer",
#                default = 3,
#                help    = "3=SNR, 4=iter, 5=sum, 6=mu, 7=var, 8=sd, 9=skew, 10=kurt, 11=BCKG  (default 3)"),
#
#    make_option(c("-E", "--model"),
#                type    = "character",
#                default = NULL,
#                help    = "tsv file with model stars"),
#
#    make_option(c("-O", "--output"),
#                type    = "character",
#                default = './results/new',
#                help    = "Path and basename for the result files (default ./results/new)"),
#
#    make_option(c("-Y", "--cent-pix-perc"),
#                type    = "numeric",
#                default = '100',
#                help    = "Proportion (in %) of brightest pixels used for centering (default 100)"),
#
#    make_option(c("-G", "--init-noise-removal"),
#                type    = "numeric",
#                default = '0',
#                help    = ">0 to subtract median(IMAGE) from the whole IMAGE, and replace negative values with a given value; =0 to do nothing (default 0)"),
#
#    make_option(c("-H", "--fine-iter"),
#                type    = "numeric",
#                default = '0',
#                help    = "Number of fine interations of centroiding after local background was removed but -L (or --local-noise) cannot be zero (default 0)"),
#
#    make_option(c("-K", "--method"),
#                type    = "character",
#                default = 'sweep',
#                help    = "How to search the image for objects (sweep, max, clusters) (default sweep)"),
#
#    make_option(c("-P", "--parallel"),
#                type    = "integer",
#                default = '1',
#                help    = "Split image into PxP parts and process parallely (default 1)"),
#
#    make_option(c("-V", "--verbose"),
#                type    = "integer",
#                default = '0',
#                help    = "Set 1 to save iteration log if parallel is 1 (default 0)")
#)
#
#opt_parser = OptionParser(option_list=option_list)
#opt = parse_args(opt_parser)
#
## conditions:
#stopifnot(sum(opt$method == c('sweep', 'max', 'clusters')) == 1)
