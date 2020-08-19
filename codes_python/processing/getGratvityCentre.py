from processing.getPixels import get_pixels
import numpy as np
from utils.structures import GravityCentreResult


def find_gravity_centre(cent_x, cent_y, A, B, alpha, image, pix_prop, bckg=0):

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
        return GravityCentreResult(None, None, None, None)
    # else return centre

    if pix_prop == 100:
        if bckg != 0:
            # this is to avoid unnecessary subtractions when BCKG == 0
            data_Z = data_Z - bckg

        sum_G = np.sum(data_Z)
        sum_Gx = np.sum(data_Z * (data_X - 0.5))
        sum_Gy = np.sum(data_Z * (data_Y - 0.5))
    
    else:
        # centroiding from PIXPROP pixels

        tmp = np.concatenate([data_Z.reshape(-1,1),data_X.reshape(-1,1), data_Y.reshape(-1,1)], axis=1)
        tmp = tmp[(-tmp[:, 0]).argsort(kind='mergesort')]
        threshold = np.floor(tmp.shape[0] * pix_prop / 100).astype(int)
        min_val = tmp[threshold, 0]
        # tmp = tmp[:threshold, :] # - for indexing from the end where are the biggest values
        tmp = tmp[tmp[:, 0] > min_val]


        z = tmp[:,0]
        if bckg != 0:
            z -= bckg
        
        x = tmp[:,1]
        y = tmp[:,2]

        sum_G = np.sum(z)
        sum_Gx = np.sum(z * (x - 0.5))
        sum_Gy = np.sum(z * (y - 0.5))

    return GravityCentreResult( center=((sum_Gx/sum_G), (sum_Gy/sum_G)), X_pixels=data_X, Y_pixels=data_Y, Z_pixels=data_Z )

if __name__ == "__main__":

    pixlim = 22
    init_x = 354
    init_y = 78
    alpha = 0
    A = B = 6

    from astropy.io import fits

    image = fits.getdata('../resources/14068A_R_1-001_d_m.fit')

    res = find_gravity_centre(init_x, init_y, A, B, alpha, image, pixlim)