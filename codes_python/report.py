import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np
import seaborn as sns
import scipy
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from scipy.spatial import distance

MATCH_LIMIT = 1

def parse_cat(filename):

    points = []

    with open(filename, 'r') as f:
        lines = f.readlines()

        for line in lines[4:]:
            data = line.split()
            if len(data) == 17:
                points.append([float(data[11])-1, float(data[12])-1,float(data[13])])
                # idx 11: x pos, idx 12: y pos, idx 13: flux

    return np.array(points)



def matchObject(database, params):

    if '.cat' == params.model[-4:]:
        model = parse_cat(params.model)
    else:
        model = np.genfromtxt(params.model, delimiter='\t')

    found_points = database.data[:, 0:2]
    model_points = model[:, 0:2]

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

        if min_value[i] > MATCH_LIMIT:
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



def draw_picture(database, image, args, model):

    def colorFader(mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1 = 'yellow'
        c2 = 'red'
        c1 = np.array(matplotlib.colors.to_rgb(c1))
        c2 = np.array(matplotlib.colors.to_rgb(c2))
        return matplotlib.colors.to_hex((1 - mix) * c1 + mix * c2)

    f1, ax = plt.subplots(1)
    f1.set_size_inches(7, 7)

    ax.imshow(image, cmap='gray', vmin=0, vmax=10)

    titles =('SNR', 'SNR', 'SNR', 'ITER', 'SUM', 'MEAN', 'VAR', 'STD', 'SKEW', 'KURT', 'BCKG')
    title = titles[args.color-1]
    col_data = database.data[:, args.color-1]

    if model is not None:
        for i, data in enumerate(model[:, 0:2]):
            x, y = data
            rec = matplotlib.patches.Rectangle((x - args.height / 2, y - args.width / 2), args.width, args.height,
                                               edgecolor='grey', facecolor="none")
            t = matplotlib.transforms.Affine2D().rotate_deg_around(x, y, args.angle) + ax.transData
            rec.set_transform(t)
            ax.add_patch(rec)


    for i, data in enumerate(database.data[:,0:2]):
        color = colorFader((col_data[i] - np.min(col_data)) / (np.max(col_data) - np.min(col_data)))
        x, y = data
        rec = matplotlib.patches.Rectangle((x-args.height/2, y-args.width/2), args.width, args.height, edgecolor=color, facecolor="none")
        t = matplotlib.transforms.Affine2D().rotate_deg_around(x, y, args.angle) + ax.transData
        rec.set_transform(t)
        ax.add_patch(rec)

    f2, ax = plt.subplots(1)
    f2.set_size_inches(5, 1.5)

    for x in range(500):
        ax.axvline(x, color=colorFader(x / 500), linewidth=4, ymax=0.1)
    ax.axis('off')
    ax.set_title(title)
    ttl = ax.title
    ttl.set_position([0.5, 0.5])

    return f1, f2


def create_hist(data,title, ax, xlabel=''):

    sns.distplot(data,bins=50, hist=True, ax=ax)
    sns.distplot(data,bins=50, hist=False, kde=True, norm_hist=False, label='density', ax=ax)
    sns.distplot(data,bins=50, fit=scipy.stats.norm, kde=False, hist=False,norm_hist=False, ax=ax, label='normal')
    ax.set_title(title)
    ax.set_ylabel('Density')
    ax.set_xlabel(xlabel)
    ax.legend()


def iter_hist(database):
    fig = plt.figure()

    axs = fig.subplots(2,2)

    sns.distplot(database.data[:, 3], bins=50, hist=True, ax=axs[0][1])

    axs[0][1].set_title("iter")

    create_hist(database.data[:, 2], title='SNR', ax=axs[0][0])
    create_hist(database.data[:, 8], title='skew', ax=axs[1][0])
    create_hist(database.data[:, 9], title='kurt', ax=axs[1][1])

    fig.set_size_inches(7.5, 7, forward=True)

    return fig

def model_hist(database, model, matched):

    fig = plt.figure()
    axs = fig.subplots(2, 2)

    X = database.data[matched[:,0], 0] - model[matched[:,1], 0]
    create_hist(X, title=f'X axis differences {np.mean(X):.4f}', ax=axs[0][0], xlabel='X difference')

    Y = database.data[matched[:,0], 1] - model[matched[:,1], 1]
    create_hist(Y, title=f'Y axis differences {np.mean(Y):.4f}', ax=axs[0][1], xlabel='Y difference')

    E = np.sqrt(X**2 + Y**2)
    create_hist(E, title='Euclidean differences', ax=axs[1][0], xlabel='Distances')
    create_hist(np.log(E), title='Log Euclidean differences', ax=axs[1][1], xlabel='Log distances')

    fig.set_size_inches(7.5, 9, forward=True)

    return X, Y, E, fig

def rms(param):
    pass


def error_scat(X, Y):

    fig = plt.figure()
    ax = fig.subplots(1)

    ax.plot(X, Y, 'o', color='black')

    return fig

def generate_report(database, image, args):

    if args.model is not None:
        model, matched, unmatched = matchObject(database, args)
    else:
        model = None
        matched = np.array([])
        unmatched = np.array([])

    # iter_hist(database)

    f_image, f_heat_map = draw_picture(database, image, args, model)
    f_hist = iter_hist(database)

    pp = PdfPages(f'{args.output}.pdf')
    pp.savefig(f_image)
    pp.savefig(f_heat_map)
    pp.savefig(f_hist)

    if model is not None:
        X, Y, E, f_model = model_hist(database, model, matched)
        f_error = error_scat(X, Y)

        pp.savefig(f_model)
        pp.savefig(f_error)

    pp.close()



    # XY = model_hist(database, model, matched)
    #
    # #invisible(dev.off()
    #
    # if XY is None:
    #     XY = ([0],[0])
    #
    # return matched, unmatched, model, np.mean(XY[0]), np.mean(XY[1]), rms(XY[0]), rms(XY[1])