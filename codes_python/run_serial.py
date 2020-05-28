import numpy as np
from database import *
import pandas as pd
import scipy.cluster.hierarchy as hcluster
from wrapper import CentroidSimpleWrapper
from structures import *


# ??? toto treba niekde vhodne umiestnit je to global povodne
CENTRE_LIMIT = 0


class Serial:

    def __init__(self, args, image, log_file=""):
        self.args = args
        self.log_file = log_file
        self.image = image

    def log(self,msg):

        if self.log_file == "":
            print(msg)
        else:
            with open(self.log_file, 'a') as lf:
                print(msg, end='', file=lf)

    def clear_statistics(self):
        self.started = 0
        self.nulldata = 0
        self.notenough = 0
        self.nocentre = 0
        self.maxiter = 0
        self.miniter = 0
        self.lowsnr = 0
        self.ok = 0
        self.notbright = 0
        self.notright = 0

    def execute(self, index):
        
        self.clear_statistics()

        x_start, x_end, y_start, y_end = index


        names = ('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
        self.database  = Database(init_value=0, nrows=0, ncols=11, col_names=names )
        self.discarded = Database(init_value=0, nrows=0, ncols=11, col_names=names )

        A = self.args.width
        B = self.args.height

        if self.args.method == 'sweep':

            Xs = np.floor(np.arange(x_start + A, x_end - A, 2*A ))
            Ys = np.floor(np.arange(y_start + B, y_end - B, 2*B ))

            for y in Ys:
                for x in Xs:
                    self.perform_step(x, y)

        elif self.args.method == 'max':
            pixels = np.where(self.image > self.args.start_iter)

            Xs = pixels[0]
            Ys = pixels[1]

            Xs = Xs[np.logical_and(Xs > x_start, Xs < x_end)]
            Ys = Ys[np.logical_and(Ys > y_start, Ys < y_end)]

            while len(Xs) > 0:
                step = self.perform_step(Xs[0], Ys[0])
                
                Xs = Xs[1:]
                Ys = Ys[1:]
                
                if step.code == 0:
                    filt_X = np.logical_and((Xs >= (step.x - A)), (Xs <= (step.x + A)))
                    filt_Y = np.logical_and((Ys >= (step.y - B)), (Ys <= (step.y + B)))
                    filt = np.logical_and(filt_X, filt_Y)
                    ok = np.logical_not(filt)

                    Xs = Xs[ok]
                    Ys = Ys[ok]

        elif self.args.method == 'cluster':
            pixels = np.where(self.image > self.args.start_iter)

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

                Z = np.arraY([self.image[X[j], Y[j]] for j in range(len(XY))])

                sumG = np.sum(Z)
                sumGx = np.sum(Z*(X-0.5))
                sumGy = np.sum(Z*(Y-0.5))

                self.perform_step(sumGx/sumG, sumGy/sumG)

        return SerialResult(database=self.database,
                            discarded=self.discarded,
                            stats=Stats(started=self.started,
                                        nulldata=self.nulldata,
                                        notbright=self.notbright,
                                        notenough=self.notenough,
                                        nocentre=self.nocentre,
                                        maxiter=self.maxiter,
                                        miniter=self.miniter,
                                        lowsnr=self.lowsnr,
                                        ok=self.ok,
                                        notright=self.notright
                                        )
                            )

    def perform_step(self, x,y):
        
        self.started += 1

        wrapper = CentroidSimpleWrapper(image=self.image, 
                                        init_x=x, 
                                        init_y=y,
                                        A=self.args.width,
                                        B=self.args.height,
                                        noise_dim=self.args.noise_dim,
                                        alpha=self.args.alpha,
                                        local_noise=self.args.local_noise,
                                        delta=self.args.delta,
                                        pix_lim=self.args.pix_lim,
                                        pix_prop=self.args.pix_prop,
                                        max_iter=self.args.max_iter,
                                        min_iter=self.args.min_iter,
                                        snr_lim=self.args.snr_lim,
                                        fine_iter=self.args.fine_iter,
                                        is_point=self.args.width == self.args.height)
        current = wrapper.execute()

        self.update_statistics(x,y,current)
        

        if current.code == 0:
            return Step(code=0,
                        x=current.relust[0],
                        y=current.result[1]
                        )
        else:
            return Step(code=1,x=-1,y=-1)
         
    def update_statistics(self,x,y, current):
        if current.code == 0:
            self.ok += 1

            ud_code = self.database.update(current.result, CENTRE_LIMIT)

            if ud_code == 1:
                self.discarded.add(current.result)
            else:
                if self.args.verbose == 1 and self.args.parallel == 1:

                    self.log(f'{x}, {y}\n')
                    
                    for line in current.log:
                        for c in line:
                            self.log(f"{c:.6f}\t")
                        self.log('\n')
                    self.log('\n')
        
        elif current.code == 1:
            self.nulldata += 1
        
        elif current.code == 2:
            self.notenough += 1

        elif current.code == 3:
            self.notbright += 1

        elif current.code == 4:
            self.nocentre += 1

        elif current.code == 5:
            self.maxiter += 1

        elif current.code == 6:
            self.miniter += 1

        elif current.code == 7:
            self.lowsnr += 1

        elif current.code == 8:
            self.notright += 1