## TODO transform image  ???
# def switch_X(F):
#     return(apply(t(F[,ncol(F):1]),2,rev))


# remove negative values
def remove_negative(v,val):
    v[v<0] = val
    return v



## TODO
# combine results from parallel processing
# combineResults = function(parResults){
#     # reset database
#     DATABASE  = matrix(0, nrow=0, ncol=11)
#     DISCARDED = matrix(0, nrow=0, ncol=11)
    
#     colnames(DATABASE)  = c('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
#     colnames(DISCARDED) = c('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')

#     # stats
#     started   = 0
#     nulldata  = 0
#     notenough = 0
#     notbright = 0
#     nocentre  = 0
#     maxiter   = 0
#     miniter   = 0
#     lowsnr    = 0
#     ok        = 0
#     notright  = 0

#     for(i in 1:length(parResults)){
#         DATABASE  = rbind(DATABASE,  parResults[[i]]$DATABASE)
#         DISCARDED = rbind(DISCARDED, parResults[[i]]$DISCARDED)

#         started   = started   + parResults[[i]]$STATS$started
#         nulldata  = nulldata  + parResults[[i]]$STATS$nulldata
#         notenough = notenough + parResults[[i]]$STATS$notenough
#         notbright = notbright + parResults[[i]]$STATS$notbright
#         nocentre  = nocentre  + parResults[[i]]$STATS$nocentre
#         maxiter   = maxiter   + parResults[[i]]$STATS$maxiter
#         miniter   = miniter   + parResults[[i]]$STATS$miniter
#         lowsnr    = lowsnr    + parResults[[i]]$STATS$lowsnr
#         ok        = ok        + parResults[[i]]$STATS$ok
#         notright  = notright  + parResults[[i]]$STATS$notright
#     }

#     return(list(
#         'DATABASE'  = DATABASE,
#         'DISCARDED' = DISCARDED,
#         'STATS'     = list(
#             'started'   = started,
#             'nulldata'  = nulldata,
#             'notenough' = notenough,
#             'notbright' = notbright,
#             'nocentre'  = nocentre,
#             'maxiter'   = maxiter,
#             'miniter'   = miniter,
#             'lowsnr'    = lowsnr,
#             'ok'        = ok,
#             'notright'  = notright
#         )
#     ))
# }