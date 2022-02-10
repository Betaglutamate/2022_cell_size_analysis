import glob
from skimage import io
import pandas as pd

class Viewer():

    def __init__(self, directory):
        self.directory = directory

    # select cell number
    def select_cell_number(self):
        cell_analysis_dirs = glob.glob('test_images/cell*')
        num_cell_dirs = len(cell_analysis_dirs)

        for dir in cell_analysis_dirs:
            cell_images = io.imread_collection(dir + '/*.png')
            cell_masks = io.imread_collection(dir + '/_labelled'+ '/*.png')
            data = pd.read_csv(dir + '/analysis' + '/zz_cell_analysis.csv')

        return num_cell_dirs, cell_images, cell_masks, data


    # open the images
    # load the analysis df