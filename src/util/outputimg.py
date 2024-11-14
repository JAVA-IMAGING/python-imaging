from PIL import Image
import cv2 # switching from Pillow to cv2
import numpy as np

from src.util.Fits import *
from src.util.Constant import *

# TODO: This implementation is not accurate. It is better to be given the 
#       separate channels as arguments to ensure that the datas are correct
def generate_img(fits_img: Fits, boost_factor: float = 1.0):
    """
    Generate a PNG file from given Fits object and boosting the pixels

    params
    ------
    fits_img: Fits
        Fits object to be converted into PNG image
    boost_factor: float, optional
        Float value to boost the image's contrast
    """
    
    # path to save the image
    slash_idx = fits_img.path.rfind("/")
    filename = fits_img.path[slash_idx + 1:-5]  # this grabs only the filename from the complete path 
    path = Constant.OUTPUT_PATH + filename + ".png"

    # get data from FITS image
    fits_data = np.array(fits_img.get_data())

    max_val = np.max(fits_data)
    min_val = np.min(fits_data)

    # scaling data to 8 bits and perform linear contrast stretching
    scaled_data = (fits_data - min_val) / (max_val - min_val) * 255 * boost_factor

    # clip to valid range after boosting
    scaled_data = np.clip(scaled_data, 0, 255)

    # cast to 8-bit unsigned integer
    scaled_data = scaled_data.astype(np.uint8)

    image = Image.fromarray(scaled_data)
    image.save(path)

    print(f"Image saved as {path}")

def generate_PNG(file_name: str, red_channel: Fits, green_channel: Fits, blue_channel: Fits, boost_factor: float = 1):
    """
    jujur cape gw nulis ginian
    extra note, ga perlu kasih whole path, just the name
    """

    # helper function
    def scale_channel(data, min_val, max_val):
        scaled_data = (data - min_val) / (max_val - min_val) * 255 * boost_factor   # doing the math
        scaled_data = np.clip(scaled_data, 0, 255)  # clips any value outside the range

        return scaled_data.astype(np.uint8)
    
    # scaling the channels to 256 bits
    red_data = np.array(red_channel.get_data())
    red_scaled = scale_channel(red_data, np.min(red_data), np.max(red_data))

    green_data = np.array(green_channel.get_data())
    green_scaled = scale_channel(green_data, np.min(green_data), np.max(green_data),)

    
    blue_data = np.array(blue_channel.get_data())
    blue_scaled = scale_channel(blue_data, np.min(blue_data), np.max(blue_data))

    rgb_image = cv2.merge((blue_scaled, green_scaled, red_scaled))  # cv2 follows the order BGR, or so I'm told

    path = Constant.OUTPUT_PATH + file_name
    cv2.imwrite(path, rgb_image)
    print(f"PNG image generated at {path}")

# Wrapper for grayscale images
def generate_grayscale_PNG(file_name: str, image_data: Fits, boost_factor: float = 1):
    generate_PNG(file_name, image_data, image_data, image_data, boost_factor)
