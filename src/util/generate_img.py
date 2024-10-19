from PIL import Image
import numpy as np

from src.util.Fits import *
from src.util.Constant import *

def generate_img(fits_img: Fits):
    # path to save the image
    slash_idx = fits_img.path.rfind("/")
    filename = fits_img.path[slash_idx + 1:-5]  # this just grabs only the filename from the complete path 
    path = Constant.PNG_PATH + filename + ".png"

    # get data from FITS image, assign NaN to 0
    fits_data = np.nan_to_num(fits_img.get_data(), nan=0)
    max_val = np.max(fits_data)
    min_val = np.min(fits_data)

    # scaling data to 8 bits
    scaled_data = (fits_data - min_val) / (max_val - min_val) * 255

    # convert to 8-bit unsigned integer
    scaled_data = scaled_data.astype(np.uint8)

    image = Image.fromarray(scaled_data)
    image.save(path)

    print(f"Image saved as {path}")
