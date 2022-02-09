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
        enumerator = 0

        for k, v in subcell_dict.items():
            x1, y1, x2, y2 = subcell_dict[k]
            x1 = int(float(x1))
            x2 = int(float(x2))
            y1 = int(float(y1))
            y2 = int(float(y2))

            enumerator = enumerator + 1

            cell_save_path = os.path.join(self.path, f"cell_{enumerator}")

            Path(cell_save_path).mkdir(parents=True, exist_ok=True)

            for num, image in enumerate(self.img_collection):
                cropped=image[y1:y2, x1:x2]
                ski.io.imsave(os.path.join(cell_save_path, f"cell_{enumerator}_id{k}_{num}.png"), cropped)
                


test = ski.io.imread("test_images/cell_1/cell_1_id3_2.png")



import matplotlib.pyplot as plt
from skimage.filters import try_all_threshold
import numpy as np


fig, ax = try_all_threshold(invert, figsize=(10, 8), verbose=False)
plt.show()

test_8bit = ski.img_as_ubyte(test)

plt.hist(invert.ravel(), bins = 20)


invert = np.invert(test_8bit)

thresh = ski.filters.threshold_mean(invert)
binary = invert > thresh

plt.imshow(binary)



edges1 = ski.feature.canny(binary)
edges2 = ski.feature.canny(binary, sigma=3)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(8, 3))

ax[0].imshow(test, cmap='gray')
ax[0].set_title('noisy image', fontsize=20)

ax[1].imshow(edges1, cmap='gray')
ax[1].set_title(r'Canny filter, $\sigma=1$', fontsize=20)

ax[2].imshow(edges2, cmap='gray')
ax[2].set_title(r'Canny filter, $\sigma=3$', fontsize=20)


label_im = ski.measure.label(edges2)

clusters = ski.measure.regionprops(label_im, invert)