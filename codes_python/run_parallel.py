import concurrent
import run_serial
import run_functions

class Parallel:

    def __init__(self, args, image):
        
        self.args = args
        self.image = image

        self.parallel = self.args.parallel
        self.no_cores = self.parallel**2

    def execute(self):
        
        def execute_serial(index):
            process = run_serial.Serial(self.args, self.image)
            return process.execute(index)
        
        lenX = self.image.shape[0] // self.parallel
        lenY = self.image.shape[1] // self.parallel

        indexes = []

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

                indexes.append((x_start,x_end,y_start,y_end))

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(execute_serial, indexes)
        

        result = run_functions.combine_results(results)

        return result
