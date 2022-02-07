import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.widgets import Button


class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.canvas = tk.Canvas(self, width=500, height=500, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

    def draw_image_and_button(self):
        self.figure_obj = Figure()
        self.ax = self.figure_obj.add_subplot()
        self.figure_obj.subplots_adjust(bottom=0.25)
        some_preloaded_data_array = np.zeros((600,600))
        imgplot = self.ax.imshow(some_preloaded_data_array, cmap='gray')
        # create tkagg canvas
        self.canvas_agg = FigureCanvasTkAgg(self.figure_obj, master=self.canvas)
        self.canvas_agg.draw()
        self.canvas_agg.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # add matplolib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas_agg, self.canvas)
        toolbar.update()
        self.canvas_agg._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # add matplolib widgets
        self.ax_ok_B = self.figure_obj.add_subplot(position=[0.2, 0.2, 0.1, 0.03]) # axes position doesn't really matter here because we have the resize event that adjusts widget position
        self.ok_B = Button(self.ax_ok_B, 'Ok', canvas=self.canvas_agg)
        # add tkinter widgets (outside of the matplolib canvas)
        button = tk.Button(master=self, text="Quit", command=self._quit)
        button.pack(side=tk.BOTTOM)
        # Connect to Events
        self.ok_B.on_clicked(self.ok)
        self.canvas_agg.mpl_connect('button_press_event', self.press)
        self.canvas_agg.mpl_connect('button_release_event', self.release)
        self.canvas_agg.mpl_connect('resize_event', self.resize)
        self.canvas_agg.mpl_connect("key_press_event", self.on_key_press)
        self.protocol("WM_DELETE_WINDOW", self.abort_exec)

    def abort_exec(self):
        print('Closing with \'x\' is disabled. Please use quit button')

    def _quit(self):
        print('Bye bye')
        self.quit()
        self.destroy()

    def ok(self, event):
        print('Bye bye')
        self.quit()
        self.destroy()

    def press(self, event):
        button = event.button
        print('You pressed button {}'.format(button))
        if event.inaxes == self.ax and event.button == 3:
            self.xp = int(event.xdata)
            self.yp = int(event.ydata)
            self.cid = (self.canvas_agg).mpl_connect('motion_notify_event',
                                                            self.draw_line)
            self.pltLine = Line2D([self.xp, self.xp], [self.yp, self.yp])

    def draw_line(self, event):
        if event.inaxes == self.ax and event.button == 3:
            self.yd = int(event.ydata)
            self.xd = int(event.xdata)
            self.pltLine.set_visible(False)
            self.pltLine = Line2D([self.xp, self.xd], [self.yp, self.yd], color='r')
            self.ax.add_line(self.pltLine)
            (self.canvas_agg).draw_idle()

    def release(self, event):
        button = event.button
        (self.canvas_agg).mpl_disconnect(self.cid)
        print('You released button {}'.format(button))

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))

    # Resize event is needed if you want your widget to move together with the plot when you resize the window
    def resize(self, event):
        ax_ok_left, ax_ok_bottom, ax_ok_right, ax_ok_top = self.ax.get_position().get_points().flatten()
        B_h = 0.08 # button width
        B_w = 0.2 # button height
        B_sp = 0.08 # space between plot and button
        self.ax_ok_B.set_position([ax_ok_right-B_w, ax_ok_bottom-B_h-B_sp, B_w, B_h])
        print('Window was resized')


if __name__ == "__main__":
    app = MyApp()
    app.draw_image_and_button()
    app.mainloop()