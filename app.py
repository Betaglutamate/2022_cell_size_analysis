import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance


class App(tk.Frame):
    def __init__( self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self.my_images = []
        self.my_images.append(tk.PhotoImage(file="test.png"))
        self.my_images.append(tk.PhotoImage(file="test.png"))
        self.my_images.append(tk.PhotoImage(file="test.png"))
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.my_images[0])
        self._createCanvasBinding()

    def _createVariables(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None

    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width = 600, height = 600)
        self.canvas.grid(row=0, column=0, sticky='nsew')


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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry( "800x600" )
    app = App(root)
    root.mainloop()