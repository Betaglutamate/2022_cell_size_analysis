import skimage as ski
import numpy as np

test = ski.io.imread("Volume_short/20220120_volume video/masks/171824-0009.png")

test_array = np.empty((0, 4)) # 4 because I have four colour dimensions

for x, y, *c in test[:, :, :]:
    test_array = np.append(test_array, c, axis = 0)

unique_colours = np.unique(test_array, axis = 0)


list_of_cells = []

# Make mask of all perfectly red pixels
for colour in unique_colours:
    single_cell = np.all(test == colour, axis=-1)
    list_of_cells.append(single_cell)

ski.io.imshow(list_of_cells[0])





label_image = ski.measure.label(x)
test_label = ski.color.label2rgb(label_image, image=b, bg_label=0)
region_props = ski.measure.regionprops(label_image)


new_img = np.zeros(test[:,:,0].shape)

for pos in region_props:
    for obj in pos.coords:
        x, y = obj[0], obj[1]
        print(x, y)
        new_img[x, y] = 255

ski.io.imshow(new_img)









