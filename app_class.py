from math import ceil, floor
import tkinter as tk
import os
import numpy as np
import csv
from PIL import Image, ImageTk
from pathlib import Path
from tkinter import filedialog
from skimage import exposure
from analysis import Analysis
from view_analysis import Viewer
from gather_data import summarize_data
from matplotlib.pyplot import imsave
from skimage import io, img_as_ubyte
from skimage.exposure import rescale_intensity
from skimage.transform import rescale
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import threading
from cellpose_analysis import create_model, run_cellpose_segment, create_labelled_imgs


class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._open_image_folder()
        self._get_image_paths()
        self._createCanvas()
        self._create_buttons()
        self._initialize_image()
        self.finalize_canvas(sample_image_path=None)
        self.model = create_model()

        # I also start a thread to do cellpose calculations
        t = threading.Thread(target=self.background_task)
        self.stop_event = threading.Event()
        t.start()

    def background_task(self):
        '''This will run in the background and generate the images for scrolling through
        '''
        self._generate_heatmaps()
        os.system('notify-send "Heatmaps generated" "Task Complete"')

    
    def restart(self):
        import sys
        python = sys.executable
        os.execl(python, python, * sys.argv)


    def _get_image_paths(self):
        '''Here I collect all image names in the selected folder note I filter for tif
        '''
        all_image_paths = []

        for root, dirs, file in os.walk(self.directory):
            all_image_paths.extend(file)
            break
        self.root = root
        # make sure that the image paths are in correct time order
        all_image_paths.sort()
        self.all_filter_image_paths = []
        for image_path in all_image_paths:
            if 'tif' in image_path: #tif filter incase other file types
                self.all_filter_image_paths.append(image_path)

        # make coord folder to save coord and display img

        self.heatmap_folder = os.path.normpath(
            os.path.join(self.root, "heatmap"))
        self.masks_folder = os.path.normpath(
            os.path.join(self.root, "masks"))
        Path(self.heatmap_folder).mkdir(parents=True, exist_ok=True)
        Path(self.masks_folder).mkdir(parents=True, exist_ok=True)

    def _generate_heatmaps(self):
        i = 0
        for file in self.all_filter_image_paths:
            i = i+1
            self.rescale_images(os.path.join(file))
            print(
                f'converting image {i} out of {len(self.all_filter_image_paths)}')
            if self.stop_event.is_set():
                break

    def rescale_images(self, filename):

        if not os.path.exists(os.path.join(self.heatmap_folder, f'{filename.split(".")[0]}.png')):
            current_image = io.imread(os.path.join(self.root, filename))
            # ravel_image = np.sort(current_image.ravel())
            # cut_image = ravel_image[int(
            #     (len(current_image)*0.3)):-int((len(current_image)*0.3))]
            sample_image = rescale_intensity(current_image)
            imgs, masks = run_cellpose_segment(filename, self.model, self.directory)
            labelled_imgs = create_labelled_imgs(masks, imgs)
            save_file_path = os.path.normpath(
                os.path.join(self.heatmap_folder, f'{filename.split(".")[0]}.png'))
            save_file_path_masks = os.path.normpath(
                os.path.join(self.masks_folder, f'{filename.split(".")[0]}.png'))

            imsave(save_file_path, arr=labelled_imgs[0])
            imsave(save_file_path_masks, arr=masks[0])

    def _initialize_image(self):
        # make coord folder to save coord and display img
        self.coord_folder = os.path.normpath(os.path.join(self.root, "coords"))
        Path(self.coord_folder).mkdir(parents=True, exist_ok=True)

        self.loaded_image = io.imread(os.path.join(
            self.root, self.all_filter_image_paths[0]))
        sample_image = rescale_intensity(self.loaded_image)
        self.sample_image_path = os.path.normpath(
            os.path.join(self.coord_folder, "display_image.png"))

        imsave(self.sample_image_path, arr=sample_image)

        # path = 'bacteria-icon.png'  # place path to your image here

    def finalize_canvas(self, sample_image_path):
        if sample_image_path == None:
            try:
                self.image = Image.open(os.path.join(self.heatmap_folder, os.listdir(self.heatmap_folder)[0]))
            except IndexError:
                self.image = Image.open(self.sample_image_path)
        else:
            self.image = Image.open(sample_image_path)  # open image
        self.width, self.height = self.image.size
        self.container = self.canvas.create_rectangle(
            0, 0, self.width, self.height, width=0)

        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind("<Button-1>", self.startRect)
        self.canvas.bind("<ButtonRelease-1>", self.stopRect)
        self.canvas.bind("<B1-Motion>", self.movingRect)
        self.canvas.bind('<ButtonPress-3>', self.move_from)
        self.canvas.bind('<B3-Motion>',     self.move_to)
        self.canvas.bind("<Button-2>", self.reset_image)
        # with Windows and MacOS, but not Linux
        self.canvas.bind('<MouseWheel>', self.wheel)
        # only with Linux, wheel scroll down
        self.canvas.bind('<Button-5>',   self.wheel)
        # only with Linux, wheel scroll up
        self.canvas.bind('<Button-4>',   self.wheel)

        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image

        self.current_size = self.image.size
        self.canvas.config(width=self.width, height=self.height)

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def _createVariables(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None
        self.coords_shown = False
        self.current_row_index = 0
        self.current_coord_selected = None
        self.current_analysis_image_label = None
        self.counter = 0
        self.total_zoom = 1

    # added stuff
        

    def reset_image(self, event):
        self.total_zoom = 1
        self.canvas.destroy()
        self._createCanvas()
        self.finalize_canvas(sample_image_path=None)
        self.display_coords()
        self.image_slider.set(0)

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area

        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))

        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        # get coordinates (x1,y1,x2,y2) of the image tile
        x1 = max(bbox2[0] - bbox1[0], 0)
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            # sometimes it is larger on 1 pixel...
            x = min(int(x2 / self.imscale), self.width)
            # ...and sometimes not
            y = min(int(y2 / self.imscale), self.height)
            image = self.image.crop(
                (int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(
                image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            # keep an extra reference to prevent garbage-collection
            self.canvas.imagetk = imagetk

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area

        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        # rescale all canvas objects
        self.canvas.scale('all', x, y, scale, scale)

        self.total_zoom = self.total_zoom * scale
        self.show_image()

    def _open_image_folder(self):
        self.directory = filedialog.askdirectory(initialdir="/home/betaglutamate/OneDrive/00_PhD/00_Phd_data")


    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width=520, height=520, bg='white')
        self.canvas.grid(row=0, column=0, sticky='nsew',
                         columnspan=5, rowspan=3)

    def _create_buttons(self):
        #Button(root, text="1", padx=40, pady=20, command=lambda: enter_number(1))
        self.save_coords_button = tk.Button(
            self.parent, text="save coords", width=20, pady=20, command=self.save_coords)
        self.save_coords_button.grid(row=3, column=0)

        self.delete_coords_button = tk.Button(
            self.parent, text="delete coords", width=20, pady=20, command=self.delete_coords)
        self.delete_coords_button.grid(row=3, column=1)

        self.display_coords_button = tk.Button(
            self.parent, text="display coords", width=20, pady=20, command=self.display_coords)
        self.display_coords_button.grid(row=3, column=2)

        self.exit_button = tk.Button(
            self.parent, text="Exit", width=20, pady=20, command=self._quit_app)
        self.exit_button.grid(row=4, column=0)

        self.current_dir_button = tk.Button(
            self.parent, text="open images", width=20, pady=20, command=self.restart)
        self.current_dir_button.grid(row=4, column=1)

        self.open_analysis_window = tk.Button(self.parent, width=20, pady=20, bg="#88ffff",
                                              text="Open Analysis",
                                              command=self.openAnalysisWindow)
        self.open_analysis_window.grid(row=4, column=2)

        # analysis buttons

        self.analysis_button = tk.Button(
            self.parent, bg="#88ffff", text="Start analysis", width=20, pady=20, command=self.start_analysis)
        self.analysis_button.grid(row=0, column=6, columnspan=2)

        # picture slider

        self.image_slider = tk.Scale(self.parent, from_=0, to=len(
            self.all_filter_image_paths)-1, orient=tk.HORIZONTAL, command=self.switch_image)
        self.image_slider.grid(row=5, column=0, columnspan = 3, sticky='NSEW', padx=5)

    def switch_image(self, slider_value):
        png_file_paths = [x.replace("tif", "png")
                          for x in self.all_filter_image_paths]
        self.all_filter_image_paths[int(slider_value)]
        loaded_image_name = os.path.join(
            self.heatmap_folder, png_file_paths[int(slider_value)])
        self.finalize_canvas(loaded_image_name)
        self.show_image()
    
    def _quit_app(self):
        self.stop_event.set()
        self.quit()

    # I need to load all the images

    def startRect(self, event):
        # Translate mouse screen x0,y0 coordinates to canvas coordinates
        self.canvas.delete(self.rectid)
        self.rectx0 = self.canvas.canvasx(event.x)
        self.recty0 = self.canvas.canvasy(event.y)
        # Create rectangle
        self.rectid = self.canvas.create_rectangle(
            self.rectx0, self.recty0, self.rectx0, self.recty0, outline="#4eccde")

    def movingRect(self, event):
        # Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)

        # Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                           self.rectx1, self.recty1)

    def stopRect(self, event):
        """
        This function receives final rectangle coords
        """
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)
        # Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                           self.rectx1, self.recty1)

    def save_coords(self):
        self.coord_file = os.path.join(self.coord_folder, 'coordinates.csv')

        if self.rectid:
            bbox1 = self.canvas.coords(self.container)  # get image area
            bbox2 = self.canvas.coords(self.rectid)  # get roi area
            # get upper left corner (x1,y1)
            x1 = int((bbox2[0] - bbox1[0]) / self.total_zoom)
            y1 = int((bbox2[1] - bbox1[1]) / self.total_zoom)

            # you need to find the width and height to get x2 and y2
            bounds = self.canvas.bbox(self.rectid)
            width = bounds[2]-bounds[0]
            height = bounds[3] - bounds[1]
            # get bottom right corner (x2,y2)
            x2 = int(x1 + width/self.total_zoom)
            y2 = int(y1 + height/self.total_zoom)

        with open(self.coord_file, 'a+', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            current_row = [os.path.split(self.directory)[-1], self.rectid, x1, y1,
                           x2, y2]
            writer.writerow(current_row)

        # check for duplicates
        with open(self.coord_file, newline='', encoding='UTF8') as f:
            data = list(csv.reader(f))
            new_data = [a for i, a in enumerate(data) if a not in data[:i]]
        with open(self.coord_file, 'w', newline='', encoding='UTF8') as t:
            write = csv.writer(t)
            write.writerows(new_data)

        self.canvas.delete(self.rectid)

        if self.coords_shown:
            self.hide_coords()
            self.display_coords()

        self.reset_image(event=None)

    def display_coords(self):

        if self.total_zoom != 1:
            self.reset_image(event=None)

        self.coords_shown = True

        self.all_shown_rect = []

        with open(os.path.join(self.coord_folder, 'coordinates.csv'), 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                drawn_rect = self.canvas.create_rectangle(
                    row[2], row[3], row[4], row[5], outline="#ff22de",  width=2)
                self.all_shown_rect.append(drawn_rect)

        self.display_coords_button['text'] = "hide coords"
        self.display_coords_button['command'] = self.hide_coords

    def hide_coords(self):
        self.coords_shown = False

        for rect in self.all_shown_rect:
            self.canvas.delete(rect)

        self.display_coords_button['text'] = "display coords"
        self.display_coords_button['command'] = self.display_coords

    def delete_coords(self):

        # remove the last row of csv file

        with open(os.path.join(self.coord_folder, 'coordinates.csv'), 'r+', newline='', encoding='UTF8') as f:
            all_lines = f.read().splitlines()
            f.truncate(0)  # Deletes all current data

        with open(os.path.join(self.coord_folder, 'coordinates.csv'), 'a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            for row in all_lines[:-1]:  # I add the -1 so last line doesnt get copied
                split_row = row.split(',')
                writer.writerow(split_row)

        # call display coords.
        if self.coords_shown:
            self.hide_coords()

        self.display_coords()

    def start_analysis(self):
        analysis = Analysis(self.root, self.coord_folder, masks_folder = self.masks_folder, heatmap_folder = self.heatmap_folder)
        analysis._load_images()
        analysis.create_subcells()
        analysis.calculate_cell_area()
        os.system('notify-send "Analysis Complete" "Task Complete"')


        # run here

        summarize_data(self.root)


    def openAnalysisWindow(self):
        # Create new anlysis window
        self.analysis_window = tk.Toplevel(self.master)
        self.analysis_window.title("Analysis")
        self.analysis_window.geometry("1000x600")
        self.dropdown = tk.StringVar(self.analysis_window)

        # CREATE analysis variables

        self.matching_mask = None
        self.canvas_analysis = None
        self.toolbar = None
        self.current_analysis_image_label = None
        self.button_quit = None
        self.slider_update = None

        # CREATE frame

        self.analysis_frame = tk.Frame(
            self.analysis_window, relief=tk.RAISED, borderwidth=1)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True)
        self.get_analysis_data()

    def get_analysis_data(self):
        # Get analysis data
        current_view = Viewer(self.directory)
        self.all_cell_number, self.all_cell_images, self.all_cell_masks, self.all_cell_data = current_view.select_cell_number()
        # Extract data to create widgets
        cell_name_list = []

        for i in self.all_cell_number:
            cell_name = i
            cell_name_list.append(cell_name)
        self.dropdown.set(cell_name_list[0])  # default value

        cell_drop_down = tk.OptionMenu(
            self.analysis_frame, self.dropdown, *cell_name_list, command=self.update_cell_analysis)
        cell_drop_down.configure(width=20, height=5, bg="#03a9f4")
        cell_drop_down['menu'].config(bg="#03a9f4")
        cell_drop_down.pack(side=tk.LEFT)

        self.currently_selected_cell_images = self.all_cell_images[0]
        self.currently_selected_cell_masks = self.all_cell_masks[0]
        self.currently_selected_cell_data = self.all_cell_data[0]

        self.place_analysis_images(
            self.currently_selected_cell_masks, self.currently_selected_cell_images)
        self.plot_matplotlib(self.currently_selected_cell_data)

    def update_cell_analysis(self, new_val):

        current_number = int(self.all_cell_number.index(new_val))
        # then I subtract 1 because cell 1 is index 0

        # find index of new val in all_cell_number

        # find out how to make it work with double digits

        self.currently_selected_cell_images = self.all_cell_images[current_number]
        self.currently_selected_cell_masks = self.all_cell_masks[current_number]
        self.currently_selected_cell_data = self.all_cell_data[current_number]

        self.place_analysis_images(
            self.currently_selected_cell_masks, self.currently_selected_cell_images)
        self.plot_matplotlib(self.currently_selected_cell_data)

    def place_analysis_images(self, cell_masks, cell_images, current_image_number=0):
        # add current cell mask

        # remove previous cell label

        if self.matching_mask is not None:
            self.matching_mask.destroy()
            self.matching_image.destroy()

        current_cell_mask = cell_masks[current_image_number]
        pi = Image.fromarray(current_cell_mask)

        height = 600
        self.max_image_size = 200
        multiplier = 8

        while height > self.max_image_size:
            multiplier = multiplier - 1
            (width, height) = (pi.width * multiplier, pi.height * multiplier)

        current_cell_mask_resized = pi.resize((width, height))

        self.current_cell_mask = ImageTk.PhotoImage(current_cell_mask_resized)
        self.matching_mask = tk.Label(
            self.analysis_frame, image=self.current_cell_mask)
        self.matching_mask.image = self.current_cell_mask  # keep a reference!
        self.matching_mask.pack(side=tk.RIGHT)

        # place image

        logarithmic_corrected = exposure.rescale_intensity(
            cell_images[current_image_number])
        logarithmic_corrected = img_as_ubyte(logarithmic_corrected)

        pi = Image.fromarray(logarithmic_corrected)
        current_cell_image_resized = pi.resize((width, height))

        self.current_cell_image = ImageTk.PhotoImage(
            current_cell_image_resized)
        self.matching_image = tk.Label(
            self.analysis_frame, image=self.current_cell_image)
        self.matching_image.image = self.current_cell_image  # keep a reference!
        self.matching_image.pack(side=tk.RIGHT)

        # Implement matplotlib figure

    def plot_matplotlib(self, data):

        if self.canvas_analysis is not None:
            self.canvas_analysis.get_tk_widget().destroy()
            self.toolbar.destroy()
            self.button_quit.destroy()
            self.slider_update.destroy()

        self.x_values, self.y_values = data['Time'], data['Area']

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot()
        self.main_plot_image, = ax.plot(self.x_values, self.y_values)
        ax.set_ylim([data['Area'][0]*0.5, data['Area'][0]*1.25])

        lower_y, upper_y = ax.get_ylim()
        self.int_ly = int(floor(lower_y))
        self.int_uy = int(ceil(upper_y))
        self.y_values_vline = range(self.int_ly, self.int_uy)
        self.x_values_vline = [0] * len(range(self.int_ly, self.int_uy))
        self.line2, = ax.plot(self.x_values_vline, self.y_values_vline)

        ax.set_ylabel("Area [pixels]")
        ax.set_xlabel("frame")

        # A tk.DrawingArea.
        self.canvas_analysis = FigureCanvasTkAgg(
            fig, master=self.analysis_window)
        self.canvas_analysis.draw()

        self.toolbar = NavigationToolbar2Tk(
            self.canvas_analysis, self.analysis_window, pack_toolbar=False)
        self.toolbar.update()

        self.canvas_analysis.mpl_connect(
            "key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas_analysis.mpl_connect("key_press_event", key_press_handler)

        self.button_quit = tk.Button(master=self.analysis_window, text="Quit",
                                     command=self.analysis_window.destroy, bg='#03a9f4', pady=20, padx=40)

        self.slider_update = tk.Scale(self.analysis_window, from_=0, to=len(data)-1, orient=tk.HORIZONTAL,
                                      command=self.update_frequency, label="Frame Number")

        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        self.button_quit.pack(side=tk.BOTTOM)
        self.slider_update.pack(side=tk.BOTTOM)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_analysis.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_frequency(self, new_val):
        # retrieve frequency
        current_slider_val = int(new_val)
        # update data
        self.x_values = [current_slider_val] * \
            len(range(self.int_ly, self.int_uy))

        self.y_values_vline = range(self.int_ly, self.int_uy)
        self.line2.set_data(self.x_values, self.y_values_vline)
        # required to update canvas and attached toolbar!
        self.canvas_analysis.draw()

        # update images

        self.place_analysis_images(self.currently_selected_cell_masks,
                                   self.currently_selected_cell_images, current_slider_val)
