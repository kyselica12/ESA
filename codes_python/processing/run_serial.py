import scipy.cluster.hierarchy as hcluster

from processing.psf_segmentation.background_extraction_cli import sigma_clipper
from processing.psf_segmentation.sobel import sobel_extract_clusters
from processing.wrapper import CentroidSimpleWrapper
from utils.structures import *


# ??? toto treba niekde vhodne umiestnit je to global povodne
from utils.structures import Database

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
        self.stats = Stats()

    def execute(self, index):
        self.clear_statistics()

        x_start, x_end, y_start, y_end = index


        names = ('cent.x', 'cent.y', 'snr', 'iter', 'sum', 'mean', 'var', 'std', 'skew', 'kurt', 'bckg')
        self.database  = Database(init_value=0, nrows=0, ncols=11, col_names=names )
        self.discarded = Database(init_value=0, nrows=0, ncols=11, col_names=names )

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

            # idx = np.argsort(Xs)
            # Xs = Xs[idx]
            # Ys = Ys[idx]

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
                XY = pixels[clusters == i]
                X = XY[:,1].astype(int)
                Y = XY[:,0].astype(int)

                Z = self.image[Y, X]

                sumG = np.sum(Z)
                sumGx = np.sum(Z*(X-0.5))
                sumGy = np.sum(Z*(Y-0.5))

                self.perform_step(sumGx/sumG, sumGy/sumG)

        elif self.args.method == "sobel":
            print('Sobel')
            image = self.image[x_start: x_end, y_start: y_end]
            sobel_threshold = 20
            fit_function = 'gauss'
            number_of_iterations = 2
            square_size = (6, 6)

            extracted_point_clusters = sobel_extract_clusters(image, threshold=sobel_threshold)
            print('Calculating image background...')
            background = sigma_clipper(image, iterations=number_of_iterations)

            output_data = []
            print('Fitting functions to clusters...')
            for i, cluster in enumerate(extracted_point_clusters):
                cluster.show_object_fit = False
                cluster.show_object_fit_separate = False
                # cluster.add_header_data(headers)
                cluster.add_background_data(background)
                try:
                    params = cluster.fit_curve(function=fit_function, square_size=square_size)
                except Exception as e:
                    continue  # suppress all Exceptions, incorrect fits are discarded
                finally:
                    pass
                    # print('.', end='')
                    # if not show_object_fit and not show_object_fit_separate:
                    #     progressBar(i, len(extracted_point_clusters) - 1)

                if cluster.correct_fit:
                    # print('+', end='')
                    output_data.append(cluster.output_data())
                    # print(cluster)
                    # self.database.add(cluster.output_data())

            result = ""
            result += '-' * 150 + '\n'
            result += '{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}'.format("x", "y", "flux", "fwhm_x|fwhm_y",
                                                                                "peak_SNR", "fit_rms", "skew_x|skew_y",
                                                                                "kurt_x|kurt_y") + '\n'
            result += '-' * 150 + '\n'
            for i, data in enumerate(output_data):
                result += '{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}'.format(data[0], data[1], data[2], data[3],
                                                                                    data[4], data[5], data[6],
                                                                                    data[7]) + '\n'

            print(result)
            self.stats.started = len(extracted_point_clusters)
            self.stats.ok = len(output_data)
            self.stats.notright = len(extracted_point_clusters) - len(output_data)



        return SerialResult(database=self.database, discarded=self.discarded, stats=self.stats)

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

        self.update_statistics(x,y,current)
        

        if current.code == 0:
            return Step(code=0, x=current.result[0], y=current.result[1])
        else:
            return Step(code=1, x=-1, y=-1)
         
    def update_statistics(self,x,y, current):
        if current.code == 0:
            self.stats.ok += 1

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