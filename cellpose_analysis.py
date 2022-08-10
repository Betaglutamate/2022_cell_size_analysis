import numpy as np
from cellpose import models, io, utils
import os
from skimage import color, exposure
from skimage.io import imshow

def create_model():
    '''Here I load the desired cellpose_model stored under cellpose_model_folder, if gpu acceleration is
    desired then switch gpu to true make sure that you have torch gpu installed'''
    model = models.CellposeModel(pretrained_model='cellpose_model/CHR_skinny_new', gpu=True)
    return model

def run_cellpose_segment(filename, model, directory):
    '''This function takes the directory and cellpose model and returns
    masks_flow and styles
    '''
    files = [filename]
    imgs = [io.imread(os.path.join(directory, f)) for f in files]
    imgs = [exposure.rescale_intensity(img) for img in imgs]

    channels = [[0,0]] #0, 0 means grayscale image

    masks, flows, styles = model.eval(imgs, diameter=None, channels=channels, compute_masks=True)

    #from scipy.ndimage import find_objects
    #find_objects(masks[0])

    #outlines = utils.outlines_list(masks[0])
    
    return imgs, masks

def create_labelled_imgs(masks, imgs):
    zip_masks = zip(imgs, masks)
    labelled_images = [color.label2rgb(mask, img, alpha = 0.2) for img, mask in zip_masks]
    return labelled_images


    # test_im = imgs[0]
    # test_mask = masks[0]

    # from skimage import segmentation
    # from skimage.io import imsave as sk_imsave
    # from skimage.io import imshow as sk_imshow
    # result_image = segmentation.mark_boundaries(test_im, test_mask, mode='outer')
    # plt.imshow(result_image)

    
    # test_im = exposure.rescale_intensity(test_im)
    # result_image = color.label2rgb(test_mask, test_im, alpha = 0.2)
    # sk_imsave("test.png", result_image)    
    # sk_imshow(result_image)
    # plt.imshow(result_image)
    # plt.imshow(test_im)
    # plt.imshow(test_mask)


