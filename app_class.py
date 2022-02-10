import tkinter as tk
import os
import csv
from pathlib import Path
from tkinter import filedialog
from analysis import Analysis
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte



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

    def _open_image_folder(self):
        self.directory = filedialog.askdirectory()
        self._initialize_image()

    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width=600, height=600)
        self.canvas.grid(row=0, column=0, sticky='nsew', columnspan=5)
    
    def _createCanvas_analysis(self):
        self.canvas2 = tk.Canvas(self.parent, bg='#ffffff', width=50, height=50)
        self.canvas2.grid(row=2, column=0, sticky='nsew')

    def _create_buttons(self):
        #Button(root, text="1", padx=40, pady=20, command=lambda: enter_number(1))
        self.save_coords_button = tk.Button(
            self.parent, text="save_coords", padx=40, pady=20, command=self.save_coords)
        self.save_coords_button.grid(row=1, column=0)

        self.current_dir_button = tk.Button(
            self.parent, text="open images", padx=40, pady=20, command=self._open_image_folder)
        self.current_dir_button.grid(row=1, column=1)

        self.delete_coords_button = tk.Button(
            self.parent, text="delete coords", padx=40, pady=20, command=self.delete_coords)
        self.delete_coords_button.grid(row=1, column=2)

        self.display_coords_button = tk.Button(
            self.parent, text="display coords", padx=40, pady=20, command=self.display_coords)
        self.display_coords_button.grid(row=1, column=3)

        self.exit_button = tk.Button(
            self.parent, text="Exit", padx=40, pady=20, command=self.master.destroy)
        self.exit_button.grid(row=1, column=4)

        self.analysis_button = tk.Button(
            self.parent, bg="#882244", text="Start_analysis", padx=40, pady=20, command=self.start_analysis)
        self.analysis_button.grid(row=0, column=6, columnspan=2)

        self.select_coord_forward = tk.Button(
            self.parent, bg="#882244", text="select_next_coord", padx=40, pady=20, command=lambda: self.select_coord('forward'))
        self.select_coord_forward.grid(row=1, column=6)

        self.select_coord_backward = tk.Button(
            self.parent, bg="#882244", text="select_previous_coord", padx=40, pady=20, command=lambda: self.select_coord('backward'))
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
        print('Rectangle {0} started at {1} {2} {3} {4} '.
              format(self.rectid, self.rectx0, self.recty0, self.rectx0,
                     self.recty0))

    def movingRect(self, event):
        # Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)
        # Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                           self.rectx1, self.recty1)
        print('Rectangle x1, y1 = ', self.rectx1, self.recty1)

    def stopRect(self, event):
        # Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)
        # Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                           self.rectx1, self.recty1)
        print('Rectangle ended')

    def save_coords(self):
        with open(os.path.join(self.coord_folder, 'coordinates.csv'), 'a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([os.path.split(self.directory)[-1], self.rectid, self.rectx0, self.recty0,
                             self.rectx1, self.recty1])
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
            print(self.current_row_index)
            print("going forward")
            
            if self.current_row_index > len(all_coords)-1:
                self.current_row_index = 0
            current_row = all_coords[self.current_row_index]
            self.current_row_index = self.current_row_index + 1
            print(self.current_row_index)
        
        if direction == "backward":
            print(self.current_row_index)
            print("going backward")
            
            if self.current_row_index < 0:
                self.current_row_index = len(all_coords)-1
            elif self.current_row_index > len(all_coords)-1:
                self.current_row_index = self.current_row_index-1

            current_row = all_coords[self.current_row_index]
            self.current_row_index = self.current_row_index -1
            print(self.current_row_index)
        
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

        # self._createCanvas_analysis()
        
        current_analysis_photo = (tk.PhotoImage(file=(current_analysis_image_path)))

        # self.current_analysis = self.canvas2.create_image(
        #     (0, 0), anchor='nw', image=current_analysis_photo)

        photo = (tk.PhotoImage(file=(current_analysis_image_path)))

        label = tk.Label(image=photo)
        label.image = photo # keep a reference!
        label.grid(row=3, column=0)

    # 3. display image on main widget
