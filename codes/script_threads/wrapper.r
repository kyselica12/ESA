centroidSimpleWrapper = function(IMAGE, INIT.X, INIT.Y, A, B, NOISE.DIM, ALPHA, LOCALNOISE, DELTA, PIXLIM, PIXPROP, MAXITER, MINITER, SNRLIM, FINEITER, ISPOINT){
    
    DATA = getPixels(INIT.X, INIT.Y, A, B, ALPHA, IMAGE)

    # check the content of the rectangle
    if((sum(is.null(DATA$PXLS_Z))>0) | (sum(is.na(DATA$PXLS_Z))>0)){ # return
        return(list(
            'result' = c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = matrix(0,nrow=0,ncol=10),
            'message'= 'Null DATA.',
            'code'   = 1
            ))
    }
    
    if(length(DATA$PXLS_Z) < 4){ # return
        return(list(
            'result' = c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = matrix(0,nrow=0,ncol=10),
            'message'= 'Not enough DATA.',
            'code'   = 2
            ))
    }
    

    # check brightest pixel
    if(max(DATA$PXLS_Z) < PIXLIM){ # return
        return(list(
            'result' = c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = matrix(0,nrow=0,ncol=10),
            'message'= 'No pixel bright enough.',
            'code'   = 3
            ))
    }
    
    # find gravity centre
    C.X   = INIT.X
    C.Y   = INIT.Y
    ITER  = 1
    
    # log iterations
    LOG = matrix(c(C.X, C.Y, 0, 0, 0, 0, 0, 0, 0, 0, 0),nrow=1,ncol=11)
    
    while(TRUE){
        # current gravity centre
        current = findGravityCentre(C.X, C.Y, A, B, ALPHA, IMAGE, PIXPROP)
        
        if(length(current$CENT) == 0){ # return
            return(list(
                'result' = c(C.X, C.Y, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                'noise'  = -1,
                'log'    = LOG,
                'message'= 'Could not find gravity centre.',
                'code'   = 4
                ))
        }
        
        # log attempt
        mu = mean(current$PXLS_Z)
        v  =  var(current$PXLS_Z)
        s  = sqrt(v)
        sk = mean(((current$PXLS_Z - mu)/s)**3)
        ku = mean(((current$PXLS_Z - mu)/s)**4)
        
        LOG = rbind(LOG, c(current$CENT[1], current$CENT[2], 0, ITER, sum(current$PXLS_Z), mu, v, s, sk, ku))
        
        # position
        D.X  = C.X - current$CENT[1]
        D.Y  = C.Y - current$CENT[2]
        
        # distance from previous centre
        D    = sqrt(D.X**2 + D.Y**2)
        
        # if too close or too many iterations, exit loop
        if((D < DELTA) | (ITER > MAXITER)){
            break
        }
        
        # new centre position
        C.X = current$CENT[1]
        C.Y = current$CENT[2]
        
        # count iteration
        ITER = ITER + 1
    }

    # stop if did not finish iteration in time
    if(ITER > MAXITER){ # return
        return(list(
            'result' = c(current$CENT[1], current$CENT[1], 0, ITER, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = LOG,
            'message'= 'Maximum number of iterations reached.',
            'code'   = 5
            ))
    }
    
    
    # stop is finished too quickly
    if(ITER < MINITER){ # return
        return(list(
            'result' = c(current$CENT[1], current$CENT[1], 0, ITER, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = LOG,
            'message'= 'Not enough iterations.',
            'code'   = 6
            ))
    }
    
    
    gravSimple = current            # full results from final iteration
    CENT.X     = gravSimple$CENT[1] # final centre
    CENT.Y     = gravSimple$CENT[2]
    
    # noise
    
    multisetDiff = function(S,T){
        # N = S - T
        S = sort(S)
        T = sort(T)
        N = c()
        i = 1
        j = 1
        while(i <= length(S)){
            # end of T
            if(j > length(T)){
                break
            }
            # s_i smaller than t_j -> add s_i to N
            if(S[i] < T[j]){
                N = c(N, S[i])
                i = i + 1
                next
            }
            # s_i == t_j -> skip s_i and t_j, move to next t_j (this is the difference)
            if(S[i] == T[j]){
                i = i + 1
                j = j + 1
                next
            }
            # s_i larger than t_j, skip t_j
            j = j + 1
        }
        # append rest of the elements of S
        if(i <= length(S)) N = c(N, S[i:length(S)])
        # done
        return(N)
    }
    
    findBackground = function(){
        
        if(LOCALNOISE == 0){
            return(0)
        }
        
        if(LOCALNOISE > 1){
            return(LOCALNOISE)
        }
        
        largeNoiseRect = getPixels(CENT.X, CENT.Y, A + 2*NOISE.DIM, B + 2*NOISE.DIM, ALPHA, IMAGE)$PXLS_Z
        largeNoiseRect = largeNoiseRect[!is.na(largeNoiseRect)]
        
        smallNoiseRect = getPixels(CENT.X, CENT.Y, A +   NOISE.DIM, B +   NOISE.DIM, ALPHA, IMAGE)$PXLS_Z
        smallNoiseRect = smallNoiseRect[!is.na(smallNoiseRect)]
        
        inBetweenFrame = multisetDiff(largeNoiseRect, smallNoiseRect)
        
        localNoiseMedian = median(inBetweenFrame)
        
        return(localNoiseMedian)
    }
    
    removeNegative = function(v, val=10){
        v[v<0] = val
        return(v)
    }
    
    
    BACKGROUND = findBackground()
    
    # fine centroiding with local noise removed
    if(FINEITER > 0 & LOCALNOISE != 0){
        for(i in 1:FINEITER){
            current = findGravityCentre(gravSimple$CENT[1], gravSimple$CENT[2], A, B, ALPHA, IMAGE, PIXPROP, BACKGROUND)
        }
        gravSimple = current            # full results from final iteration
        CENT.X     = gravSimple$CENT[1] # final centre
        CENT.Y     = gravSimple$CENT[2]
    }
    
    
    # remove local background from local pixels (for calculation of statistics, IMAGE is not changed)
    gravSimple$PXLS_Z = removeNegative(gravSimple$PXLS_Z - BACKGROUND)
    
    # OLD defintion
    # SIGNAL = mean(removeNegative(gravSimple$PXLS_Z - BACKGROUND))
    # NOISE  = mean(removeNegative(inBetweenFrame    - BACKGROUND))
    
    # Definition for 1 pixel SNR (peak SNR) from Raab (2001) - Detecting and measuring faint point sources with a CCD, eq. 5
    SIGNAL = max(gravSimple$PXLS_Z)
    NOISE  = sqrt(SIGNAL + BACKGROUND)
    SNR    = SIGNAL / NOISE
    
    # Print out values for cross-check
    #cat("gravSimple:    ", gravSimple$PXLS_Z, " ")
    #cat("BACKGROUND:    ", BACKGROUND, " ")
    #cat("SIGNAL:        ", SIGNAL, " ")
    #cat("NOISE:        ", NOISE, " ")
    #cat("SNR:            ", SNR, " \n")
    
    if(SNR < SNRLIM){ # return
        return(list(
            'result' = c(CENT.X, CENT.Y, SNR, ITER, sum(gravSimple$PXLS_Z), 0, 0, 0, 0, 0, 0),
            'noise'  = BACKGROUND,
            'log'    = LOG,
            'message'= 'Low signal-to-noise value.',
            'code'   = 7
            ))
    }

    # stop if centre not right
    maxpix.v = max(current$PXLS_Z)
    maxpix.i = which.max(current$PXLS_Z)
    maxpix.x = current$PXLS_X[maxpix.i]
    maxpix.y = current$PXLS_Y[maxpix.i]
    maxpix.d = sqrt((maxpix.x - current$CENT[1])**2 + (maxpix.y - current$CENT[2])**2)
    
    if(ISPOINT & (maxpix.d > min(A,B)/2)){ # return
        return(list(
            'result' = c(current$CENT[1], current$CENT[1], 0, ITER, 0, 0, 0, 0, 0, 0, 0),
            'noise'  = -1,
            'log'    = LOG,
            'message'= 'Centre not right.',
            'code'   = 8
            ))
    }
    
    # moments
    mu = mean(gravSimple$PXLS_Z)
    v  =  var(gravSimple$PXLS_Z)
    s  = sqrt(v)
    # skewness
    sk = mean(((gravSimple$PXLS_Z - mu)/s)**3)
    # kurtosis
    ku = mean(((gravSimple$PXLS_Z - mu)/s)**4)

    if(FINEITER > 0 & LOCALNOISE != 0){
        LOG = rbind(LOG, c(current$CENT[1], current$CENT[2], 0, ITER, sum(current$PXLS_Z), mu, v, s, sk, ku))
    }
    
    return(list(
        'result' = c(CENT.X, CENT.Y, SNR, ITER, sum(gravSimple$PXLS_Z), mu, v, s, sk, ku, BACKGROUND),
        'noise'  = BACKGROUND,
        'log'    = LOG,
        'message'= 'OK',
        'code'   = 0
        ))
  
}
