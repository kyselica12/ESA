import pandas as pd
import scipy.cluster.hierarchy as hcluster

pixels = pd.DataFrame(pixels)

clusters = hcluster.fclusterdata(pixels, thresh, criterion='distance').tolist()
