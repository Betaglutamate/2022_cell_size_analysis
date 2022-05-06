import matplotlib.pyplot as plt
from skimage.color import rgb2gray
import skimage as sk
import numpy as np
#image: https://live.staticflickr.com/2456/3854685038_48bc4c8b02_z.jpgpng



import cv2
import matplotlib.pyplot as plt
import numpy as np
img = cv2.imread("Volume_videos/20220120_volume video/cell_1/cell_1_id14140_0.png")
img = cv2.resize(img,(512,512))

gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
_,thresh = cv2.threshold(gray, np.mean(gray), 255, cv2.THRESH_BINARY_INV)
edges = cv2.dilate(cv2.Canny(thresh,0,255),None)


cnt = sorted(cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2], key=cv2.contourArea)[-1]
mask = np.zeros((512,512), np.uint8)
masked = cv2.drawContours(mask, [cnt],-1, 255, -1)

dst = cv2.bitwise_and(img, img, mask=mask)
segmented = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

sk.io.imshow(segmented)
sk.io.imshow(masked)

