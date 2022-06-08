import skimage as ski
import numpy as np

test = ski.io.imread("Volume_short/20220120_volume video/masks/171824-0009.png")

a = test[...,0:3]

b = ski.color.rgb2gray(a)

bit = ski.img_as_ubyte(b)

ski.io.imshow(a)
ski.io.imshow(b)

ski.filters.threshold_otsu(bit)

x = bit >= 22

ski.io.imshow(x)


# thresh = threshold_otsu(new_im)        
# final_im = new_im < thresh

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


