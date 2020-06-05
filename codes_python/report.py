import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np
import seaborn as sns
import scipy
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib


def matchObject(database, params):
    pass


def pdf(report):
    pass


def draw_picture(database, image, args):

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


def create_hist(data,title, ax):

    sns.distplot(data,bins=50, hist=True, ax=ax)
    sns.distplot(data,bins=50, hist=False, kde=True, norm_hist=False, label='density', ax=ax)
    sns.distplot(data,bins=50, fit=scipy.stats.norm, kde=False, hist=False,norm_hist=False, ax=ax, label='normal')
    ax.set_title(title)
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
    pass


def rms(param):
    pass


def generate_report(database, image, args):



    # iter_hist(database)

    f_image, f_heat_map = draw_picture(database, image, args)
    f_hist = iter_hist(database)

    pp = PdfPages(f'{args.output}.pdf')
    pp.savefig(f_image)
    pp.savefig(f_heat_map)
    pp.savefig(f_hist)
    pp.close()


    # if params.model is not None:
    #     no = matchObject(database, params)
    #     model = no.model
    #     matched = no.matched
    #     unmatched = no.unmatched
    # else:
    #     model = None
    #     matched = np.array([])
    #     unmatched = np.array([])
    #
    # pdf(params.report)
    #
    # draw_picture(database, params, model)
    #
    # iter_hist(database)
    # XY = model_hist(database, model, matched)
    #
    # #invisible(dev.off()
    #
    # if XY is None:
    #     XY = ([0],[0])
    #
    # return matched, unmatched, model, np.mean(XY[0]), np.mean(XY[1]), rms(XY[0]), rms(XY[1])