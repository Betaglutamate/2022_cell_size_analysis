import tkinter as tk
import os
import csv
from tkinter import filedialog
from analysis import Analysis

class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self._create_buttons()
        self._createCanvasBinding()
        self._open_image_folder()
        self._initialize_image()
        self.coords_shown = False


    def _initialize_image(self):
        self.loaded_image = []
        self.my_images = []

        for root, dirs, files in os.walk(self.directory, topdown=False):
            self.root = root
            for name in files:
                if "csv" not in name: 
                    file_name = (os.path.join(root, name)).replace("\\","/")
                    self.loaded_image.append(file_name)

        self.my_images.append(tk.PhotoImage(file=self.loaded_image[0]))
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.my_images[0])

    def start_analysis(self):
        analysis = Analysis(self.root)
        print(analysis.path)

    def _createVariables(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None

    def _open_image_folder(self):
        self.directory = filedialog.askdirectory()


    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width = 600, height = 600)
        self.canvas.grid(row=0, column=0, sticky='nsew', columnspan=5)

    def _create_buttons(self):
        #Button(root, text="1", padx=40, pady=20, command=lambda: enter_number(1))
        self.save_coords_button = tk.Button(self.parent, text="save_coords", padx=40, pady=20, command=self.save_coords)
        self.save_coords_button.grid(row=1, column=0)

        self.current_dir_button = tk.Button(self.parent, text="open images", padx=40, pady=20, command=self._open_image_folder)
        self.current_dir_button.grid(row=1, column=1)

        self.delete_coords_button = tk.Button(self.parent, text="delete coords", padx=40, pady=20, command=self.delete_coords)
        self.delete_coords_button.grid(row=1, column=2)

        self.display_coords_button = tk.Button(self.parent, text="display coords", padx=40, pady=20, command=self.display_coords)
        self.display_coords_button.grid(row=1, column=3)

        self.exit_button = tk.Button(self.parent, text="Exit", padx=40, pady=20, command=self.master.destroy)
        self.exit_button.grid(row=1, column=4)

        self.exit_button = tk.Button(self.parent, bg="#882244", text="Start_analysis", padx=40, pady=20, command=self.start_analysis)
        self.exit_button.grid(row=0, column=6)

    def _createCanvasBinding(self):
        self.canvas.bind( "<Button-1>", self.startRect )
        self.canvas.bind( "<ButtonRelease-1>", self.stopRect )
        self.canvas.bind( "<B1-Motion>", self.movingRect )

    def startRect(self, event):
        #Translate mouse screen x0,y0 coordinates to canvas coordinates
        self.canvas.delete(self.rectid)
        self.rectx0 = self.canvas.canvasx(event.x)
        self.recty0 = self.canvas.canvasy(event.y) 
        #Create rectangle
        self.rectid = self.canvas.create_rectangle(
            self.rectx0, self.recty0, self.rectx0, self.recty0, outline="#4eccde")
        print('Rectangle {0} started at {1} {2} {3} {4} '.
              format(self.rectid, self.rectx0, self.recty0, self.rectx0,
                     self.recty0))

    def movingRect(self, event):
        #Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)
        #Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1)
        print('Rectangle x1, y1 = ', self.rectx1, self.recty1)

    def stopRect(self, event):
        #Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.canvas.canvasx(event.x)
        self.recty1 = self.canvas.canvasy(event.y)
        #Modify rectangle x1, y1 coordinates
        self.canvas.coords(self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1)
        print('Rectangle ended')
    
    def save_coords(self):
        with open(os.path.join(self.root, 'coordinates.csv'), 'a', newline='', encoding='UTF8') as f:
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
        
        with open(os.path.join(self.root, 'coordinates.csv'), 'r') as file:
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

        #remove the last row of csv file

        with open(os.path.join(self.root, 'coordinates.csv'), 'r+', newline='', encoding='UTF8') as f:
            all_lines = f.read().splitlines()
            f.truncate(0) #Deletes all current data

        with open(os.path.join(self.root, 'coordinates.csv'), 'a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            for row in all_lines[:-1]: #I add the -1 so last line doesnt get copied
                split_row = row.split(',')
                writer.writerow(split_row)

        #call display coords.
        if self.coords_shown:
            self.hide_coords()

        
        self.display_coords()
        #add if to see if coords already displayed
        #self.display_coords()