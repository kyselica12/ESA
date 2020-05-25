# prepare cluster
P = opt$parallel
no_cores = P**2
cl = makeCluster(no_cores, type="FORK")

# prepare image indices
lenX = fitsDimX %/% P
lenY = fitsDimY %/% P

indices = list()
k = 1
for(i in 1:P){
    # start
    x.start = (i-1)*lenX + 1
    # end
    if(i < P){
        x.end = i*lenX
    }else{
        x.end = fitsDimX
    }
    for(j in 1:P){
        # start
        y.start = (j-1)*lenY + 1
        # end
        if(j < P){
            y.end = j*lenY
        }else{
            y.end = fitsDimY
        }
        # index
        indices[[k]] = c(x.start, x.end, y.start, y.end)
        k = k + 1
    }
}

# parallel processing
parResults = parLapply(cl, indices, executeSerial)
results    = combineResults(parResults)

# stop cluster
stopCluster(cl)
