import numpy as np
from database import *
import pandas as pd
import scipy.cluster.hierarchy as hcluster


class Serial:

    def __init__(self, log_file=""):
        self.log_file = log_file

    def log(self,msg):

        if self.log_file == "":
            print(msg)
        else:
            with open(self.log_file, 'a') as lf:
                print(msg, file=lf)

    def clear_statistics(self):
        self.started = 0
        self.nulldata = 0
        self.notenough = 0
        self.nocentre = 0
        self.maxiter = 0
        self.miniter = 0
        self.lowsnr = 0
        self.ok = 0
        self.notright = 0

    def execute(self, index, args, image):
        
        self.clear_statistics()

        x_start, x_end, y_start, y_end = index


        names = ('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
        database  = Database(init_value=0, nrows=0, ncols=11, col_names=names )
        discarded = Database(init_value=0, nrows=0, ncols=11, col_names=names )

        A = args.width
        B = args.height

        if args.method == 'sweep':

            Xs = np.floor(np.arange(x_start + A, x_end - A, 2*A ))
            Ys = np.floor(np.arange(y_start + B, y_end - B, 2*B ))

            for y in Ys:
                for x in Xs:
                    self.perform_step(x, y)

        elif args.method == 'max':
            pixels = np.where(image > args.start_iter)

            Xs = pixels[0]
            Ys = pixels[1]

            Xs = Xs[np.logical_and(Xs > x_start, Xs < x_end)]
            Ys = Ys[np.logical_and(Ys > y_start, Ys < y_end)]

            while len(Xs) > 0:
                step = self.perform_step(Xs[0], Ys[0])
                
                Xs = Xs[1:]
                Ys = Ys[1:]
                
                if step['code'] == 0:
                    filt_X = np.logical_and((Xs >= (step['x'] - A)), (Xs <= (step['x'] + A)))
                    filt_Y = np.logical_and((Ys >= (step['y'] - B)), (Ys <= (step['y'] + B)))
                    filt = np.logical_and(filt_X, filt_Y)
                    ok = np.logical_not(filt)

                    Xs = Xs[ok]
                    Ys = Ys[ok]

        elif args.method == 'cluster':
            pixels = np.where(image > args.start_iter)

            Xs = pixels[0]
            Ys = pixels[1]

            Xs = Xs[np.logical_and(Xs > x_start, Xs < x_end)]
            Ys = Ys[np.logical_and(Ys > y_start, Ys < y_end)]

            pixels = pd.DataFrame( pixels[Xs, Ys] )
            thresh = np.sqrt(A**2 + B**2)

            clusters = hcluster.fclusterdata(pixels, thresh, criterion='distance')

            for i in range(1, np.max(clusters)+1):
                XY = pixels[clusters == i]
                X = XY[:,0]
                Y = XY[:,1]

                Z = np.arraY([image[X[j], Y[j]] for j in range(len(XY))])

                sumG = np.sum(Z)
                sumGx = np.sum(Z*(X-0.5))
                sumGy = np.sum(Z*(Y-0.5))

                self.perform_step(sumGx/sumG, sumGy/sumG)

        return database, discarded



    def perform_step(self, x,y):
        #TODO
        return {}

