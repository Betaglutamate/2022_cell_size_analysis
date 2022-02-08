import tkinter as tk
from app_class import App

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry( "1000x800" )
    app = App(root)
    root.mainloop()



# spare code


# video_dir = "Volume_videos"

# images = []

# # for root, dirs, files in os.walk(video_dir, topdown=False):
# #    for name in files:
# #       file_name = (os.path.join(root, name))
# #       images.append(file_name)