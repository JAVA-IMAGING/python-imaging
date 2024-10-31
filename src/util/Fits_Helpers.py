from src.module import *
from src.util import *
import numpy as np
import cv2
from astropy.io import fits

def resize_fits_data(fits_img: Fits, target_shape):
    """Resizes FITS image data to the target shape."""
    data = np.array(fits_img.get_data())
    resized_data = cv2.resize(data, (target_shape[1], target_shape[0]))  # OpenCV uses (width, height) format
    fits_img.set_data(resized_data)
    return fits_img

def adjust_gamma(image, gamma=1.0):
    """Adjusts gamma for an image to control brightness."""
    inv_gamma = 1.0 / gamma
    image = image / np.max(image)  # Normalize before gamma correction
    return np.power(image, inv_gamma) * np.max(image)

def histogram_equalize(image):
    """Applies histogram equalization to enhance contrast."""
    normalized_image = (image / np.max(image) * 255).astype(np.uint8)
    equalized_image = cv2.equalizeHist(normalized_image)
    return equalized_image / 255.0 * np.max(image)  # Rescale to original max range

def extract_rgb_from_fits(fits_path, output_red, output_green, output_blue):
    """
    Extract RGB channels from a FITS file based on the Bayer pattern and save each as a separate FITS file.
    """
    with fits.open(fits_path) as hdul:
        float_data = hdul[0].data.astype(float)
        header = hdul[0].header
        #bayer_pat = header.get("BAYERPAT")
        bayer_pat = 'BGGR'
        if not bayer_pat:
            raise ValueError("BAYERPAT not found in FITS header.")

        # Extract RGB channels based on Bayer pattern
        red_image, green_image, blue_image = extract_rgb(float_data, bayer_pat)
        
        # Save each channel as a FITS file
        red_fits = Fits.create_fits(output_red, red_image)
        green_fits = Fits.create_fits(output_green, green_image)
        blue_fits = Fits.create_fits(output_blue, blue_image)

        return red_fits, green_fits, blue_fits
