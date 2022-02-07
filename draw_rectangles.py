import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance


class App(tk.Frame):
    def __init__( self, parent):
        tk.Frame.__init__(self, parent)
        self._createVariables(parent)
        self._createCanvas()
        self._createCanvasBinding()

    def _createVariables(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None

    def _createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width = 600, height = 600,
                                bg = "white" )

        my_img1 = ImageTk.PhotoImage(Image.open("test.png"))
        mylabel = tk.Label(image=my_img1)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        mylabel.grid(row=0, column=0, columnspan=3)



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
            self.rectx0, self.recty0, self.rectx0, self.recty0, fill="#4eccde")
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


    # def printcoords(event):
    #     #outputting x and y coords to console
    #     x, y = (event.x,event.y)

    #     labelx = tk.Label(root, text="xcord").grid(column=4, row=2)
    #     enter_x = tk.Entry(root)
    #     enter_x.insert(0, x)
    #     enter_x.grid(column=4, row=3)

    #     labely = tk.Label(root, text="ycord").grid(column=5, row=2)
    #     enter_y = tk.Entry(root)
    #     enter_y.insert(0, y)
    #     enter_y.grid(column=5, row=3)
    # #mouseclick event


    # my_img1 = ImageTk.PhotoImage(Image.open("test.png"))
    # my_img2 = ImageTk.PhotoImage(Image.open("images/171822-0001.tif"))
    # my_img3 = ImageTk.PhotoImage(Image.open("images/171822-0002.tif"))
    # my_img4 = ImageTk.PhotoImage(Image.open("test.png"))


    # image_list = [my_img1, my_img2, my_img3, my_img4]


    # mylabel = tk.Label(image=my_img1)
    # mylabel.grid(row=0, column=0, columnspan=3)


    # button_forward= tk.Button(root, text="forward", command = lambda: forward(0, mylabel, "forward"))
    # button_back= tk.Button(root, text="back", command = lambda: forward(0, mylabel, "backward"))
    # button_close= tk.Button(root, text="close", command=root.destroy)

    # button_back.grid(row=1, column=0)
    # button_close.grid(row=1, column=1)
    # button_forward.grid(row=1, column=2)


    # root.bind("<Button 1>",printcoords)

    #mouseclick event
    root.mainloop()