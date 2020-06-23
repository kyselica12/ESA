import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.optimize import curve_fit

from processing.psf_segmentation.point_cluster import PointCluster

np.seterr(all='ignore')

def sobel_extract_clusters(image, threshold=20):
    image_int32 = image.astype('int32')
    dx = ndimage.sobel(image_int32, 0)
    dy = ndimage.sobel(image_int32, 1)
    mag = np.hypot(dx, dy)
    mag *= 255.0 / np.max(mag)
    original_mask = mag
    mask = original_mask >= threshold

    points = list()

    joined_points = join_neigbor_points_mask(mask)

    noise_dispersion = int( histogram_threshold( image, sigma_only=True ))

    clusters = []
    for point_mesh in joined_points:
        cluster = PointCluster(point_mesh, image)
        cluster.noise_dispersion = noise_dispersion
        cluster.sobel = True
        clusters.append(cluster)
    return clusters

def join_neigbor_points_mask(mask):
    joined_points = list()
    for y, row in enumerate(mask):
        for x, value in enumerate(row):
            if value == 1:
                mask[y][x] = 0
                cluster = list()
                cluster.append((x,y))
                stack = [(x,y)]
                while len(stack) > 0:
                    x_p,y_p = stack.pop()
                    if x_p-1 >= 0 and mask[y_p][x_p-1] == 1:
                        mask[y_p][x_p-1] = 0
                        stack.append((x_p-1,y_p))
                        cluster.append((x_p-1,y_p))
                    if x_p+1 < mask.shape[1] and mask[y_p][x_p+1] == 1:
                        mask[y_p][x_p+1] = 0
                        stack.append((x_p+1,y_p))
                        cluster.append((x_p+1,y_p))
                    if y_p-1 >= 0 and mask[y_p-1][x_p] == 1:
                        mask[y_p-1][x_p] = 0
                        stack.append((x_p,y_p-1))
                        cluster.append((x_p,y_p-1))
                    if y_p+1 < mask.shape[0] and mask[y_p+1][x_p] == 1:
                        mask[y_p+1][x_p] = 0
                        stack.append((x_p,y_p+1))
                        cluster.append((x_p,y_p+1))
                joined_points.append(cluster)
    return joined_points

def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / wid)

def histogram_threshold(image, show=False, threshold_sigma=2, sigma_only=False):
    hist, bins = np.histogram(image.flatten(), bins=len(np.unique(image)))

    init_vals = [1000., 0., 1000.]
    np.seterr(all='ignore')
    best_vals, covar = curve_fit(gaussian, [x for x in range(len(hist))], hist, p0=init_vals, maxfev=5000)

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