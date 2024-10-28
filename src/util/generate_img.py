from PIL import Image
import numpy as np

from src.util.Fits import *
from src.util.Constant import *

# TODO: This implementation is not accurate. It is better to be given the 
#       separate channels as arguments to ensure that the datas are correct
def generate_img(fits_img: Fits, boost_factor: float = 1.0):
    '''
    Generate a PNG file from given Fits object and boosting the pixels

    params
    ------
    fits_img: Fits
        Fits object to be converted into PNG image
    boost_factor: float, optional
        Float value to boost the image's contrast
    '''
    
    # path to save the image
    slash_idx = fits_img.path.rfind("/")
    filename = fits_img.path[slash_idx + 1:-5]  # this grabs only the filename from the complete path 
    path = Constant.PNG_PATH + filename + ".png"

    # get data from FITS image
    fits_data = np.array(fits_img.get_data())

    max_val = np.max(fits_data)
    min_val = np.min(fits_data)

    # scaling data to 8 bits and perform linear contrast stretching
    scaled_data = (fits_data - min_val) / (max_val - min_val) * 255 * boost_factor

    # clip to valid range after boosting
    scaled_data = np.clip(scaled_data, 0, 255)

    # convert to 8-bit unsigned integer
    scaled_data = scaled_data.astype(np.uint8)

    image = Image.fromarray(scaled_data)
    image.save(path)

    print(f"Image saved as {path}")
