import skimage as ski
import os
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
import seaborn as sns



class Analysis():
    def __init__(self, path):
        self.path = path
        self._load_images()
        self.create_subcells()
        self.calculate_cell_area()

    def _load_images(self):
        self.img_collection = ski.io.imread_collection(os.path.normpath(self.path + '/*.tif'))


    def create_subcells(self):
        #load images into sk ima
        self.cell_save_paths = []
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

            ##logic to check that coords are in correct order
            if x1>x2:
                x1_temp = x1
                x1 = x2
                x2 = x1_temp
            
            if y1>y2:
                y1_temp = y1
                y1 = y2
                y2 = y1_temp


            enumerator = enumerator + 1

            cell_save_path = os.path.join(self.path, f"cell_{enumerator}")

            Path(cell_save_path).mkdir(parents=True, exist_ok=True)

            self.cell_save_paths.append(cell_save_path)
            
            for num, image in enumerate(self.img_collection):
                cropped=image[y1:y2, x1:x2]
                ski.io.imsave(os.path.join(cell_save_path, f"cell_{enumerator}_id{k}_{num}.png"), cropped, check_contrast=False)
                

    def calculate_cell_area(self):
        '''
        This function takes a cell subfolder and applies measure properties
        '''
        for path in self.cell_save_paths:
            cell_collection = ski.io.imread_collection(os.path.normpath(path + '/*.png'))

            time_list = []
            area_list = []

            for num, image in enumerate(cell_collection):
                area = self.measure_properties(image)
                time_list.append(num)
                area_list.append(area)
            
            fig, ax = plt.subplots()
            sns.scatterplot(ax=ax, x=time_list, y= area_list)
            plt.savefig(os.path.join(path, "cellplot.png"))
                
        



    def measure_properties(self, image):
        '''
        extracts the area of largest object in
            image by applying otsu threshold then measuring
            regions
        '''
        d_img = self.denoise_img(image)
        thresh = ski.filters.threshold_otsu(d_img)
        binary = d_img < thresh
        label_im = ski.measure.label(binary)
        clusters = ski.measure.regionprops(label_im, d_img)

        filtered_list = []
        max_area_list = []
        for point in clusters:
            filtered_list.append(point)
            max_area_list.append(point.area)

        #find largest area
        probably_cell = max_area_list.index(max(max_area_list))

        obj_coords = []
        for obj in filtered_list:
            obj_coords.append(obj.coords)
    
        new_img = np.zeros(d_img.shape)

        for pos in obj_coords[probably_cell]:
                x, y = pos[0], pos[1]
                new_img[x, y] = 255

        labelled_img, labels = ndimage.label(new_img)
        labelled_img = ski.color.label2rgb(labelled_img, bg_label = 0)

        ##save new image here

        max_area = max_area_list[probably_cell]
        return max_area

    def denoise_img(self, img):
        """estimate the noise standard deviation from the noisy image"""
        sigma_est = np.mean(ski.restoration.estimate_sigma(img, channel_axis=True))
        print(f"estimated noise standard deviation = {sigma_est}")

        patch_kw = dict(patch_size=1,      # 5x5 patches
                        patch_distance=2,  # 13x13 search area
                        multichannel=False)

        # slow algorithm
        denoise = ski.restoration.denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True,
                                **patch_kw)
        
        return denoise













# edges1 = ski.feature.canny(binary)
# edges2 = ski.feature.canny(binary, sigma=3)

# fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(8, 3))

# ax[0].imshow(test, cmap='gray')
# ax[0].set_title('noisy image', fontsize=20)

# ax[1].imshow(edges1, cmap='gray')
# ax[1].set_title(r'Canny filter, $\sigma=1$', fontsize=20)

# ax[2].imshow(edges2, cmap='gray')
# ax[2].set_title(r'Canny filter, $\sigma=3$', fontsize=20)



