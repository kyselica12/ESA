# print("Tests!!!")

# print("TEST 1")
# print(ALG_PARS$CENTRE_LIMIT)
# print("TEST 2")

# single step function
performStep = function(x,y,out){
    # x,y -- where to iterate,
    # out -- if there should be output
    started <<- started + 1

    # this has to be set for the "return from function" part
    UD = list('code' = 0)

    if (x==355){
        if (y==79){
            print("debug")
        }
    }

    current =  centroidSimpleWrapper(
                IMAGE      = IMAGE,
                INIT.X     = x,
                INIT.Y     = y,
                A          = opt$width,
                B          = opt$height,
                NOISE.DIM  = opt$`noise-dim`,
                ALPHA      = opt$angle*pi/180,
                LOCALNOISE = opt$`local-noise`,
                DELTA      = opt$delta,
                PIXLIM     = opt$`start-iter`,
                PIXPROP    = opt$`cent-pix-perc`,
                MAXITER    = opt$`max-iter`,
                MINITER    = opt$`min-iter`,
                SNRLIM     = opt$`snr-lim`,
                FINEITER   = opt$`fine-iter`,
                ISPOINT    = opt$width == opt$height
                )
	
    if(current$code == 0){
        ok <<- ok + 1
        # update database if necessary
        UD = updateDatabase(DATABASE, current$result, ALG_PARS$CENTRE_LIMIT)

        DATABASE <<- UD$DATABASE
        # discarded cases
        if(UD$code == 1){
            DISCARDED <<- rbind(DISCARDED, current$result)
        }else{
            if(opt$verbose == 1 & opt$parallel == 1){
                # print iteration log for successfull runs
                cat(x); cat(', '); cat(y); cat('\n')
                for(i in 1:nrow(current$log)) {
                    for(j in 1:ncol(current$log)){
                        cat(sprintf("%.6f", current$log[i,j]))
                        cat('\t')
                    }
                    cat('\n')
                }
                cat('\n')
            }
        }
    }else if(current$code == 1){ nulldata  <<- nulldata  + 1
    }else if(current$code == 2){ notenough <<- notenough + 1
    }else if(current$code == 3){ notbright <<- notbright + 1
    }else if(current$code == 4){ nocentre  <<- nocentre  + 1
    }else if(current$code == 5){ maxiter   <<- maxiter   + 1
    }else if(current$code == 6){ miniter   <<- miniter   + 1
    }else if(current$code == 7){ lowsnr    <<- lowsnr    + 1
    }else if(current$code == 8){ notright  <<- notright  + 1
    }
    
    
    # return from function
    if(out){
        # return code and position for method max
        if(current$code == 0 & UD$code != 1){
            return(list(
                'code' = 0,
                'x'    = current$result[1],
                'y'    = current$result[2]
            ))
        }else{
            return(list(
                'code' = 1
            ))
        }
    }else{
        # no return for methods sweep and cluster
        return()
    }
}
# performStep() function updates
#   DATABASE
#   DISCARDED
#   __stat_vars__
#
# these variables come from executeSerial() serial function, so they should be visible for performStep(),
# but they will disappear when executeSerial() functions ends.
# this is important for multiple calls of executeSerial() function in parallel processing
#
# also, the performStep() function should see x.{start,end}, y.{start,end} mentioned below
#
#
# executeSerial() sees IMAGE
# executeSerial() gets what part of the image should be processed in x.{start,end}, y.{start,end}
#
# for single thread, these will be
#   x.start = 1
#   x.end   = fitsDimX
#   y.start = 1
#   y.end   = fitsDimY
#
# the variables are used in sweep/max/serial parts

executeSerial = function(index){

    # which part of the IMAGE to process
    x.start = index[1]
    x.end   = index[2]
    y.start = index[3]
    y.end   = index[4]
    
    # run statistics (__stat_vars__)
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
    
    # reset database
    DATABASE  = matrix(0, nrow=0, ncol=11)
    DISCARDED = matrix(0, nrow=0, ncol=11)
    
    colnames(DATABASE)  = c('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
    colnames(DISCARDED) = c('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
    
    # box dimension
    A = opt$width
    B = opt$height
    
    # sweep through the image
    if(opt$method == 'sweep'){
        # iteration points
        Xs = floor(seq(x.start + A, x.end - A, by=2*A))
        Ys = floor(seq(y.start + B, y.end - B, by=2*B))
        for(y in Ys){
            for(x in Xs){
                environment(performStep) = environment()
                performStep(x, y, FALSE)
            }
        }
    }
    
    # find brightest points
    if(opt$method == 'max'){
        pixels = which(IMAGE > opt$`start-iter`, arr.ind = T)

        # iteration points
        Xs = pixels[,2]
        Ys = pixels[,1]

        # keep only those in range x.{start,end}, y.{start,end}
        good = (x.start < Xs) & (Xs < x.end) & (y.start < Ys) & (Ys < y.end)
        Xs = Xs[good]
        Ys = Ys[good]

        # go through all items
        while(length(Xs) > 0){
            environment(performStep) = environment()
            STEP = performStep(Xs[1], Ys[1], TRUE)
            # remove analyzed pixel
            Xs = Xs[-1]
            Ys = Ys[-1]
            # remove close pixels
            if(STEP$code == 0){
                filt_x = (Xs >= (STEP$x - A)) & (Xs <= (STEP$x + A))
                filt_y = (Ys >= (STEP$y - B)) & (Ys <= (STEP$y + B))
                Xs = Xs[!(filt_x & filt_y)]
                Ys = Ys[!(filt_x & filt_y)]
            }
        }
    }
    
    # cluster analysis
    #if(opt$method == 'clusters'){
    #    pixels = which(IMAGE > opt$`start-iter`, arr.ind = T)
    #
    #    Xs = pixels[,2]
    #    Ys = pixels[,1]
    #
    #    # keep only those in range x.{start,end}, y.{start,end}
    #    good = (x.start < Xs) & (Xs < x.end) & (y.start < Ys) & (Ys < y.end)
    #
    #    pixels = as.data.frame(pixels[good,])
    #
    #    # python clustering
    #    python.assign("pixels", pixels)
    #    python.assign("thresh", sqrt(A**2 + B**2) )
    #    python.load("script_threads/python_clustering.py")
    #    clusters = python.get("clusters")
    #
    #    pixels = cbind(pixels, clusters)
    #    pixels = pixels[order(pixels$clusters),]
    #
    #    for(i in 1:max(clusters)){
    #        # get cluster
    #        XY = pixels[pixels$clusters == i,]
    #        X  = XY[,2]
    #        Y  = XY[,1]
    #        Z  = c()
    #        for(j in 1:nrow(XY)) Z = c(Z, IMAGE[Y[j], X[j]])
    #        # centre of the cluster
    #        sumG  = sum(Z)
    #        sumGx = sum(Z*(X - 0.5))
    #        sumGy = sum(Z*(Y - 0.5))
    #        # centroiding
    #        environment(performStep) = environment()
    #        performStep(sumGx/sumG, sumGy/sumG, FALSE)
    #    }
    #
    #}
    #
    return(list(
        'DATABASE'  = DATABASE,
        'DISCARDED' = DISCARDED,
        'STATS'     = list(
            'started'   = started,
            'nulldata'  = nulldata,
            'notenough' = notenough,
            'notbright' = notbright,
            'nocentre'  = nocentre,
            'maxiter'   = maxiter,
            'miniter'   = miniter,
            'lowsnr'    = lowsnr,
            'ok'        = ok,
            'notright'  = notright
        )
    ))
}
