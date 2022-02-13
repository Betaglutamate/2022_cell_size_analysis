from math import ceil, floor
import tkinter as tk
import os
import csv
from PIL import Image, ImageTk
from pathlib import Path
from tkinter import filedialog
from skimage import exposure
from analysis import Analysis
from view_analysis import Viewer
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte
from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self._create_buttons()
        self._createCanvasBinding()
        self._open_image_folder()
        self._initialize_image()
        


    def _initialize_image(self):
        self.loaded_image = []
        self.my_images = []

        for root, dirs, files in os.walk(self.directory, topdown=False):
            self.root = root
            for name in files:
                if "tif" in name:
                    file_name = (os.path.join(root, name)).replace("\\", "/")
                    self.loaded_image.append(file_name)

        # make coord folder to save coord and display img
        self.coord_folder = os.path.normpath(os.path.join(self.root, "coords"))
        Path(self.coord_folder).mkdir(parents=True, exist_ok=True)

        sample_image = io.imread(self.loaded_image[0])
        sample_image_path = os.path.normpath(
            os.path.join(self.coord_folder, "display_image.png"))

        plt.imsave(sample_image_path, arr=sample_image, cmap="Greys")

        self.my_images.append(tk.PhotoImage(file=(sample_image_path)))
        self.current_size = self.image_size=sample_image[0].size
        self.canvas.config(width=self.current_size, height=self.current_size)
        self.image_on_canvas = self.canvas.create_image(
            0, 0, anchor='nw', image=self.my_images[0])

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

    def _open_image_folder(self):
        self.directory = filedialog.askdirectory()
        self._initialize_image()

    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width=520, height=520, bg='white')
        self.canvas.grid(row=0, column=0, sticky='nsew', columnspan=5, rowspan=3)
    

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
            self.parent, text="Exit", width=20, pady=20, command=self.master.destroy)
        self.exit_button.grid(row=4, column=0)

        self.current_dir_button = tk.Button(
            self.parent, text="open images", width=20, pady=20, command=self._open_image_folder)
        self.current_dir_button.grid(row=4, column=1)

        self.open_analysis_window = tk.Button(self.parent, width=20, pady=20, bg="#88ffff",
             text ="Open Analysis",
             command = self.openAnalysisWindow)
        self.open_analysis_window.grid(row=4, column=2)


        ## analysis buttons

        self.analysis_button = tk.Button(
            self.parent, bg="#88ffff", text="Start analysis", width=20, pady=20, command=self.start_analysis)
        self.analysis_button.grid(row=0, column=6, columnspan=2)

        self.select_coord_forward = tk.Button(
            self.parent, bg="#882244", text="select next coord", width=20, pady=20, command=lambda: self.select_coord('forward'))
        self.select_coord_forward.grid(row=1, column=6)

        self.select_coord_backward = tk.Button(
            self.parent, bg="#882244", text="select previous coord", width=20, pady=20, command=lambda: self.select_coord('backward'))
        self.select_coord_backward.grid(row=1, column=7)

        

    def _createCanvasBinding(self):
        self.canvas.bind("<Button-1>", self.startRect)
        self.canvas.bind("<ButtonRelease-1>", self.stopRect)
        self.canvas.bind("<B1-Motion>", self.movingRect)

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

        with open(self.coord_file, 'a+', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            current_row = [os.path.split(self.directory)[-1], self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1] 
            writer.writerow(current_row)


        ## check for duplicates
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




    def display_coords(self):
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
        analysis = Analysis(self.root, self.coord_folder)

        analysis._load_images()
        analysis.create_subcells()
        analysis.calculate_cell_area()
    
    def select_cell_button_logic(self, direction):
        all_coords = []

        with open(os.path.join(self.coord_folder, 'coordinates.csv'), 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                    all_coords.append(row)
        
        ## select coordinate
        if direction == "forward":
            
            if self.current_row_index > len(all_coords)-1:
                self.current_row_index = 0
            current_row = all_coords[self.current_row_index]
            self.current_row_index = self.current_row_index + 1
        
        if direction == "backward":
            
            if self.current_row_index < 0:
                self.current_row_index = len(all_coords)-1
            elif self.current_row_index > len(all_coords)-1:
                self.current_row_index = self.current_row_index-1

            current_row = all_coords[self.current_row_index]
            self.current_row_index = self.current_row_index -1
        
        return current_row


    def select_coord(self, direction):

        current_row = self.select_cell_button_logic(direction)

        if self.current_coord_selected is not None:
            self.canvas.delete(self.current_coord_selected)

        self.current_coord_selected = self.canvas.create_rectangle(
            current_row[2], current_row[3], current_row[4], current_row[5], outline="#000000",  width=2)

        self.perform_sample_analysis(current_row)
    
    def perform_sample_analysis(self, current_row):
        img = io.imread(self.loaded_image[0])
        x1, y1, x2, y2 = current_row[2], current_row[3], current_row[4], current_row[5]
        x1 = int(float(x1))
        x2 = int(float(x2))
        y1 = int(float(y1))
        y2 = int(float(y2))
        
        if x1 > x2:
            x1_temp = x1
            x1 = x2
            x2 = x1_temp

        if y1 > y2:
            y1_temp = y1
            y1 = y2
            y2 = y1_temp
        
        cropped = img[y1:y2, x1:x2]

        single_analysis = Analysis(self.root, self.coord_folder, single_cell=cropped)
        max_area, labelled_img = single_analysis.measure_properties(cropped)
        current_analysis_image_path = os.path.join(self.coord_folder, "current_analysis.png")
        labelled_img_8bit = img_as_ubyte(labelled_img)

        io.imsave(current_analysis_image_path, labelled_img_8bit)


        if self.current_analysis_image_label is not None:
            self.current_analysis_image_label.destroy()

        current_analysis_image = (tk.PhotoImage(file=(current_analysis_image_path)))
        self.current_analysis_image_label = tk.Label(image=current_analysis_image)
        self.current_analysis_image_label.image = current_analysis_image # keep a reference!
        self.current_analysis_image_label.grid(row=2, column=6, columnspan=2)
    
    def openAnalysisWindow(self):
        #Create new anlysis window
        self.analysis_window = tk.Toplevel(self.master)
        self.analysis_window.title("New Window")
        self.analysis_window.geometry("600x600")
        self.dropdown = tk.StringVar(self.analysis_window)

        ##CREATE frame

        self.analysis_frame = tk.Frame(self.analysis_window, relief=tk.RAISED, borderwidth=1)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True)
        self.get_analysis_data()

    def get_analysis_data(self):
        #Get analysis data
        current_view = Viewer(self.directory)
        num_cell_dirs, self.all_cell_images, self.all_cell_masks, self.all_cell_data = current_view.select_cell_number()
        #Extract data to create widgets
        cell_name_list = []

        for i in range(num_cell_dirs):
            cell_name = f"cell_{i+1}"
            cell_name_list.append(cell_name)   
        self.dropdown.set(cell_name_list[0]) # default value

        cell_drop_down = tk.OptionMenu(self.analysis_frame, self.dropdown, *cell_name_list, command=self.update_cell_analysis)
        cell_drop_down.pack(side = tk.LEFT)

        
        self.place_analysis_images(self.all_cell_masks[0], self.all_cell_images[0])
        self.plot_matplotlib(self.all_cell_data[0], self.all_cell_images[0], self.all_cell_masks[0])
        

    def update_cell_analysis(self, new_val):

        current_number = int(new_val[-1])

        self.currently_selected_cell_images = self.all_cell_images[current_number]
        self.currently_selected_cell_masks = self.all_cell_masks[current_number]
        self.currently_selected_cell_data = self.all_cell_data[current_number]

        self.place_analysis_images(self.currently_selected_cell_masks, self.currently_selected_cell_images)
        self.plot_matplotlib(self.currently_selected_cell_data, self.currently_selected_cell_image, self.currently_selected_cell_masks)

    def place_analysis_images(self, cell_masks, cell_images):
            ### add current cell mask
        current_cell_mask = cell_masks[0]
        pi = Image.fromarray(current_cell_mask)
        (width, height) = (pi.width * 4, pi.height * 4)
        current_cell_mask_resized = pi.resize((width, height))

        self.current_cell_mask = ImageTk.PhotoImage(current_cell_mask_resized)
        self.matching_mask = tk.Label(self.analysis_frame, image=self.current_cell_mask)
        self.matching_mask.image = self.current_cell_mask # keep a reference!
        self.matching_mask.pack(side = tk.RIGHT)
        logarithmic_corrected = exposure.adjust_log(cell_images[0], 8)
        logarithmic_corrected = img_as_ubyte(logarithmic_corrected)

        pi = Image.fromarray(logarithmic_corrected)
        (width, height) = (pi.width * 4, pi.height * 4)
        current_cell_image_resized = pi.resize((width, height))

        self.current_cell_image = ImageTk.PhotoImage(current_cell_image_resized)
        self.matching_image = tk.Label(self.analysis_frame, image=self.current_cell_image)
        self.matching_image.image = self.current_cell_image # keep a reference!
        self.matching_image.pack(side = tk.RIGHT)

        
        
        ###Implement matplotlib figure

    def plot_matplotlib(self, data, cell_images, cell_masks):

        self.x_values, self.y_values = data['Time'], data['Area']
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot()
        self.line2, = ax.plot(self.x_values, self.y_values)
        lower_y, upper_y = ax.get_ylim()

        self.int_ly = int(floor(lower_y))
        self.int_uy = int(ceil(upper_y))
        self.y_values = range(self.int_ly,self.int_uy)
        self.x_values = [0]* len(range(self.int_ly,self.int_uy))

        ax.set_ylabel("Area [pixels]")
        ax.set_xlabel("frame")

        self.canvas_analysis = FigureCanvasTkAgg(fig, master=self.analysis_window)  # A tk.DrawingArea.
        self.canvas_analysis.draw()

        toolbar = NavigationToolbar2Tk(self.canvas_analysis, self.analysis_window, pack_toolbar=False)
        toolbar.update()

        self.canvas_analysis.mpl_connect(
            "key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas_analysis.mpl_connect("key_press_event", key_press_handler)

        button_quit = tk.Button(master=self.analysis_window, text="Quit", command=self.analysis_window.destroy)

        slider_update = tk.Scale(self.analysis_window, from_=0, to=len(cell_images)-1, orient=tk.HORIZONTAL,
                                    command=self.update_frequency, label="Frequency [Hz]")

        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        button_quit.pack(side=tk.BOTTOM)
        slider_update.pack(side=tk.BOTTOM)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_analysis.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

 
    def update_frequency(self, new_val):
            # retrieve frequency
            f = int(new_val)
            # update data
            self.x_values = [f]* len(range(self.int_ly, self.int_uy))
            self.line2.set_data(self.x_values, self.y_values)
            # required to update canvas and attached toolbar!
            self.canvas_analysis.draw()
        



