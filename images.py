import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import matplotlib.pyplot as plt
import skimage as sk


def save_coords():
    current_x = int(enter_x.get())
    current_y = int(enter_y.get())
    my_rect = canvas.create_rectangle(current_x, current_y, current_x+15, current_y+15,
    outline="#fb0", fill="#fb0")


def draw_box():
    canvas.create_rectangle(1, 1, 50, 50, outline='red')



def printcoords(event):
    #outputting x and y coords to console
    global enter_x, enter_y

    x, y = (event.x,event.y)

    labelx = tk.Label(root, text="xcord").grid(column=4, row=2)
    enter_x = tk.Entry(root)
    enter_x.insert(0, x)
    enter_x.grid(column=4, row=3)

    labely = tk.Label(root, text="ycord").grid(column=5, row=2)
    enter_y = tk.Entry(root)
    enter_y.insert(0, y)
    enter_y.grid(column=5, row=3)

        
    #mouseclick event    

def forward(image_number, canvas, direction):
    
    if direction == "forward":

        if image_number >= len(image_list)-1:
            button_forward= tk.Button(root, text="forward", state=tk.DISABLED, command = lambda: forward(image_number, canvas, "forward"))
            button_forward.grid(row=1, column=2)
        else:
            image_number =  image_number + 1

            print(image_number)

            canvas.grid_forget()
            canvas= tk.Label(image=image_list[image_number])
            canvas.grid(row=0, column=0, columnspan=3)
            button_forward= tk.Button(root, text="forward", command = lambda: forward(image_number, canvas, "forward"))
            button_backward= tk.Button(root, text="backward", command = lambda: forward(image_number, canvas, "backward"))
            button_forward.grid(row=1, column=2)
            button_backward.grid(row=1, column=0)
        
    elif direction == "backward":
        print(image_number)

        if image_number <= 0:
            button_backward= tk.Button(root, text="backward", state=tk.DISABLED, command = lambda: forward(image_number, canvas, "backward"))
            button_backward.grid(row=1, column=0)

        else:
            image_number =  image_number - 1
            canvas.grid_forget()
            canvas= tk.Label(image=image_list[image_number])
            canvas.grid(row=0, column=0, columnspan=3)
            button_forward= tk.Button(root, text="forward", command = lambda: forward(image_number, canvas, "forward"))
            button_backward= tk.Button(root, text="backward", command = lambda: forward(image_number, canvas, "backward"))
            button_forward.grid(row=1, column=2)
            button_backward.grid(row=1, column=0)




### Main APP

root= tk.Tk()

canvas = tk.Canvas(root, width=600, height=600)
canvas.grid(row=0, column=0, columnspan=3)
png = tk.PhotoImage(file = r'test.png') # Just an example
canvas.create_image(0, 0, image = png, anchor = "nw")



root.img = tk.PhotoImage(file="info.png")
root.iconphoto( False, root.img )
root.title("Images")


#convert sk image to pillow
my_img1 = ImageTk.PhotoImage(Image.open("test.png"))
my_img2 = ImageTk.PhotoImage(Image.open("bact.png"))
my_img3 = ImageTk.PhotoImage(Image.open("bact.png"))
my_img4 = ImageTk.PhotoImage(Image.open("test.png"))


image_list = [my_img1, my_img2, my_img3, my_img4]


# canvas = tk.Label(image=my_img1)
# canvas.grid(row=0, column=0, columnspan=3)


button_forward= tk.Button(root, text="forward", command = lambda: forward(0, canvas, "forward"))
button_back= tk.Button(root, text="back", command = lambda: forward(0, canvas, "backward"))
button_close= tk.Button(root, text="close", command=root.destroy)

button_back.grid(row=1, column=0)
button_close.grid(row=1, column=1)
button_forward.grid(row=1, column=2)

button_first_coords = tk.Button(root, text="select_coords", command = save_coords)
button_first_coords.grid(row = 3, column=0, columnspan=2)


root.bind("<space>",printcoords)

root.mainloop()

