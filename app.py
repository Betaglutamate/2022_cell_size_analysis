from fileinput import filename
import tkinter as tk
import csv
from PIL import Image, ImageTk, ImageEnhance
from click import command
import os
from tkinter import filedialog



class App(tk.Frame):
    def __init__( self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self._create_buttons()
        self._createCanvasBinding()
        self._open_image_folder()

        self.loaded_image = []
        self.my_images = []

        for root, dirs, files in os.walk(self.directory, topdown=False):
            for name in files:
                file_name = (os.path.join(root, name)).replace("\\","/")
                self.loaded_image.append(file_name)
        
        self.my_images.append(tk.PhotoImage(file=self.loaded_image[0]))
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.my_images[0])

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
        self.canvas.grid(row=0, column=0, sticky='nsew')

    def _create_buttons(self):
        #Button(root, text="1", padx=40, pady=20, command=lambda: enter_number(1))
        save_coords = tk.Button(self.parent, text="save_coords", padx=40, pady=20, command=self.save_coords)
        save_coords.grid(row=1, column=0)

        current_dir = tk.Button(self.parent, text="open images", padx=40, pady=20, command=self._open_image_folder)
        current_dir.grid(row=1, column=1)

    def _createCanvasBinding(self):
        self.canvas.bind( "<Button-1>", self.startRect )
        self.canvas.bind( "<ButtonRelease-1>", self.stopRect )
        self.canvas.bind( "<B1-Motion>", self.movingRect )

    def startRect(self, event):
        #Translate mouse screen x0,y0 coordinates to canvas coordinates
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
        with open('new.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow([self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1])
        self.canvas.delete(self.rectid)
        


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry( "800x800" )
    app = App(root)
    root.mainloop()



# spare code


# video_dir = "Volume_videos"

# images = []

# # for root, dirs, files in os.walk(video_dir, topdown=False):
# #    for name in files:
# #       file_name = (os.path.join(root, name))
# #       images.append(file_name)