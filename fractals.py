"""
Alex Eidt

Contains Escape time fractal calculation functions.
"""

import math
import numpy as np
from numba import njit, prange


@njit(parallel=True, nogil=True, fastmath=True)
def julia(image, palette, iterations, brx, bry, tlx, tly, smooth, jr=-0.70176, ji=-0.3842):
    height, width = image.shape[:2]
    scale_x = (brx - tlx) / width
    scale_y = (bry - tly) / height

    for y in prange(height):
        for x in range(width):
            z = complex(tlx + x * scale_x, tly + y * scale_y)
            c = complex(jr, ji)
  
            n = 0
            while n < iterations and z.real**2 + z.imag**2 <= (1 << 16):
                z = z**2 + c
                n += 1

            if smooth:
                if n < iterations:
                    log_zn = np.log(z.real*z.real + z.imag*z.imag) / 2
                    nu = np.log(log_zn / np.log(2)) / np.log(2)
                    n = n + 1 - nu

                floor = math.floor(n)
                remainder = n - floor
                image[y, x] = palette[floor] * (1 - remainder) + palette[floor + 1] * remainder
            else:
                image[y, x] = palette[int(n / iterations * len(palette))]


@njit(parallel=True, nogil=True, fastmath=True)
def mandelbrot(image, palette, iterations, brx, bry, tlx, tly, smooth, mr=0, mi=0):
    # Parameters mr and mi are placeholders to make calling between fractal functions easier.
    height, width = image.shape[:2]
    scale_x = (brx - tlx) / width
    scale_y = (bry - tly) / height

    for y in prange(height):
        for x in range(width):
            z = complex(tlx + x * scale_x, tly + y * scale_y)
            c = complex(z.real, z.imag)

            n = 0
            while n < iterations and z.real**2 + z.imag**2 <= (1 << 16):
                z = z**2 + c
                n += 1

            if smooth:
                if n < iterations:
                    log_zn = np.log(z.real*z.real + z.imag*z.imag) / 2
                    nu = np.log(log_zn / np.log(2)) / np.log(2)
                    n = n + 1 - nu

                floor = math.floor(n)
                remainder = n - floor
                image[y, x] = palette[floor] * (1 - remainder) + palette[floor + 1] * remainder
            else:
                image[y, x] = palette[int(n / iterations * len(palette))]