"""
Alex Eidt

This script creates a viewer for escape time fractals using a TKinter GUI.
"""

import imageio
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from fractals import mandelbrot, julia


WIDTH, HEIGHT = 640, 360
MIN_ITERATIONS = 100
MAX_ITERATIONS = 1024
SNAPSHOT_TYPE = 'png'


class FractalViewer:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.iterations = MIN_ITERATIONS
        self.draw = False
        self.smooth = True
        self.fractal_func = mandelbrot
        self.image = np.empty((height, width, 3), dtype=np.uint8)
        self.snapshot_count = 0

        self.scale = np.array([width/2, height], dtype=np.float64)
        zero = np.array([0, 0], dtype=np.float64)
        self.offset = zero.copy()
        self.mouse = zero.copy()
        self.pressed = zero.copy()
        # Top left and Bottom right points of the fractal space.
        self.frac_tl = zero.copy()
        self.frac_br = zero.copy()
        # Top left and Bottom right points of the fractal on screen.
        self.pix_tl = zero.copy()
        self.pix_br = np.array([width, height], dtype=np.float64)
        # Julia Set initial complex point.
        self.julia_point = np.array([-0.70176, -0.3842], dtype=np.float64)

        self.mouse_before_zoom = zero.copy()
        self.mouse_after_zoom = zero.copy()
    
        self.alpha = 0.1
        self.palette = np.array([
            (0.5 * np.sin(np.arange(MAX_ITERATIONS) * self.alpha) + 0.5) * 255,
            (0.5 * np.sin(np.arange(MAX_ITERATIONS) * self.alpha + 2.094) + 0.5) * 255,
            (0.5 * np.sin(np.arange(MAX_ITERATIONS) * self.alpha + 4.188) + 0.5) * 255
        ], dtype=np.uint8).transpose(1, 0)

        self.fractal_func(
            self.image,
            self.palette,
            self.iterations,
            self.frac_tl[0], self.frac_tl[1],
            self.frac_br[0], self.frac_br[1],
            self.smooth,
            self.julia_point[0], self.julia_point[1]
        )

        root = tk.Tk()
        root.title("Fractals")

        frame_image = ImageTk.PhotoImage(Image.fromarray(self.image))
        self.label = tk.Label(root, image=frame_image)
        self.label.pack()

        root.bind('<KeyPress>', lambda event: self.update_keypress(event))
        root.bind('<MouseWheel>', lambda event: self.update_mousewheel(event))
        root.bind('<Motion>', lambda event: self.motion(event))
        root.bind('<ButtonPress 1>', self.set_pressed)
        root.bind('<ButtonRelease 1>', self.set_pressed)

        self.update_screen()

        root.resizable(False, False)
        root.mainloop()

    def update_keypress(self, event):
        shift = event.char.isupper()
        key = event.char.lower()

        if key == 'm':
            self.fractal_func = mandelbrot
        elif key == 'j':
            self.fractal_func = julia

        if key == 's':
            self.smooth = not self.smooth

        if key == 'i':
            # If holding shift, increase iterations.
            self.iterations += -4 if shift else 4
            self.iterations = max(min(self.iterations, MAX_ITERATIONS), MIN_ITERATIONS)

        if key == 'k':
            self.julia_point[0] += -0.01 if shift else 0.01
        if key == 'l':
            self.julia_point[1] += -0.01 if shift else 0.01

        if key == 'c':
            imageio.imwrite(f'fractal-{self.snapshot_count}.{SNAPSHOT_TYPE}', self.image)
            self.snapshot_count += 1
        
        if key in 'mjsikl':
            self.update_screen()

    def update_mousewheel(self, event):
        self.screen_to_world(self.pix_br - self.mouse, self.mouse_before_zoom)

        if event.delta < 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        
        self.screen_to_world(self.pix_br - self.mouse, self.mouse_after_zoom)
        self.offset += (self.mouse_before_zoom - self.mouse_after_zoom)
        self.update_screen()

    def update_screen(self):
        self.screen_to_world(self.pix_tl, self.frac_tl)
        self.screen_to_world(self.pix_br, self.frac_br)
        self.fractal_func(
            self.image,
            self.palette,
            self.iterations,
            self.frac_tl[0], self.frac_tl[1],
            self.frac_br[0], self.frac_br[1],
            self.smooth,
            self.julia_point[0], self.julia_point[1]
        )
        frame_image = ImageTk.PhotoImage(Image.fromarray(self.image))
        self.label.configure(image=frame_image)
        self.label.image = frame_image
        self.label.pack()

    def motion(self, event):
        x, y = event.x, event.y
        self.mouse[:] = x, y

        if not self.draw:
            return

        self.offset -= (self.pressed - self.mouse) / self.scale
        self.pressed[:] = x, y
        self.update_screen()

    def world_to_screen(self, v, n):
        n[:] = (v - self.offset) * self.scale

    def screen_to_world(self,n, v):
        v[:] = n / self.scale + self.offset

    def set_pressed(self, event):
        self.pressed[:] = event.x, event.y
        self.draw = not self.draw


def main():
    FractalViewer(WIDTH, HEIGHT)


if __name__ == '__main__':
    main()
