import scipy.cluster.hierarchy as hcluster

from processing.psf_segmentation.background_extraction_cli import sigma_clipper
from processing.psf_segmentation.point_cluster import PointCluster
from processing.psf_segmentation.sobel import sobel_extract_clusters
from processing.getPixels import get_pixels
from processing.wrapper import CentroidSimpleWrapper
from utils.structures import *

from utils.structures import Database

import os


class Serial:

    def __init__(self, args, image, log_file=""):
        self.args: Configuration = args
        self.log_file = log_file
        self.image = image
        self.psf_bckg = None

    def log(self,msg):

        if self.log_file == "":
            print(msg)
        else:
            with open(self.log_file, 'a') as lf:
                print(msg, end='', file=lf)

    def clear_statistics(self):
        self.stats = Stats()

    def execute(self, index):
        self.clear_statistics()

        x_start, x_end, y_start, y_end = index

        self.database  = Database()
        self.discarded = Database()

        A = self.args.width
        B = self.args.height

        if self.args.method == 'sweep':

            Xs = np.floor(np.arange(x_start + A, x_end - A, 2*A )).astype(int)
            Ys = np.floor(np.arange(y_start + B, y_end - B, 2*B )).astype(int)

            for y in Ys:
                for x in Xs:
                    self.perform_step(x, y)

        elif self.args.method == 'max':
            pixels = np.where(self.image > self.args.start_iter)

            Xs = pixels[1]
            Ys = pixels[0]

            good = (Xs > x_start) * (Xs < x_end) * (Ys > y_start) * (Ys < y_end)
            Xs = Xs[good]
            Ys = Ys[good]

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

            Xs = pixels[1]
            Ys = pixels[0]

            good = (Xs > x_start) * (Xs < x_end) * (Ys > y_start) * (Ys < y_end)
            Xs = Xs[good]
            Ys = Ys[good]

            pixels = np.zeros((len(Xs), 2))
            pixels[:,0] = Ys
            pixels[:,1] = Xs
            thresh = np.sqrt(A**2 + B**2)

            clusters = hcluster.fclusterdata(pixels, thresh, criterion='distance')


            for i in range(1, np.max(clusters)+1):
                YX = pixels[clusters == i]
                X = YX[:, 1]
                Y = YX[:, 0]

                Z = self.image[Y, X]

                sumG = np.sum(Z)
                sumGx = np.sum(Z * (X - 0.5))
                sumGy = np.sum(Z * (Y - 0.5))

                self.perform_step(sumGx / sumG, sumGy / sumG)

        elif self.args.method == "sobel":
            image = self.image[x_start: x_end, y_start: y_end]
            sobel_threshold = self.args.sobel_threshold

            joined_points = sobel_extract_clusters(image, threshold=sobel_threshold)

            for XY in joined_points:

                XY = np.array(XY)
                X = XY[:, 0]
                Y = XY[:, 1]

                Z = self.image[Y, X]

                sumG = np.sum(Z)
                sumGx = np.sum(Z * (X - 0.5))
                sumGy = np.sum(Z * (Y - 0.5))

                self.perform_step(sumGx / sumG, sumGy / sumG)


        return SerialResult(database=self.database, discarded=self.discarded, stats=self.stats)

    def psf(self, current):
        cent_x = current.result.data[0]
        cent_y = current.result.data[1]

        X, Y, Z = get_pixels(cent_x=cent_x, cent_y=cent_y,
                             A=self.args.width, B=self.args.height,
                             alpha=self.args.angle, image=self.image)
        X = X.reshape(-1,1)
        Y = Y.reshape(-1,1)
        points = np.concatenate((X, Y),axis=1).astype(int)
        cluster = PointCluster(points, self.image)

        if self.psf_bckg is None:
            number_of_iterations = self.args.bkg_iterations
            self.psf_bckg = sigma_clipper(self.image, iterations=number_of_iterations)

        fit_function = self.args.fit_function
        square_size = (self.args.width , self.args.height )

        cluster.show_object_fit = False
        cluster.show_object_fit_separate = False
        cluster.add_background_data(self.psf_bckg)
        try:
            cluster.fit_curve(function=fit_function, square_size=square_size)
        except Exception as e:
            pass

        if cluster.correct_fit:
            return WrapperResult(result=cluster.output_database_item(),
                                 noise=cluster.noise_median,
                                 log=current.log,
                                 message='OK',
                                 code=0)
        else:
            iter = current.result.data[3]
            return WrapperResult(result=DatabaseItem(cent_x, cent_y, iter=iter),
                                 noise=-1,
                                 log=current.log,
                                 message='Centre not right.',
                                 code=8)

    def is_point_object(self, current):
        return False

    def perform_step(self, x,y):

        self.stats.started += 1

        wrapper = CentroidSimpleWrapper(image=self.image, 
                                        init_x=x, 
                                        init_y=y,
                                        A=self.args.width,
                                        B=self.args.height,
                                        noise_dim=self.args.noise_dim,
                                        alpha=self.args.angle*np.pi/180,
                                        local_noise=self.args.local_noise,
                                        delta=self.args.delta,
                                        pix_lim=self.args.start_iter,
                                        pix_prop=self.args.cent_pix_perc,
                                        max_iter=self.args.max_iter,
                                        min_iter=self.args.min_iter,
                                        snr_lim=self.args.snr_lim,
                                        fine_iter=self.args.fine_iter,
                                        is_point=self.args.width == self.args.height)
        current = wrapper.execute()

        if self.is_point_object(current):
            wrapper.init_x = current.result.data[0]
            wrapper.init_y = current.result.data[1]
            wrapper.A = self.args.height
            wrapper.B = self.args.height
            wrapper.alpha = 0
            current = wrapper.execute()

        if self.args.psf and current.code == 0:
            current = self.psf(current)




        self.update_statistics(x,y,current)
        

        if current.code == 0:
            return Step(code=0, x=current.result.data[0], y=current.result.data[1])
        else:
            return Step(code=1, x=-1, y=-1)
         
    def update_statistics(self,x,y, current):
        if current.code == 0:
            self.stats.ok += 1

            ud_code = self.database.update(current.result, self.args.centre_limit)

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
            self.stats.nulldata += 1
        
        elif current.code == 2:
            self.stats.notenough += 1

        elif current.code == 3:
            self.stats.notbright += 1

        elif current.code == 4:
            self.stats.nocentre += 1

        elif current.code == 5:
            self.stats.maxiter += 1

        elif current.code == 6:
            self.stats.miniter += 1

        elif current.code == 7:
            self.stats.lowsnr += 1

        elif current.code == 8:
            self.stats.notright += 1