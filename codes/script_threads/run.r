time.init = system.time({ #########################################################################  This block:
# general functions                                                                               #  1) loads/installs packages
source('script_threads/run_functions.r')                                                          #  2) loads functions
#                                                                                                 #  3) parses options
# preamble                                                                                        #  4) saves call
source('script_threads/run_preamble.r')                                                           #
#                                                                                                 #
# load input parameters                                                                           #
source('script_threads/run_options.r')                                                            #  <<< creates "opt" GLOBAL VAR
#                                                                                                 #
# save call                                                                                       #
source('script_threads/run_call.r', local=TRUE)                                                   #
}) ################################################################################################

time.load = system.time({##########################################################################  This block:
# load image                                                                                      #  1) opens fits file
FILE  = opt$input                                                                                 #  2) does preliminary image processing
FITS  = readFITS(FILE)
print((FITS$imDat)[1,1:10])
print('-----------------------')                                                                            #
IMAGE = switchX(FITS$imDat)                                                                       #
print(IMAGE[1,1:10])
print(IMAGE[1:10,1])
# print(IMAGE)
#SDPIXLIM = sd(IMAGE)		        # modified by Silha 20200122
#cat('SDPIXLIM ', SDPIXLIM, '\n')    # modified by Silha 20200122

#                                                                                                 #
if(opt$`init-noise-removal` > 0){                                                                 #
    MED = median(IMAGE)                                                                           #
    IMAGE = removeNegative(IMAGE - MED, opt$`init-noise-removal`)                                 #
}                                                                                                 #
#                                                                                                 #
fitsDimX = ncol(IMAGE)                                                                            #  <<< THIS IS GLOBAL VAR
fitsDimY = nrow(IMAGE)                                                                            #  <<< THIS IS GLOBAL VAR
}) ################################################################################################

# print(fitsDimX)
# print(fitsDimY)
# print(IMAGE)
# algoritm params
ALG_PARS = list(                                                                                  #  <<< THIS IS GLOBAL VAR
    # [px] when to consider two stars identical (always take the one with better SNR)
    #"CENTRE_LIMIT" = sqrt(opt$width**2 + opt$height**2),
    "CENTRE_LIMIT" = 0,
    # for matching found objects with catalog (report.r)
    "MATCH_LIMIT"  = 1
)


time.cmp = system.time({###########################################################################  This block executes the main computation,
#                                                                                                 #   either in serial or parallel processing
#                                                                                                 #
# load functions                                                                                  #
source('script_threads/run_serial.r')                                                             #
#                                                                                                 #
if(opt$parallel == 1){                                                                            #
    # write all processing output to log file                                                     #
    if(opt$verbose == 1) sink(paste(opt$output, ".log", sep=""))                                  #
    results = executeSerial(c(1, fitsDimX, 1, fitsDimY))                                          #
    if(opt$verbose == 1) sink()                                                                   #
}else{                                                                                            #
    # there is no log for parallel processing                                                     #
    source('script_threads/run_parallel.r', local=TRUE)                                           #
}                                                                                                 #
})#################################################################################################

# if nothing was found
if(nrow(results$DATABASE) == 0){
    
    cat('\n')
    cat('Identified stars:    ', nrow(results$DATABASE),  '\n')
    cat('Discarded stars:     ', nrow(results$DISCARDED), '\n')
    cat('Matched stars:       ', 0,                       '\n')
    cat('\n')
    
    cat('Started iterations:  ', results$STATS$started,  '\n')
    cat('\tOK:          ',       results$STATS$ok,       '\n')
    cat('\tNull data:   ',       results$STATS$nulldata, '\n')
    cat('\tNo data:     ',       results$STATS$notenough,'\n')
    cat('\tNo bright:   ',       results$STATS$notbright,'\n')
    cat('\tNo centre:   ',       results$STATS$nocentre, '\n')
    cat('\tMax iter:    ',       results$STATS$maxiter,  '\n')
    cat('\tMin iter:    ',       results$STATS$miniter,  '\n')
    cat('\tLow SNR:     ',       results$STATS$lowsnr,   '\n')
    cat('\tNot right:   ',       results$STATS$notright, '\n')
    
    cat('\nInit time:        ', '\n')
    print(time.init)
    
    cat('\nLoading time:     ', '\n')
    print(time.load)
    
    cat('\nComputation time: ', '\n')
    print(time.cmp)
    
    cat('\n')
    stop('No stars found!')
}

# time.wrt = system.time({###########################################################################  This block writes:
# #                                                                                                 #  1) writes database
#     # write found objects                                                                         #  2) produces report.pdf
#     write.table(results$DATABASE[order(results$DATABASE[,1]),],                                   #  3) writes matched objects/stars
# #                paste(opt$output,'.database.tsv', sep=''),                                        #
#                 paste(opt$output,'_s.tsv', sep=''),                                        #
#                 col.names=T, row.names=F, sep='\t')                                               #
# #                                                                                                 #
#     write.table(results$DISCARDED[order(results$DISCARDED[,1]),],                                 #
#                 paste(opt$output,'_discarded.tsv', sep=''),                                       #
#                 col.names=T, row.names=F, sep='\t')                                               #
# #                                                                                                 #
#     # generate PDF report                                                                         #
#     params = list(                                                                                #
#     'fitsDimX' = fitsDimX,                                                                        #
#     'fitsDimY' = fitsDimY,                                                                        #
#     'color'    = opt$color,                                                                       #
#     'angle'    = opt$angle,                                                                       #
#     'model'    = opt$model,                                                                       #
#     'A'        = opt$width,                                                                       #
#     'B'        = opt$height,                                                                      #
#     'ALPHA'    = opt$angle,                                                                       #
#     'report'   = paste(opt$output, '.pdf', sep='')                                                #
#     )                                                                                             #
# #                                                                                                 #
#     report = generateReport(results$DATABASE, IMAGE, params)                                      #
# #                                                                                                 #
#     # save table with matched stars                                                               #
#     if(!is.null(report$model)){                                                                   #
#         write.table(cbind(results$DATABASE[report$matched[,1], 1],                                #
#                           results$DATABASE[report$matched[,1], 2],                                #
#                           results$DATABASE[report$matched[,1], 5],                                #
#                               report$model[report$matched[,2], 1],                                #
#                               report$model[report$matched[,2], 2],                                #
#                               report$model[report$matched[,2], 3]),                               #
#                     file=paste(opt$output,'.matched.tsv', sep=''),                                #
#                     col.names=F, row.names=F, sep='\t')                                           #
#     }                                                                                             #
# }) ################################################################################################

# cat('\n')
# cat('Identified stars:    ', nrow(results$DATABASE),  '\n')
# cat('Discarded stars:     ', nrow(results$DISCARDED), '\n')
# if(is.null(report$model)){
# cat('Matched stars:       ', 0, ' out of ', 0, '\n')
# }else{
# cat('Matched stars:       ', nrow(report$matched), ' out of ', nrow(report$model), '\n')
# cat('  average error X:   ', round(report$X, 4),     '\n')
# cat('  average error Y:   ', round(report$Y, 4),     '\n')
# cat('  RMS X:             ', round(report$RMS.X, 4), '\n')
# cat('  RMS Y:             ', round(report$RMS.Y, 4), '\n')
# }
# cat('\n')

# cat('Started iterations:  ', results$STATS$started,  '\n')
# cat('\tOK:          ',       results$STATS$ok,       '\n')
# cat('\tNull data:   ',       results$STATS$nulldata, '\n')
# cat('\tNo data:     ',       results$STATS$notenough,'\n')
# cat('\tNo bright:   ',       results$STATS$notbright,'\n')
# cat('\tNo centre:   ',       results$STATS$nocentre, '\n')
# cat('\tMax iter:    ',       results$STATS$maxiter,  '\n')
# cat('\tMin iter:    ',       results$STATS$miniter,  '\n')
# cat('\tLow SNR:     ',       results$STATS$lowsnr,   '\n')
# cat('\tNot right:   ',       results$STATS$notright, '\n')

# cat('\nInit time:        ', '\n')
# print(time.init)

# cat('\nLoading time:     ', '\n')
# print(time.load)

# cat('\nComputation time: ', '\n')
# print(time.cmp)

# cat('\nWrite time:       ', '\n')
# print(time.wrt)

# cat('\n')
