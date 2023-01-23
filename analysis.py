from skimage import io, img_as_ubyte
from skimage.measure import label, regionprops
from skimage.color import label2rgb, rgb2gray
from skimage.restoration import denoise_nl_means, estimate_sigma
import os
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
import pandas as pd


class Analysis():
    def __init__(self, path, coord_folder, masks_folder, heatmap_folder, **kwargs):
        self.path = path
        self.masks = masks_folder
        self.heatmap = heatmap_folder
        self.coord_folder = coord_folder
        self.single_image = kwargs.get('single_cell')

    def _load_images(self):
        self.img_collection = io.imread_collection(
            os.path.normpath(self.masks + '/*.png'))
        print(self.path)
        self.heatmap_collection = io.imread_collection(
            os.path.normpath(self.heatmap + '/*.png'))

    def create_subcells(self):
        # load images into sk ima
        self.cell_save_paths = []
        self.cell_save_paths_labelled = []
        self.cell_save_paths_heatmap = []
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

            cell_path_heatmap = os.path.join(cell_save_path, "_heatmap")
            Path(cell_path_heatmap).mkdir(parents=True, exist_ok=True)

            self.cell_save_paths.append(cell_save_path)
            self.cell_save_paths_labelled.append(cell_path_labelled)
            self.cell_save_paths_heatmap.append(cell_path_heatmap)


            for num, image in enumerate(self.img_collection):
                cropped = image[y1:y2, x1:x2]
                cropped = img_as_ubyte(cropped)
                io.imsave(os.path.join(
                    cell_save_path, f"cell_{enumerator}_id{k}_{num}.png"), cropped, check_contrast=False)
            
            for num, image in enumerate(self.heatmap_collection):
                cropped = image[y1:y2, x1:x2]
                cropped = img_as_ubyte(cropped)
                io.imsave(os.path.join(
                    cell_path_heatmap, f"cell_{enumerator}_id{k}_{num}.png"), cropped, check_contrast=False)

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
            length_list = []
            width_list = []
            orientation_list = []

            # Try calculating threshold based on first image only

            for num, image in enumerate(cell_collection):
                area, label_image, length, width, orientation = self.measure_properties(image)
                time_list.append(num)
                area_list.append(area)
                length_list.append(length)
                width_list.append(width)
                orientation_list.append(orientation)
                label_img_8bit = label_image.astype(np.uint8) * 255
                
                io.imsave(os.path.join(
                    label_path, f"label_image_{num}.png"), label_img_8bit, check_contrast=False)

            # Make analysis path
            Path(os.path.normpath(os.path.join(path, "analysis"))).mkdir(
                parents=True, exist_ok=True)

            # get cell number name
            cell_number = os.path.split(path)[1]

            # plot size over time

            fig, ax = plt.subplots()
            ax.scatter(x=time_list, y=area_list)
            ax.set(ylim=[min(area_list)-20, max(area_list)+20])
            plt.savefig(os.path.normpath(os.path.join(
                path, "analysis", f"{cell_number}_cellplot.png")))

            plt.close()
            analysis_df = pd.DataFrame({"Time": time_list, "Area": area_list, "Length": length_list, "Width": width_list, "Orientation": orientation_list})
            analysis_df.to_csv(os.path.normpath(os.path.join(
                path, "analysis", f"{cell_number}_dataframe.csv")))

    def measure_properties(self, image):
        '''
        extracts the area of largest object in
            image by applying otsu threshold then measuring
            regions
        '''

        color_array = np.empty((0, 4)) # 4 because I have four colour dimensions

        for x, y, *c in image[:, :, :]:
            color_array = np.append(color_array, c, axis = 0)

        unique_colours = np.unique(color_array, axis = 0).tolist()
        backg = [68,1,84,255] # This is the bg color given to cellpose images
        new_unique_colours = []

        for col in unique_colours:
            if col != backg:
                new_unique_colours.append(col)

        list_of_cells = []
        for colour in new_unique_colours:
            single_cell = np.all(image == colour, axis=-1)
            list_of_cells.append(single_cell)


        all_areas = []
        all_axis_length = []
        all_axis_width = []
        all_orientation = []
        all_labels = []

        if list_of_cells:
            for single_mask in list_of_cells:
                    self.label_image = label(single_mask)
                    region_props = regionprops(self.label_image)
                    self.area = region_props[0].area
                    self.cell_length = region_props[0].axis_major_length
                    self.cell_width = region_props[0].axis_minor_length
                    self.cell_orientation = region_props[0].orientation
                    self.cell_orientation = self.cell_orientation * (180/np.pi) + 90 
                    
                    all_areas.append(self.area)
                    all_axis_length.append(self.cell_length)
                    all_axis_width.append(self.cell_width)
                    all_orientation.append(self.cell_orientation)
                    all_labels.append(self.label_image)
            self.copy_list=list_of_cells

        
        else: #Sometimes cellpose fails to generate mask for image. If this happens I use the last stored values
            for single_mask in self.copy_list:
                    self.label_image = label(single_mask)
                    region_props = regionprops(self.label_image)

                    self.area = region_props[0].area
                    self.cell_length = region_props[0].axis_major_length
                    self.cell_width = region_props[0].axis_minor_length
                    
                    all_areas.append(self.area)
                    all_axis_length.append(self.cell_length)
                    all_axis_width.append(self.cell_width)
                    all_labels.append(self.label_image)

        max_value = max(all_areas) 
        max_index = all_areas.index(max_value) 
        self.max_area = all_areas[max_index]
        self.max_length = all_axis_length[max_index]
        self.max_width = all_axis_width[max_index]
        try:
            self.max_orientation = all_orientation[max_index]
        except IndexError:
            print("index error")
            self.max_orientation = float('nan')
        self.new_img = all_labels[max_index]

        return self.max_area, self.new_img, self.max_length, self.max_width, self.max_orientation


        


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
