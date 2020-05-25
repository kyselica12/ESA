createHist = function(X, breaks, xlab='', ylab='Probability', main=''){
    # main histogram
    hist(X, breaks=breaks, prob=T, xlab=xlab, main=main)
    # blue density line
    points(density(X), type="l", col="blue")
    # red normal distribution
    m = mean(X); std = sqrt(var(X))
    curve(dnorm(x, mean=m, sd=std), col="red", lwd=2, add=TRUE)
    # red bottom lines
    rug(X, col="red")
    # legend
    legend('topright', col=c('blue','red'), lty=1, lwd=2, legend=c('density', 'normal'))
}

iterHist = function(DATABASE){
    tc = tryCatch({
        par(mfrow=c(2,2))
        createHist(DATABASE[,3],  breaks=50, main='SNR')
              hist(DATABASE[,4],  breaks=50, main='iter', xlab='', probability=T)
        createHist(DATABASE[,9],  breaks=50, main='skew')
        createHist(DATABASE[,10], breaks=50, main='kurt')
        par(mfrow=c(1,1))
        }, warning=function(w) {
        }, error=function(w) {
            message('Iterations histogram error!')
        }
    )
}

modelHist = function(DATABASE, model, matched){
    # stop if no model
    if(is.null(model)){
        return(list(
            'X' = NULL,
            'Y' = NULL
        ))
    }
    # else
    tc = tryCatch({
        par(mfrow=c(2,2))
        X = DATABASE[matched[,1],1] - model[matched[,2], 1]
        createHist(X, breaks=20, main=paste('X axis differences', round(mean(X), 4)), xlab='X difference')
        
        Y = DATABASE[matched[,1],2] - model[matched[,2], 2]
        createHist(Y, breaks=20, main=paste('Y axis differences', round(mean(Y), 4)), xlab='Y difference')
        
        E = sqrt(X**2 + Y**2)
        createHist(E, breaks=20, main='Euclidean distances', xlab='Distances')
        createHist(log(E), breaks=20, main='Log Euclidean distances', xlab='Log distances')
        }, warning=function(w) {
        }, error  =function(w) {
            message('Model histogram error!')
        }
    )
    return(list(
        'X' = X,
        'Y' = Y,
        'E' = E
    ))
}

errorScat = function(X,Y){
    if(is.null(X)){
        return()
    }
    tc = tryCatch({
        par(mfrow=c(1,1))
        dataEllipse(X,Y,
                    levels=c(0.95), robust=TRUE,
                    main='Error points', xlab='X', ylab='Y', ellipse.label='95%',
                    grid=FALSE)
        abline(h=0, lty=3)
        abline(v=0, lty=3)
        abline(h=mean(Y), lty=2, col='red')
        abline(v=mean(X), lty=2, col='red')
        # linear model
        #fit = mblm(Y~X)
        #abline(fit, col='red', lty=2, lwd=2)
        }, warning=function(w) { 
        }, error  =function(w) {
            message('Error scatter plot error!')
        }
    )
}

briScat = function(DATABASE, model, matched){
    # stop if no model
    if(is.null(model)){
        return()
    }
    # else
    tc = tryCatch({
        m = lm(model[matched[,2], 3] ~ DATABASE[matched[,1],5])
        par(mfrow=c(1,1))
        plot(DATABASE[matched[,1],5], model[matched[,2], 3], main='Total brightness', xlab='SCA', ylab='Model')
        legend('bottomright', legend=paste('model = ', round(m$coefficients[2], 4), '*SCA + ', round(m$coefficients[1], 4)), lwd=2, col='red')
        abline(m, col='red', lwd=2)
        }, warning=function(w) { 
        }, error  =function(w) {
            message('Brightness scatter plot error!')
        }
    )
}

parseCat = function(input){
    X = c()
    Y = c()
    F = c()
    alldata = readLines(input)
    for(i in 4:length(alldata)){
        l = gsub("^ *|(?<= ) | *$", "", alldata[i], perl = TRUE)
        p = strsplit(l, ' ')[[1]]
        if(length(p) != 17){
            next
        }
        X = c(X, as.numeric(p[12]))
        Y = c(Y, as.numeric(p[13]))
        F = c(F, as.numeric(p[14]))
    }
    
    return(cbind(X, Y, F))
}

getFileNameExtension = function (fn) {
    # remove a path
    splitted    <- strsplit(x=fn, split='/')[[1]]
    # or use .Platform$file.sep in stead of '/'
    fn          <- splitted [length(splitted)]
    ext         <- ''
    splitted    <- strsplit(x=fn, split='\\.')[[1]]
    l           <-length (splitted)
    if (l > 1 && sum(splitted[1:(l-1)] != ''))  ext <-splitted [l]
    # the extention must be the suffix of a non-empty name
    ext
}

rms = function(X){
    sqrt(sum(X**2)/length(X))
}
