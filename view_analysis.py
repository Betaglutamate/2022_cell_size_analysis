import glob
from skimage import io
from pandas import read_csv

class Viewer():

    def __init__(self, directory):
        self.directory = directory

    # select cell number
    def select_cell_number(self):
        cell_analysis_dirs = glob.glob('test_images/cell*')
        num_cell_dirs = len(cell_analysis_dirs)

        all_cell_images = []
        all_cell_masks = []
        all_cell_data = []

        for dir in cell_analysis_dirs:
            cell_images = io.imread_collection(dir + '/*.png')
            cell_masks = io.imread_collection(dir + '/_labelled'+ '/*.png')
            data = read_csv(dir + '/analysis' + '/zz_cell_analysis.csv')
            all_cell_images.append(cell_images)
            all_cell_masks.append(cell_masks)
            all_cell_data.append(data)


        return num_cell_dirs, all_cell_images, all_cell_masks, all_cell_data


    # open the images
    # load the analysis df