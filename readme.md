# Cell size analyser

## dependencies
matplotlib
skimage
pandas

## quick start
1. clone repository
2. install dependencies
3. run 'python main_app.py'
4. select folder containing tif microscopy images
5. drop and drag on the screen of the cell you want to analyse
6. click save coord to add the coordinate to analysis
7. use hide show coordinate to display cells select for analysis
8. once you have selected all the cells click start analysis

## output
you will receive a new subfolder for each cell you are analysing. In it you get the cropped cell image a _labelled folder showing the predicted cell using Otsu thresholding. The analysis folder contains a csv frame showing the estimate cell area in pixels based on the _labelled image. Time corresponds to image number so needs to be multiplied by acquisition speed to get the actual time in seconds.



