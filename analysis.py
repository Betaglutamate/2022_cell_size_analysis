from skimage import io, img_as_ubyte
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.exposure import rescale_intensity
from skimage.color import label2rgb
from skimage.restoration import denoise_nl_means, estimate_sigma
import os
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
import pandas as pd


class Analysis():
    def __init__(self, path, coord_folder, **kwargs):
        self.path = path
        self.coord_folder = coord_folder
        # self._load_images()
        # self.create_subcells()
        # self.calculate_cell_area()
        self.single_image = kwargs.get('single_cell')

    def _load_images(self):
        self.img_collection = io.imread_collection(
            os.path.normpath(self.path + '/*.tif'))

    def create_subcells(self):
        # load images into sk ima
        self.cell_save_paths = []
        self.cell_save_paths_labelled = []
        subcell_dict = {}

        with open(os.path.normpath(os.path.join(self.coord_folder, 'coordinates.csv')), 'r') as file:
            reader = csv.reader(file)
            for num, row in enumerate(reader):
                print(f"processing {row}")
                coord = [row[2], row[3], row[4], row[5]]
                subcell_dict[str(row[1] + str(num))] = coord
        # load coordinates
        # crop
        enumerator = 0

        for k, v in subcell_dict.items():
            x1, y1, x2, y2 = subcell_dict[k]
            x1 = int(float(x1))
            x2 = int(float(x2))
            y1 = int(float(y1))
            y2 = int(float(y2))

            # logic to check that coords are in correct order
            if x1 > x2:
                x1_temp = x1
                x1 = x2
                x2 = x1_temp

            if y1 > y2:
                y1_temp = y1
                y1 = y2
                y2 = y1_temp

            enumerator = enumerator + 1

            cell_save_path = os.path.join(self.path, f"cell_{enumerator}")

            Path(cell_save_path).mkdir(parents=True, exist_ok=True)

            cell_path_labelled = os.path.join(cell_save_path, "_labelled")

            Path(cell_path_labelled).mkdir(parents=True, exist_ok=True)

            self.cell_save_paths.append(cell_save_path)
            self.cell_save_paths_labelled.append(cell_path_labelled)

            for num, image in enumerate(self.img_collection):
                cropped = image[y1:y2, x1:x2]
                io.imsave(os.path.join(
                    cell_save_path, f"cell_{enumerator}_id{k}_{num}.png"), cropped, check_contrast=False)

            print("finished_processing")

    def calculate_cell_area(self):
        '''
        This function takes a cell subfolder and applies measure properties
        '''
        for path, label_path in zip(self.cell_save_paths, self.cell_save_paths_labelled):
            cell_collection = io.imread_collection(
                os.path.normpath(path + '/*.png'))

            time_list = []
            area_list = []

            for num, image in enumerate(cell_collection):
                area, label_image = self.measure_properties(image)
                time_list.append(num)
                area_list.append(area)
                label_img_8bit = img_as_ubyte(label_image)
                io.imsave(os.path.join(
                    label_path, f"label_image_{num}.png"), label_img_8bit, check_contrast=False)

            # Make analysis path
            Path(os.path.normpath(os.path.join(path, "analysis"))).mkdir(
                parents=True, exist_ok=True)

            # plot size over time
            fig, ax = plt.subplots()
            ax.scatter(x=time_list, y=area_list)
            plt.savefig(os.path.normpath(os.path.join(
                path, "analysis", "zz_cellplot.png")))

            analysis_df = pd.DataFrame({"Time": time_list, "Area": area_list})
            analysis_df.to_csv(os.path.normpath(os.path.join(
                path, "analysis", "zz_cell_analysis.csv")))

    def measure_properties(self, image):
        '''
        extracts the area of largest object in
            image by applying otsu threshold then measuring
            regions
        '''
        d_img = self.denoise_img(image)
        d_img = rescale_intensity(d_img)
        thresh = threshold_otsu(d_img)
        binary = d_img < thresh
        label_im = label(binary)
        clusters = regionprops(label_im, d_img)

        filtered_list = []
        max_area_list = []
        for point in clusters:
            filtered_list.append(point)
            max_area_list.append(point.area)

        # find largest area
        probably_cell = max_area_list.index(max(max_area_list))

        obj_coords = []
        for obj in filtered_list:
            obj_coords.append(obj.coords)

        new_img = np.zeros(d_img.shape)

        for pos in obj_coords[probably_cell]:
            x, y = pos[0], pos[1]
            new_img[x, y] = 255

        labelled_img, labels = ndimage.label(new_img)
        labelled_img = label2rgb(labelled_img, bg_label=0)

        # save new image here

        max_area = max_area_list[probably_cell]
        return max_area, labelled_img

    def denoise_img(self, img):
        """estimate the noise standard deviation from the noisy image"""
        sigma_est = np.mean(
            estimate_sigma(img, channel_axis=True))

        patch_kw = dict(patch_size=1,      # 5x5 patches
                        patch_distance=2)

        # slow algorithm
        denoise = denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True,
                                                   **patch_kw)

        return denoise
