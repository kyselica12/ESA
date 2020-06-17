from utils.structures import *
from utils.structures import Database
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
    
    stats = Stats()

    for result in results:
        database = database.concatenate(result.database)
        discarded = database.concatenate(result.discarded)

        stats.started  += result.stats.started
        stats.nulldata += result.stats.nulldata
        stats.notenough+= result.stats.notenough
        stats.notbright+= result.stats.notbright
        stats.nocentre += result.stats.nocentre
        stats.maxiter  += result.stats.maxiter
        stats.miniter  += result.stats.miniter
        stats.lowsnr   += result.stats.lowsnr
        stats.ok       += result.stats.ok
        stats.notright += result.stats.notright

    return SerialResult(database=database, discarded=discarded, stats=stats)
