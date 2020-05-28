from structures import *
from database import Database
from typing import List

# def switch_X(F):
#     return(apply(t(F[,ncol(F):1]),2,rev))
# -> not neede in numpy axis are in good order already

# remove negative values
def remove_negative(v,val):
    v[v<0] = val
    return v

def combine_results(results : List[SerialResult]):

    names = ('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
    database  = Database(init_value=0, nrows=0, ncols=11, col_names=names )
    discarded = Database(init_value=0, nrows=0, ncols=11, col_names=names )
    
    started   = 0
    nulldata  = 0
    notenough = 0
    notbright = 0
    nocentre  = 0
    maxiter   = 0
    miniter   = 0
    lowsnr    = 0
    ok        = 0
    notright  = 0

    for result in results:
        database = database.concatenate(result.database)
        discarded = database.concatenate(result.discarded)

        started  += result.started
        nulldata += result.nulldata
        notenough+= result.notenough
        notbright+= result.notbright
        nocentre += result.nocentre
        maxiter  += result.maxiter
        miniter  += result.miniter
        lowsnr   += result.lowsnr
        ok       += result.ok
        notright += result.notright

    return SerialResult(database=database,
                            discarded=discarded,
                            stats=Stats(started=started,
                                        nulldata=nulldata,
                                        notbright=notbright,
                                        notenough=notenough,
                                        nocentre=nocentre,
                                        maxiter=maxiter,
                                        miniter=miniter,
                                        lowsnr=lowsnr,
                                        ok=ok,
                                        notright=notright
                                        )
                            )
