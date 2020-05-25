getPixels = function(CENT.X, CENT.Y, A, B, ALPHA, IMAGE){

    # function extracts pixels from the box centred at CENT with length 2*A a width 2*B
    
    # CENT.X  : centre of the box
    # CENT.Y  : centre of the box
    # A,B     : size of the box
    # ALPHA   : angle between box axis A and axis X (-pi/2 .. pi/2)
    # IMAGE   : pixels
    
    # basic vectors of the box
   
    vecR = c(CENT.X, CENT.Y)
    vecA = c(A*cos(ALPHA), A*sin(ALPHA))
    vecB = c(B*cos(ALPHA+pi/2), B*sin(ALPHA+pi/2))    
      
    # four corners of the box
    TL = vecR - vecA + vecB
    TR = vecR + vecA + vecB
    BL = vecR - vecA - vecB
    BR = vecR + vecA - vecB
    
    # define four bounding lines
    if(abs(tan(ALPHA)) > 0){
        tgA  = tan(ALPHA)
        tgA2 = tan(ALPHA + pi/2)
        L1 = c(tgA,  -1, TR[2] - tgA *TR[1])
        L2 = c(tgA,  -1, BL[2] - tgA *BL[1])
        L3 = c(tgA2, -1, BL[2] - tgA2*BL[1])
        L4 = c(tgA2, -1, TR[2] - tgA2*TR[1])
    }else{
        L1 = c(0, 1, -TR[2])
        L2 = c(0, 1, -BL[2])
        L3 = c(1, 0, -BL[1])
        L4 = c(1, 0, -TR[1])
    }
    
    
    # define box pixel borders (four lines perpendicular to axes and passing through box four corners)
    box.top = floor  (max(TL[2], TR[2], BL[2] ,BR[2]))   # first horizontal line from the top to cut the box
    box.bot = ceiling(min(TL[2], TR[2], BL[2] ,BR[2]))   # first horizontal line from the bottom to cut the box 
    box.lef = ceiling(min(TL[1], TR[1], BL[1] ,BR[1]))
    box.rig = floor  (max(TL[1], TR[1], BL[1] ,BR[1]))
    
    PIXELS_X = c()
    PIXELS_Y = c()
    PIXELS_Z = c()
    
    # line : y = ax + b
    # intersect with y = c
    isect = function(aa,bb,cc) (cc - bb)/aa
    
    # FOR FIRST LINE OF PIXELS
    
    y = min(box.top + 1, nrow(IMAGE))
    if(y <= 0) return(list('PXLS_X' = c(), 'PXLS_Y' = c(), 'PXLS_Z' = c()))
    # EXIT
    
    # horizontal lines cutting the box one pixel apart (for the topmost part of the box, the lines are equal -- the corner of the box is inside of some pixel)
    # box.top is the topmost horizontal line cutting the box
    line.top = y - 1
    line.bot = y - 1
    
    # intersect with all four lines
    if(abs(tan(ALPHA)) > 0){
        x1.top = isect(L1[1], L1[3], line.top)
        x2.top = isect(L2[1], L2[3], line.top)
        x3.top = isect(L3[1], L3[3], line.top)
        x4.top = isect(L4[1], L4[3], line.top)
    }else{
        x1.top = -Inf
        x2.top = Inf
        x3.top = BL[1]
        x4.top = TR[1]
    }
    
    # for the first line, top == bot
    x1.bot = x1.top
    x2.bot = x2.top
    x3.bot = x3.top
    x4.bot = x4.top
    
    # remove min and max
    x.top  = sort(c(x1.top, x2.top, x3.top, x4.top))[-c(1,4)]
    x.bot  = sort(c(x1.bot, x2.bot, x3.bot, x4.bot))[-c(1,4)]
    
    # align with pixels
    x.sort = ceiling(sort(c(x.top, x.bot)))
    x.lef  = x.sort[1]
    x.rig  = x.sort[4]
        
    if(x.lef <= 0 & x.rig <= 0) return(list('PXLS_X' = c(), 'PXLS_Y' = c(), 'PXLS_Z' = c()))
    # EXIT
    
    if(x.lef > ncol(IMAGE) & x.rig > ncol(IMAGE)) return(list('PXLS_X' = c(), 'PXLS_Y' = c(), 'PXLS_Z' = c()))
    # EXIT
    
    if(x.lef <= 0)           x.lef = 1
    if(x.lef > ncol(IMAGE))  x.lef = ncol(IMAGE)
    
    if(x.rig <= 0)           x.rig = 1
    if(x.rig > ncol(IMAGE))  x.rig = ncol(IMAGE)
        
    PIXELS_X = c(PIXELS_X, x.lef:x.rig)	
    PIXELS_Y = c(PIXELS_Y, rep(y, x.rig - x.lef + 1))	
    PIXELS_Z = c(PIXELS_Z, IMAGE[y,x.lef:x.rig])
    
    BEG = y
        
    if(y == 1) return(list(
        'PXLS_X' = PIXELS_X,
        'PXLS_Y' = PIXELS_Y,
        'PXLS_Z' = PIXELS_Z
        ))
    
    # INTERMEDIATE PIXELS
    
    if(box.bot+1 > nrow(IMAGE)) return(list(
        'PXLS_X' = PIXELS_X,
        'PXLS_Y' = PIXELS_Y,
        'PXLS_Z' = PIXELS_Z
        ))
        
    # cycle through pixels from top to bottom
    for(y in (BEG-1):max((box.bot+1), 1)){
        # for each y we need to determine the left and right border
        # intersections from previous round
        x.top = x.bot
        
        # pixel line
        line.top = line.bot
        line.bot = line.top - 1
        
        # do only intersection with bottom line
        if(abs(tan(ALPHA)) > 0){
            x1.bot = isect(L1[1], L1[3], line.bot)
            x2.bot = isect(L2[1], L2[3], line.bot)
            x3.bot = isect(L3[1], L3[3], line.bot)
            x4.bot = isect(L4[1], L4[3], line.bot)
        }else{
            x1.bot = -Inf
            x2.bot = Inf
            x3.bot = BL[1]
            x4.bot = TR[1]
        }
        
        # remove min and max
        x.bot  = sort(c(x1.bot, x2.bot, x3.bot, x4.bot))[-c(1,4)]
        
        # align with pixels
        x.sort = ceiling(sort(c(x.top, x.bot)))
        x.lef  = x.sort[1]
        x.rig  = x.sort[4]

        if(x.lef <= 0)          x.lef = 1
        if(x.lef > ncol(IMAGE)) x.lef = ncol(IMAGE)

        if(x.rig <= 0)          x.rig = 1
        if(x.rig > ncol(IMAGE)) x.rig = ncol(IMAGE)
        
        PIXELS_X = c(PIXELS_X, x.lef:x.rig)
        PIXELS_Y = c(PIXELS_Y, rep(y, x.rig - x.lef + 1))
        PIXELS_Z = c(PIXELS_Z, IMAGE[y,x.lef:x.rig])
    }

    
    # LAST LINE OF PIXELS
    
    if(y != 1){
        y = box.bot
        # for each y we need to determine the left and right border
        # intersections from previous round
        x.top = x.bot
        
        # align with pixels
        x.sort = ceiling(sort(c(x.top, x.bot)))
    
        x.lef = x.sort[1]

        if(x.lef <= 0)          x.lef = 1
        if(x.lef > ncol(IMAGE)) x.lef = ncol(IMAGE)

        x.rig  = x.sort[4]

        if(x.rig <= 0)          x.rig = 1
        if(x.rig > ncol(IMAGE)) x.rig = ncol(IMAGE)
        
        PIXELS_X = c(PIXELS_X, x.lef:x.rig)
        PIXELS_Y = c(PIXELS_Y, rep(y, x.rig - x.lef + 1))
        PIXELS_Z = c(PIXELS_Z, IMAGE[y,x.lef:x.rig])

    }
    
    
    # DONE
    
    return(list(
        'PXLS_X' = PIXELS_X,
        'PXLS_Y' = PIXELS_Y,
        'PXLS_Z' = PIXELS_Z
        ))
}
