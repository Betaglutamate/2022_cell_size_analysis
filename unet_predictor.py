import keras
import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt
import keras

reconstructed_model = keras.models.load_model("unet_folder/saved_unet")

test_image = tiff.imread('Volume_videos/20220120_volume video/171822-0000.tif')


a = np.array([test_image, test_image])
final = np.expand_dims(a, 0)
b = np.swapaxes(final,1,3)
ok_now = np.swapaxes(b,0,3)
y_pred=reconstructed_model.predict(ok_now)
plt.imshow(np.squeeze(y_pred[0]))