import glob
from skimage import io
import os
from pandas import read_csv


class Viewer():

    def __init__(self, directory):
        self.directory = directory

    # select cell number
    def select_cell_number(self):
        cell_analysis_dirs = glob.glob(f'{self.directory}/cell*')
        num_cell_dirs = len(cell_analysis_dirs)

        all_cell_images = []
        all_cell_masks = []
        all_cell_data = []
        all_cell_number = []

        for dir in cell_analysis_dirs:
            print(dir)
            cell_images = io.imread_collection(dir + '/_heatmap' + '/*.png')
            cell_masks = io.imread_collection(dir + '/_labelled' + '/*.png')
            cell_number = os.path.split(dir)[1]
            data = read_csv(dir + '/analysis' +
                            f'/{cell_number}_dataframe.csv')
            all_cell_images.append(cell_images)
            all_cell_masks.append(cell_masks)
            all_cell_data.append(data)
            all_cell_number.append(cell_number)

        return all_cell_number, all_cell_images, all_cell_masks, all_cell_data

    # open the images
    # load the analysis df
