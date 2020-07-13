import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import gaussian_kde
import numpy as np
import scipy
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from scipy.spatial import distance
from scipy.stats import norm, gaussian_kde
from utils.run_functions import rms
from utils.structures import Report, Configuration

# MATCH_LIMIT = 1


def parse_cat(filename):
    points = []

    with open(filename, 'r') as f:
        lines = f.readlines()

        for line in lines[4:]:
            data = line.split()
            if len(data) == 17:
                points.append([float(data[11]) - 1, float(data[12]) - 1, float(data[13])])
                # idx 11: x pos, idx 12: y pos, idx 13: flux

    return np.array(points)


def match_objects(database, params):
    if '.cat' == params.model[-4:]:
        model = parse_cat(params.model)
    else:
        model = np.genfromtxt(params.model, delimiter='\t')

    found_points = database.data[:, 0:2].astype(np.float32)
    model_points = model[:, 0:2]

    # idx = np.argsort(found_points[:,0])
    # found_points = found_points[idx]

    dist = distance.cdist(found_points, model_points, 'euclidean')

    min_idx = np.argmin(dist, axis=1)
    min_value = np.min(dist, axis=1)

    processed = set()
    used = set()
    matched = []
    unmatched = []
    i = 0

    while len(processed) != len(dist):

        if i in processed:
            i += 1
            continue

        if min_value[i] > params.match_limit:
            unmatched.append([i, min_value[i]])
            processed.add(i)
            i += 1
            continue

        model_min_idx = np.argmin(min_value)

        if min_idx[model_min_idx] in used:
            # is used
            min_value[model_min_idx] = np.min(dist[model_min_idx])
            min_idx[model_min_idx] = np.argmin(dist[model_min_idx])
        else:
            # is free
            # set a match

            matched.append([model_min_idx, min_idx[model_min_idx]])

            # mark as used
            used.add(min_idx[model_min_idx])
            dist[:, min_idx[model_min_idx]] = 1000

            processed.add(model_min_idx)
            min_value[model_min_idx] = 1000

    return model, np.array(matched), np.array(unmatched)


def draw_picture(database, image, args: Configuration, model):

    fig, ax = plt.subplots(1)
    fig.set_size_inches(8.5, 8)


    titles = ('SNR', 'SNR', 'SNR', 'ITER', 'SUM', 'MEAN', 'VAR', 'STD', 'SKEW', 'KURT', 'BCKG')
    title = titles[args.color - 1]
    col_data = database.data[:, args.color - 1]

    cmap = plt.get_cmap('autumn')
    norm = mpl.colors.Normalize(vmin=np.min(col_data), vmax=np.max(col_data))

    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                 ax=ax, label='SNR')

    if model is not None:
        for i, data in enumerate(model[:, 0:2]):
            x, y = data
            rec = matplotlib.patches.Rectangle((x -  args.width, y - args.height), 2*args.width, 2*args.height,
                                               edgecolor='white', facecolor="none", linewidth=0.5)
            t = matplotlib.transforms.Affine2D().rotate_deg_around(x, y, args.angle) + ax.transData
            rec.set_transform(t)
            ax.add_patch(rec)

    for i, data in enumerate(database.data[:, 0:2]):
        color = cmap(norm(col_data[i]))
        x, y = data
        rec = matplotlib.patches.Rectangle((x - args.width, y - args.height), 2*args.width, 2*args.height,
                                           edgecolor=color, facecolor="none", linewidth=0.5, linestyle='dotted')
        t = matplotlib.transforms.Affine2D().rotate_deg_around(x, y, args.angle) + ax.transData
        rec.set_transform(t)
        ax.add_patch(rec)

    ax.imshow(image, cmap='gray', origin='lower', vmin=0, vmax=10)

    return fig


def create_hist(data, title, ax, xlabel='', ylabel='', plot_normal=True):

    data = data.astype(np.float32)

    mu, std = norm.fit(data)

    # Plot the histogram.
    ax.hist(data, bins=50, density=True, alpha=0.6, color='skyblue')

    # Plot the PDF.
    ax.get_xlim()
    xmin, xmax = ax.get_xlim()

    offset = (xmax - xmin)*0.2
    xmax += offset
    xmin -= offset
    x = np.linspace(xmin, xmax, 100)

    if plot_normal:
        p = norm.pdf(x, mu, std)
        ax.plot(x, p, 'k', linewidth=2, label='normal', color='black')

    density = gaussian_kde(data)
    density.covariance_factor = lambda: .5
    density._compute_covariance()
    ax.plot(x, density(x), label='density', color='orange')

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend()


def iter_hist(database):
    fig = plt.figure()

    axs = fig.subplots(2, 2)

    create_hist(database.data[:, 3], title='iter', ax=axs[0][1], plot_normal=False)

    create_hist(database.data[:, 2], title='SNR', ax=axs[0][0], ylabel='Density', plot_normal=True)
    create_hist(database.data[:, 8], title='skew', ax=axs[1][0], ylabel='Density', plot_normal=True)
    create_hist(database.data[:, 9], title='kurt', ax=axs[1][1], ylabel='Density', plot_normal=True)

    fig.set_size_inches(8.5, 8, forward=True)
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    return fig


def model_hist(database, model, matched):
    fig = plt.figure()
    axs = fig.subplots(2, 2)

    X, Y = np.array([]), np.array([])

    #Fixme No matching starts cause error

    X = database.data[matched[:, 0], 0] - model[matched[:, 1], 0]
    X = X.astype(np.float32)
    create_hist(X, title=f'X axis differences {np.mean(X):.4f}', ax=axs[0][0], xlabel='X difference')

    Y = database.data[matched[:, 0], 1] - model[matched[:, 1], 1].astype(np.float32)
    Y = Y.astype(np.float32)
    create_hist(Y, title=f'Y axis differences {np.mean(Y):.4f}', ax=axs[0][1], xlabel='Y difference')

    E = np.sqrt(X ** 2 + Y ** 2)

    create_hist(E, title='Euclidean differences', ax=axs[1][0], xlabel='Distances')
    create_hist(np.log(E), title='Log Euclidean differences', ax=axs[1][1], xlabel='Log distances')

    fig.set_size_inches(8.5, 8, forward=True)
    fig.subplots_adjust(hspace=0.5)

    return X, Y, E, fig


def error_scat(X, Y):
    fig = plt.figure()
    fig.set_size_inches(8.5, 8, forward=True)
    ax = fig.subplots(1)

    # ax.plot(X, Y, 'o', color='black')
    ax.scatter(X, Y, s=50, facecolors='none', edgecolors='black')
    # ax.hlines(np.mean(Y), colors='r', linestyles='dashed')
    ax.axvline(np.mean(X), color="r", linestyle='dashed')
    ax.axhline(np.mean(Y), color="r", linestyle='dashed')
    ax.set_title('Error points')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    return fig


def brightness_scat(database, model, matched):

    fig = plt.figure()
    fig.set_size_inches(8.5, 8, forward=True)
    ax = fig.subplots(1)

    X = database.data[matched[:, 0], 4].astype(np.float32)
    Y = model[matched[:, 1], 2]
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(X, Y)

    ax.scatter(X, Y, s=30, facecolors='none', edgecolors='black' )

    t = np.linspace(np.min(X),np.max(X))

    ax.plot(t, t*slope + intercept, color='red', label=f'model = {slope:.3f}*SCA + ( {intercept:.4f} )')
    ax.legend()
    ax.set_ylabel('Model')
    ax.set_xlabel('SCA')

    ax.set_title('Total brightness')

    return fig

def no_matched_text():

    fig = plt.figure()
    fig.set_size_inches(8.5, 8, forward=True)
    ax = fig.subplots(1)


    plt.text(0.5, 0.5, 'No stars matched', fontsize=25, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.set_axis_off()


    return fig

def generate_report(database, image, args):
    if args.model is not None and args.model != "":
        model, matched, unmatched = match_objects(database, args)
    else:
        model = None
        matched = np.array([])
        unmatched = np.array([])

    # iter_hist(database)

    f_image = draw_picture(database, image, args, model)
    f_hist = iter_hist(database)

    pp = PdfPages(f'{args.output}.pdf')
    pp.savefig(f_image)
    pp.savefig(f_hist)

    X, Y = None, None
    if model is not None:

        if len(matched) > 0:

            X, Y, E, f_model = model_hist(database, model, matched)
            f_error = error_scat(X, Y)

            f_brightness = brightness_scat(database, model, matched)

            pp.savefig(f_model)
            pp.savefig(f_error)
            pp.savefig(f_brightness)

        else:

            f_no_matched = no_matched_text()
            pp.savefig(f_no_matched)

    pp.close()
    return Report(matched=matched,
                  unmatched=unmatched,
                  model=model,
                  X=np.mean(X) if X is not None else 0,
                  Y=np.mean(Y) if Y is not None else 0,
                  rms_x=rms(X) if X is not None else 0,
                  rms_y=rms(Y) if Y is not None else 0
                  )

