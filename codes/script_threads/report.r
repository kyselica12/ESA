drawPicture = function(DATABASE, params, model){
    
    # save fits as jpg to use as background
    jpeg('image.jpg', height=params$fitsDimY, width=params$fitsDimX, units="px")
    par(mar=c(0,0,0,0))
    par(mai=c(0,0,0,0))
    par(oma=c(0,0,0,0))
    par(omi=c(0,0,0,0))
    MAXB = quantile(IMAGE, probs=0.99)
    image(t(replace(IMAGE,IMAGE > MAXB, MAXB)), axes = FALSE, col = grey(seq(0, 1, length = 65535)), useRaster=F)
    #image(t(IMAGE), axes = FALSE, col = grey(seq(0, 1, length = 65535)), useRaster=F)
    invisible(dev.off())
    
    # load background
    img = readJPEG("image.jpg")
    # remove jpg
    invisible(file.remove('image.jpg'))

    # RESULT IMAGE
    df = data.frame(
    x    = DATABASE[,1],
    y    = DATABASE[,2],
    SNR  = DATABASE[,3],
    ITER = DATABASE[,4],
    SUM  = DATABASE[,5],
    MU   = DATABASE[,6],
    VAR  = DATABASE[,7],
    SD   = DATABASE[,8],
    SKEW = DATABASE[,9],
    KURT = DATABASE[,10],
    BCKG = DATABASE[,11]
    )
    
    if(!is.null(model)){
        dfm = data.frame(
            x = model[,1],
            y = model[,2]
        )
    }

    COL    = DATABASE[,params$color]
    TITLE  = c('SNR', 'SNR', 'SNR', 'ITER', 'SUM', 'MEAN', 'VAR', 'STD', 'SKEW', 'KURT', 'BCKG')
    TITLE  = TITLE[params$color]
    ALPHA  = params$angle*pi/180
#    vecA   = c(params$A*cos(params$ALPHA),      params$A*sin(params$ALPHA))        #modified J. Silha 20200116
#    vecB   = c(params$B*cos(params$ALPHA+pi/2), params$B*sin(params$ALPHA+pi/2))
    vecA   = c(params$A*cos(ALPHA),      params$A*sin(ALPHA))
    vecB   = c(params$B*cos(ALPHA+pi/2), params$B*sin(ALPHA+pi/2))

    plt = ggplot(df, aes(x, y)) + 
            #                                                                                               v    and     v   are global vars
            annotation_custom(rasterGrob(img, width=unit(1,"npc"), height=unit(1,"npc"), interpolate=F), 1, fitsDimX, 1, fitsDimY) + 
            scale_colour_gradientn(colours = heat.colors(128)) + 
            xlim(c(1,fitsDimX)) + 
            ylim(c(1,fitsDimY))

    # add shapes for model objects
    if(!is.null(model)){
        plt = plt + 
        # TR -> BR
        geom_segment( data = dfm, aes(x = model[,1] + vecA[1] + vecB[1], 
                                      y = model[,2] + vecA[2] + vecB[2], 
                                   xend = model[,1] + vecA[1] - vecB[1], 
                                   yend = model[,2] + vecA[2] - vecB[2]), 
                     color = 'grey', 
                      size = 0.1) +
        # BR -> BL
        geom_segment( data = dfm, aes(x = model[,1] + vecA[1] - vecB[1], 
                                      y = model[,2] + vecA[2] - vecB[2], 
                                   xend = model[,1] - vecA[1] - vecB[1], 
                                   yend = model[,2] - vecA[2] - vecB[2]), 
                     color = 'grey', 
                      size = 0.1) +
        # BL -> TL
        geom_segment( data = dfm, aes(x = model[,1] - vecA[1] - vecB[1], 
                                      y = model[,2] - vecA[2] - vecB[2], 
                                   xend = model[,1] - vecA[1] + vecB[1], 
                                   yend = model[,2] - vecA[2] + vecB[2]), 
                     color = 'grey', 
                      size = 0.1) +
        # TL -> TR
        geom_segment( data = dfm, aes(x = model[,1] - vecA[1] + vecB[1], 
                                      y = model[,2] - vecA[2] + vecB[2], 
                                   xend = model[,1] + vecA[1] + vecB[1], 
                                   yend = model[,2] + vecA[2] + vecB[2]), 
                     color = 'grey', 
                      size = 0.1)
    }

    # add shapes from found objects
    plt = plt + 
        # TR -> BR
        geom_segment( data =  df, aes(x = DATABASE[,1] + vecA[1] + vecB[1], 
                                      y = DATABASE[,2] + vecA[2] + vecB[2], 
                                   xend = DATABASE[,1] + vecA[1] - vecB[1], 
                                   yend = DATABASE[,2] + vecA[2] - vecB[2], 
                                 colour = COL), 
                  linetype = 'dashed', 
                      size = 0.1) +
        # BR -> BL
        geom_segment( data =  df, aes(x = DATABASE[,1] + vecA[1] - vecB[1], 
                                      y = DATABASE[,2] + vecA[2] - vecB[2], 
                                   xend = DATABASE[,1] - vecA[1] - vecB[1], 
                                   yend = DATABASE[,2] - vecA[2] - vecB[2], 
                                 colour = COL), 
                  linetype = 'dashed', 
                      size = 0.1) +
        # BL -> TL
        geom_segment( data =  df, aes(x = DATABASE[,1] - vecA[1] - vecB[1], 
                                      y = DATABASE[,2] - vecA[2] - vecB[2], 
                                   xend = DATABASE[,1] - vecA[1] + vecB[1], 
                                   yend = DATABASE[,2] - vecA[2] + vecB[2], 
                                 colour = COL), 
                  linetype = 'dashed', 
                      size = 0.1) +
        # TL -> TR
        geom_segment( data =  df, aes(x = DATABASE[,1] - vecA[1] + vecB[1], 
                                      y = DATABASE[,2] - vecA[2] + vecB[2], 
                                   xend = DATABASE[,1] + vecA[1] + vecB[1], 
                                   yend = DATABASE[,2] + vecA[2] + vecB[2], 
                                 colour = COL), 
                  linetype = 'dashed', 
                      size = 0.1) + 
        # legend title
        labs(color = TITLE)
    print(plt)

}

matchObjects = function(DATABASE, params){
        # parse catalogue
        if(getFileNameExtension(params$model) == 'cat'){
            model = parseCat(params$model)
        }else{
            model = as.matrix(read.table(params$model, sep='\t', header=F))
        }
        
        # euclidean distances (SCA x model)
        euclid = crossdist(DATABASE[,1], DATABASE[,2], model[,1], model[,2])
        
        mins  = apply(euclid,1,min)
        wmins = apply(euclid,1,which.min)
        
        # process matched stars (because SCA stars can be matched to same model stars)
        processed = c()                     # processed SCA stars
        used      = c()                     # used model stars
        matched   = matrix(0,nrow=0,ncol=2) # matched stars
        unmatched = matrix(0,nrow=0,ncol=2) # unmatched stars
        i = 1
        
        # model matching
        while(length(processed) != nrow(euclid)){
            
            # skip processed SCA stars
            if(i %in% processed){
                i = i + 1
                next
            }

            # skip unmatched SCA stars
            if(mins[i] > ALG_PARS$MATCH_LIMIT){
                unmatched = rbind(unmatched, c(i, mins[i]))
                # mark matched model star
                processed = c(processed, i)
                i = i + 1
                next
            }
            
            # take unmatched SCA star closest to model
            mmin = which.min(mins)

            # check if the model star is free
            if(wmins[mmin] %in% used){
                # is used:

                mins[mmin]  = min(euclid[mmin,])
                wmins[mmin] = which.min(euclid[mmin,])

            }else{
                # is free:

                # set a match
                matched = rbind(matched, c(mmin, wmins[mmin]))

                # mark matched model star
                used = c(used, wmins[mmin])
                euclid[,wmins[mmin]] = 1000

                # set SCA star as processed
                processed = c(processed, mmin)
                mins[mmin] = 1000
            }
        } # end while

    return(list(
        'model'     = model,
        'matched'   = matched,
        'unmatched' = unmatched
    ))
}

generateReport = function(DATABASE, IMAGE, params){

    # load functions
    source('script_threads/report_functions.r')
    
    # match found objects to catalogue
    if(!is.null(params$model)){
        mo = matchObjects(DATABASE, params)
        model     = mo$model
        matched   = mo$matched
        unmatched = mo$unmatched
    }else{
        model     = NULL
        matched   = matrix(0, nrow=0, ncol=0)
        unmatched = matrix(0, nrow=0, ncol=0)
    }
    
    # start writing report to file
    pdf(params$report)
    
    # MAIN PICTURE
    drawPicture(DATABASE, params, model)
    
    # HISTOGRAMS
          iterHist(DATABASE)
    XY = modelHist(DATABASE, model, matched)
    
    # SCATTER PLOTS
    errorScat(XY$X, XY$Y)
      briScat(DATABASE, model, matched)

    # done
    invisible(dev.off())
    
    if(is.null(XY$X)){
        XY$X = c(0)
        XY$Y = c(0)
    }
    
    return(list(
        'matched'   = matched,
        'unmatched' = unmatched,
        'model'     = model,
        'X'         = mean(XY$X),
        'Y'         = mean(XY$Y),
        'RMS.X'     = rms(XY$X),
        'RMS.Y'     = rms(XY$Y)
    ))
}
