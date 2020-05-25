findGravityCentre = function(CENT.X, CENT.Y, A, B, ALPHA, IMAGE, PIXPROP, BCKG=0){
    
    # function find gravity centre of the pixels from the box centred at CENT with length 2*A a width 2*B
    
    # CENT.X  : centre of the box
    # CENT.Y  : centre of the box
    # A       : size of the boxes
    # B       : size of the boxes
    # ANGLE   : angle between box axis A and axis X (-pi/2 .. pi/2)
    # IMAGE    : image (pixels)
    
    # extract data
    DATA = getPixels(CENT.X, CENT.Y, A, B, ALPHA, IMAGE)
    
    # if empty, exit
    if(length(DATA$PXLS_X) == 0) return(list('CENT' = c(), 'PXLS_X' = c(), 'PXLS_Y' = c(), 'PXLS_Z' = c()))
    
    # else return centre
    if(PIXPROP == 100){
        if(BCKG == 0){
            sumG  = sum(DATA$PXLS_Z)
            sumGx = sum(DATA$PXLS_Z*(DATA$PXLS_X - 0.5))
            sumGy = sum(DATA$PXLS_Z*(DATA$PXLS_Y - 0.5))
        }else{
            # this is to avoid unnecessary subtractions when BCKG == 0
            DATA_Z = DATA$PXLS_Z - BCKG
            sumG  = sum(DATA_Z)
            sumGx = sum(DATA_Z*(DATA$PXLS_X - 0.5))
            sumGy = sum(DATA_Z*(DATA$PXLS_Y - 0.5))
        }
    }else{
        # centroiding from PIXPROP pixels
        tmp = cbind(DATA$PXLS_Z, DATA$PXLS_X, DATA$PXLS_Y)
        tmp = tmp[order(tmp[,1], decreasing=TRUE), ]
        tmp = tmp[1:floor(nrow(tmp)*PIXPROP/100),]
        
        if(BCKG == 0){
            Z = tmp[,1]
        }else{
            Z = tmp[,1] - BCKG
        }
        X = tmp[,2]
        Y = tmp[,3]
        
        sumG  = sum(Z)
        sumGx = sum(Z*(X - 0.5))
        sumGy = sum(Z*(Y - 0.5))
    }
    
    return(list(
        'CENT' = c(sumGx/sumG, sumGy/sumG),
        'PXLS_X' = DATA$PXLS_X,
        'PXLS_Y' = DATA$PXLS_Y,
        'PXLS_Z' = DATA$PXLS_Z
        ))
}
