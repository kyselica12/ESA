import concurrent
import run_serial
from  copy import deepcopy
from run_functions import combine_results


def execute_serial(arg):
    index, args, image = arg
    process = run_serial.Serial(args, image)
    return process.execute(index)


class Parallel:

    def __init__(self, args, image):
        
        self.args = args
        self.image = image

        self.parallel = self.args.parallel
        self.no_cores = self.parallel**2

    def execute(self):

        lenX = self.image.shape[0] // self.parallel
        lenY = self.image.shape[1] // self.parallel

        args = []

        for i in range(self.parallel):
            
            x_start = i*lenX 

            if i < self.parallel - 1:
                x_end = (i+1)*lenX
            else:
                x_end = self.image.shape[0]-1
            
            for j in range(self.parallel):

                y_start = j*lenY

                if j < self.parallel - 1:
                    y_end = (j+1)*lenY
                else:
                    y_end = self.image.shape[1]-1

                args.append(((x_start,x_end,y_start,y_end), deepcopy(self.args), self.image.copy()))

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [ result for result in executor.map(execute_serial, args)]

        result = combine_results(results)

        return result
