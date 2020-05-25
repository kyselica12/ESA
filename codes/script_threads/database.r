updateDatabase = function(DATABASE, current, THRS){
    # cycles through DATABASE (global)
    # finds all rows that are within THRS distance from the current (they themselves do not need be this close)
    # from all rows (including the current) we pick the one with best SNR
    
    # first entry
    if(nrow(DATABASE) == 0){
        return(list(
            'DATABASE' = rbind(DATABASE, current),
            'code'     = -1
        ))
    }
    
    # calculate distances
    dist = rep(0,nrow(DATABASE))
    for(i in 1:nrow(DATABASE)) dist[i] = sqrt((DATABASE[i,1] - current[1])**2 + (DATABASE[i,2] - current[2])**2)
        
    # pick close rows
    closeRows = dist < THRS
        
    # if no row found, append current
    if(sum(closeRows) == 0){
        return(list(
            'DATABASE' = rbind(DATABASE, current),
            'code'     = 0
        ))
    }
    
    # otherwise, select the best SNR
    D    = rbind(DATABASE[closeRows,], current)
    id   = which.max(D[,4])
    best = D[id,]
    #print(D)
    # remove goodRows and append the best
    return(list(
        'DATABASE' = rbind(DATABASE[!closeRows, ], best),
        'code'     = 1
    ))
}