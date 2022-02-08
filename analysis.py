import skimage as ski
import os
import csv
from pathlib import Path


class Analysis():
    def __init__(self, path):
        self.path = path
        self._load_images()

    def _load_images(self):
        self.img_collection = ski.io.imread_collection(os.path.normpath(self.path + '/*.tif'))


    def create_subcells(self):
        #load images into sk image

        subcell_dict = {}

        with open(os.path.normpath(self.path + '/coordinates.csv'), 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                coord =  [row[2], row[3], row[4], row[5]]
                subcell_dict[str(row[1])] = coord
        #load coordinates
        #crop

        for k, v in subcell_dict.items():
            x1, y1, x2, y2 = subcell_dict[k]
            x1 = int(float(x1))
            x2 = int(float(x2))
            y1 = int(float(y1))
            y2 = int(float(y2))

            cell_save_path = os.path.join(self.path, f"cell_{k}")

            Path(cell_save_path).mkdir(parents=True, exist_ok=True)

            for num, image in enumerate(self.img_collection):
                cropped=image[y1:y2, x1:x2]
                ski.io.imsave(os.path.join(cell_save_path, f"cell_{k}_{num}.png"), cropped)
                


