import numpy as np
from math import floor, ceil


def get_pixels(cent_x, cent_y, A, B, alpha, image):
    
    # function extracts pixels from the box centred at CENT with length 2*A a width 2*B
    
    # CENT.X  : centre of the box
    # CENT.Y  : centre of the box
    # A,B     : size of the box
    # ALPHA   : angle between box axis A and axis X (-pi/2 .. pi/2)
    # IMAGE   : pixels
    
    # basic vectors of the box
    nrow , ncol = image.shape[:2]

    vecR = np.array([cent_x, cent_y])
    vecA = np.array([A*np.cos(alpha), A*np.sin(alpha)])
    vecB = np.array([B*np.cos(alpha + np.pi/2), B*np.sin(alpha + np.pi/2)])

    #four corners of the box
    TL = vecR - vecA + vecB
    TR = vecR + vecA + vecB
    BL = vecR - vecA + vecB
    BR = vecR + vecA + vecB

    #define four bounding lines
    if abs(np.tan(alpha)) > 0:
        tgA = np.tan(alpha)
        tgA2 = np.tan(alpha + np.pi/2)
        L1 = np.array([tgA,  -1, TR[1] - tgA *TR[0]])
        L2 = np.array([tgA,  -1, BL[1] - tgA *BL[0]])
        L3 = np.array([tgA2, -1, BL[1] - tgA2*BL[0]])
        L4 = np.array([tgA2, -1, TR[1] - tgA2*TR[0]])
    else:
        L1 = np.array([0, 1, -TR[1]])
        L2 = np.array([0, 1, -BL[1]])
        L3 = np.array([1, 0, -BL[0]])
        L4 = np.array([1, 0, -TR[0]])

    # define box pixel borders (four lines perpendicular to axes and passing through box four corners)
    box_top = floor(np.max(TL[1], TR[1], BL[1] ,BR[1]))   # first horizontal line from the top to cut the box
    box_bot = ceil(np.min(TL[1], TR[1], BL[1] ,BR[1]))   # first horizontal line from the bottom to cut the box 
    box_lef = ceil(np.min(TL[0], TR[0], BL[0] ,BR[0]))  # this is not used
    box_rig = floor(np.max(TL[0], TR[0], BL[0] ,BR[0])) # this is not used
    

    isect = lambda a,b,c: (c-b)/a

    y = np.min(box_top, nrow - 1)

    X_pixels, Y_pixels, Z_pixels = [], [], []

    if y < 0:
        return X_pixels, Y_pixels, Z_pixels

    line_top = y-1
    line_bot = y-1

    # intersect with all four lines
    if abs(np.tan(alpha)) > 0:
        x1_top = isect(L1[0], L1[2], line_top)
        x2_top = isect(L2[0], L2[2], line_top)
        x3_top = isect(L3[0], L3[2], line_top)
        x4_top = isect(L4[0], L4[2], line_top)
    else:
        x1_top = - np.inf
        x2_top = np.inf
        x3_top = BL[0]
        x4_top = TR[0]

    # for the first line, top == bot
    x1_bot = x1_top
    x2_bot = x2_top
    x3_bot = x3_top
    x4_bot = x4_top

     # remove min and max
    x_top  = sorted([x1_top, x2_top, x3_top, x4_top])[1:-1]
    x_bot  = sorted([x1_bot, x2_bot, x3_bot, x4_bot])[1:-1]
    
    # align with pixels
    x_sort = np.ceil(sorted([x_top, x_bot]))
    x_lef  = x_sort[0][0]
    x_rig  = x_sort[1][3]

    if x_lef < 0 and x_rig < 0:
        return X_pixels, Y_pixels, Z_pixels
    
    if x_lef > ncol and x_rig > ncol:
        return X_pixels, Y_pixels, Z_pixels
     
    x_lef = 0 if x_lef < 0 else x_lef
    x_lef = ncol if x_lef > ncol else x_lef
        

    x_rig = 0 if x_rig < 0 else x_rig
    x_rig = ncol if x_rig > ncol else x_rig

    X_pixels = [x  for x in range(x_lef, x_rig+1)]
    Y_pixels = [y for _ in range(x_rig - x_lef + 1) ]
    Z_pixels = image[y, x_lef:x_rig+1]

    beg = y

    if y == 0:
        return X_pixels, Y_pixels, Z_pixels


    # INTERMEDIATE PIXELS
    
    if box_bot > nrow:
        return X_pixels, Y_pixels, Z_pixels

    # cycle through pixels from top to bottom
    start = max(max(box_bot,0), beg)
    end = min(max(box_bot,0), beg)-1

    for y in range(start, end, -1):
        # for each y we need to determine the left and right border
        # intersections from previous round
        x_top = x_bot
        
        # pixel line
        
        line_top = line_bot
        line_bot = line_top - 1
        
        # do only intersection with bottom line
        if abs(np.tan(alpha)) > 0:
            x1_bot = isect(L1[0], L1[2], line_bot)
            x2_bot = isect(L2[0], L2[2], line_bot)
            x3_bot = isect(L3[0], L3[2], line_bot)
            x4_bot = isect(L4[0], L4[2], line_bot)
        else:
            x1_bot = -np.inf
            x2_bot = np.inf
            x3_bot = BL[0]
            x4_bot = TR[0]
        
        
        # remove min and max
        x_bot  = sorted([x1_bot, x2_bot, x3_bot, x4_bot])[1:-1]
        
        # align with pixels
        x_sort = np.ceil(sorted([x_top, x_bot]))
        x_lef  = x_sort[0][0]
        x_rig  = x_sort[1][3]
        
        x_lef = 0 if x_lef < 0 else x_lef
        x_lef = ncol if x_lef > ncol else x_lef
            

        x_rig = 0 if x_rig < 0 else x_rig
        x_rig = ncol if x_rig > ncol else x_rig

        X_pixels += [x for x in range(x_lef, x_rig+1)]
        Y_pixels += [y for _ in range(x_rig - x_lef + 1) ]
        Z_pixels += image[y, x_lef:x_rig+1]
    

    # LAST LINE OF PIXELS
    
    if y != 0: 
        y = box_bot
        # for each y we need to determine the left and right border
        # intersections from previous round
        x_top = x_bot
        
        # align with pixels
        x_sort = np.ceil(sorted([x_top, x_bot]))
    
        x_lef = x_sort[0][0]

        x_lef = 0 if x_lef < 0 else x_lef
        x_lef = ncol if x_lef > ncol else x_lef

        x_rig  = x_sort[1][1]

        x_rig = 0 if x_rig < 0 else x_rig
        x_rig = ncol if x_rig > ncol else x_rig
        
        X_pixels += [x for x in range(x_lef, x_rig+1)]
        Y_pixels += [y for _ in range(x_rig - x_lef + 1) ]
        Z_pixels += image[y, x_lef:x_rig+1]

    
    return X_pixels, Y_pixels, Z_pixels
