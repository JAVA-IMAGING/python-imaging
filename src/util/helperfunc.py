import numpy as np
import cv2

from src.util.Fits import *
from src.module import flatprocessing

def resize_fits_data(fits_img: Fits, target_shape: tuple):
    """Resizes FITS image data to the target shape."""
    data = np.array(fits_img.get_data())
    resized_data = cv2.resize(data, (target_shape[1], target_shape[0]))  # OpenCV uses (width, height) format
    fits_img.set_data(resized_data)
    return fits_img

def adjust_gamma(image: list[list[float]], gamma: float=1.0):
    """Adjusts gamma for an image to control brightness."""
    inv_gamma = 1.0 / gamma
    image = image / np.max(image)  # Normalize before gamma correction
    return np.power(image, inv_gamma) * np.max(image)

def histogram_equalize(image: list[list[float]]):
    """Applies histogram equalization to enhance contrast."""
    normalized_image = (image / np.max(image) * 255).astype(np.uint8)
    equalized_image = cv2.equalizeHist(normalized_image)
    return equalized_image / 255.0 * np.max(image)  # Rescale to original max range

def color_equalize(red: Fits, green: Fits, blue: Fits):
    r = red.get_data()
    g = green.get_data()
    b = blue.get_data()
    
    r_mean = np.mean(r)
    g_mean = np.mean(g)
    b_mean = np.mean(b)

    r_std = np.std(r)
    g_std = np.std(g)
    b_std = np.std(b)
    
    green_a = 1
    green_b = 0
    
    blue_a = g_std / b_std
    blue_b = g_mean - blue_a * b_mean
    
    red_a = g_std / r_std
    red_b = g_mean - red_a * r_mean
    
    red.set_data(np.multiply(r,red_a))
    red.set_data(np.add(r,red_b))
    
    green.set_data(np.multiply(g,green_a))
    green.set_data(np.add(g,green_b))
    
    blue.set_data(np.multiply(b,blue_a))
    blue.set_data(np.add(b,blue_b))

def extract_rgb_from_fits(fits_img: Fits, directory: str):
    """
    Extract RGB channels from a FITS file based on the Bayer pattern and save each as a separate FITS file.

    params
    ------
    fits_img: Fits
        Fits image object with valid Bayer pattern listed on the header file
    directory: str
        Directory path as string for Fits object

    return
    ------
    tuple(Fits, Fits, Fits):
        Tuple of three Fits objects each representing a color channel (Red, Green, Blue)
    """
    
    data = fits_img.get_data().astype(float)
    bayer_pat = fits_img.bayerpat()

    red_image, green_image, blue_image = flatprocessing.extract_rgb_optimized(data, bayer_pat)
        
    # Save each channel as a FITS file
    fn = directory + fits_img.path[fits_img.path.rfind("/") + 1:len(fits_img.path) - 5] # just the filename, without .fits extension

    red_fits = Fits.filecreate(fn + "_r.fits", red_image)
    green_fits = Fits.filecreate(fn + "_g.fits", green_image)
    blue_fits = Fits.filecreate(fn + "_b.fits", blue_image)
    
    return red_fits, green_fits, blue_fits
    