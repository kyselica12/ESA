from getPixels import get_pixels
import numpy as np


def fing_gravity_centre(cent_x, cent_y, A, B, alpha, image, pix_prob, bckg=0):

    # function find gravity centre of the pixels from the box centred at CENT with length 2*A a width 2*B
    
    # CENT.X  : centre of the box
    # CENT.Y  : centre of the box
    # A       : size of the boxes
    # B       : size of the boxes
    # ANGLE   : angle between box axis A and axis X (-pi/2 .. pi/2)
    # IMAGE    : image (pixels)
    
    # extract data
    data_X, data_Y, data_Z = get_pixels(cent_x, cent_y, A, B, alpha, image)
    
    # if empty, exit
    if len(data_X) == 0:
        return None, None, None, None
    
    # else return centre

    if pix_prob == 100:
        if bckg != 0:
            # this is to avoid unnecessary subtractions when BCKG == 0
            data_Z = data_Z - bckg

        sum_G = np.sum(data_Z)
        sum_Gx = np.sum(data_Z * (data_X - 0.5))
        sum_Gy = np.sum(data_Z * (data_Y - 0.5))
    
    else:
        # centroiding from PIXPROP pixels
        tmp = np.concatenate([data_Z.reshape(-1,1),data_X.reshape(-1,1), data_Y.reshape(-1,1)], axis=1)
        tmp = tmp[tmp[:,0].argsort(kind='mergesort')]
        tmp = tmp[0: np.floor(tmp.shape[0] * pix_prob / 100)]

        z = tmp[:,0]
        if bckg != 0:
            z -= bckg
        
        x = tmp[:,1]
        y = tmp[:,2]

        sum_G = np.sum(z)
        sum_Gx = np.sum(z * (x - 0.5))
        sum_Gy = np.sum(z * (y - 0.5))

    return (sum_Gx/sum_G, sum_Gy/sum_G), data_X, data_Y, data_Z
    

