import math
import random
import numpy as np
import copy
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from scipy.optimize import curve_fit


np.seterr(all='ignore')

def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / wid)

def histogram_threshold(image, show=False, threshold_sigma=2, sigma_only=False):
    hist, bins = np.histogram(image.flatten(), bins=len(np.unique(image)))

    init_vals = [1000., 0., 1000.]

    np.seterr(all='ignore')
    best_vals, covar = curve_fit(gaussian, [x for x in range(len(hist))], hist, p0=init_vals)#, maxfev=1000)
    # Get the fitted curve
    hist_fit = gaussian([x for x in range(len(hist))], *best_vals)

    center = int(best_vals[1])
    sigma = int(best_vals[2])
    if sigma_only:
        return sigma
    threshold = int(center + sigma*threshold_sigma)
    if show:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # smoothed = smooth(hist,15) ax.bar([x for x in range(len(hist))], hist)
        ax.axvline(threshold, color='green', label='threshold')
        ax.axvline(center, color='brown', label='center')
        ax.axvline(center+sigma, color='yellow', label='center+sigma')
        ax.plot([x for x in range(len(hist))], hist, label='Test data', color='red')
        ax.plot([x for x in range(len(hist))], hist_fit, label='Fitted data', color='blue')
        plt.show()
        return bins[threshold]
    else:
        return bins[threshold]

if __name__ == '__main__':
    image = fits.getdata('data/M27_R_60s-001.fit')
    histogram_threshold(image, True)
