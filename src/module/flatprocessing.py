import numpy as np
import cv2
from scipy.ndimage import convolve

from src.util.Fits import *
from src.util import helperfunc

def normalize_fits(fits: Fits, overwrite: bool=True):
    """
    Normalize the master flat by dividing it by its median.
    """
    
    data = fits.get_data()

    median_data = np.median(data)

    normalized_data = data / median_data

    if overwrite:
        fits.set_data(normalized_data)
    else:
        path = fits.path[:len(path)-5] + "_normalized.fits"
        return Fits.filecreate(path, normalized_data)

def divide_fits(target_img: Fits, flat_img: Fits, overwrite: bool=True, output_path: str=None):
    """
    Divide target FITS image by flat FITS image

    params
    ------
    target_img: Fits
        Fits object of target image
    flat_img: Fits
        Fits object of flat image
    output_path: str, optional
        Path for the resulting division

    return
    ------
    Fits
        new Fits object of resulting division
    """

    flat_data = np.array(flat_img.get_data())
    target_data = np.array(target_img.get_data())

    flat_dimension = (flat_data.shape[0], flat_data.shape[1])
    target_dimension = (target_data.shape[0], target_data.shape[1])

    # Ensure same image dimensions
    if flat_dimension != target_dimension:
        raise ValueError(f"Different image dimensions!\nFlat image dimension: {flat_dimension}\nTarget image dimension: {target_dimension}")

    # Avoid division by zero by replacing zeros in the flat image with NaNs
    flat_data[flat_data == 0] = np.nan

    # Perform the division
    divided_data = np.divide(target_data, flat_data)

    # Replace NaNs resulting from division by zero with zeros
    divided_data = np.nan_to_num(divided_data)

    if overwrite:
        target_img.set_data(divided_data)
    else:
        # If output path is specified, do as so
        if output_path:
            file_name = target_img.path[target_img.path.rfind("/") + 1:len(target_img.path)-5] + "_divflat.fits"  # get file name
            new_path = output_path + file_name
        else:
            # The new file will have the same path and be named with "_divflat" at the end of it
            new_path = target_img.path[:len(target_img.path)-5] + "_divflat.fits"

        return Fits.filecreate(new_path, divided_data)

def sort_flats_by_color(fits_files: list[Fits]):
    """
    Sort flat images into separate lists for Red, Green, and Blue flats based on their FITS header information.
    
    params
    ------
    fits_files: list[Fits]
        List of FITS objects to be sorted by color channel.
    
    return
    ------
    tuple(list[Fits], list[Fits], list[Fits])
        Three lists of FITS objects: red_flats, green_flats, and blue_flats.
    """
    red_flats = []
    green_flats = []
    blue_flats = []
    
    for fits_file in fits_files:
        header = fits_file.hdul[0].header  # Access the header of the primary HDU
        print(header)
        # Check for the 'FILTER' keyword in the header to determine the color
        if 'FILTER' in header:
            filter_name = header['FILTER']  # Get the filter value directly from the header
            print(filter_name)
            if filter_name.lower() == 'r':  
                red_flats.append(fits_file)
            elif filter_name.lower() == 'g':
                green_flats.append(fits_file)
            elif filter_name.lower() == 'b':
                blue_flats.append(fits_file)
    
    return red_flats, green_flats, blue_flats

def extract_rgb_optimized(float_data, bayer_pat):
    """
    Extracts the red, green, and blue channels from a FITS image based on Bayer pattern using NumPy.
    
    Args:
        float_data (np.ndarray): 2D array of image data.
        bayer_pat (str): Bayer pattern (e.g., 'RGGB', 'BGGR').

    Returns:
        tuple: Three 2D arrays representing red, green, and blue channels.
    """
    # Image dimensions
    image_height, image_width = float_data.shape

    # Initialize red, green, and blue channels
    red_image = np.zeros((image_height, image_width), dtype=float)
    green_image = np.zeros((image_height, image_width), dtype=float)
    blue_image = np.zeros((image_height, image_width), dtype=float)

    # Define kernels for averaging neighboring pixels
    green_kernel = np.array([[0, 1, 0],
                             [1, 0, 1],
                             [0, 1, 0]]) * 0.25
    diag_kernel = np.array([[0.25, 0, 0.25],
                            [0,    0,  0],
                            [0.25, 0, 0.25]])
    #bayer_pat = 'RGGB'
    # RGGB pattern
    if bayer_pat == 'RGGB':
        # Red pixels: every [0::2, 0::2] position
        red_image[0::2, 0::2] = float_data[0::2, 0::2]
        
        # Blue pixels: every [1::2, 1::2] position
        blue_image[1::2, 1::2] = float_data[1::2, 1::2]
        
        # Green pixels
        green_image[0::2, 1::2] = float_data[0::2, 1::2]  # Green pixels on red row
        green_image[1::2, 0::2] = float_data[1::2, 0::2]  # Green pixels on blue row

    # BGGR pattern
    elif bayer_pat == 'BGGR':
        # Blue pixels: every [0::2, 0::2] position
        blue_image[0::2, 0::2] = float_data[0::2, 0::2]
        
        # Red pixels: every [1::2, 1::2] position
        red_image[1::2, 1::2] = float_data[1::2, 1::2]
        
        # Green pixels
        green_image[0::2, 1::2] = float_data[0::2, 1::2]  # Green pixels on blue row
        green_image[1::2, 0::2] = float_data[1::2, 0::2]  # Green pixels on red row
    else:
        raise ValueError("Invalid Bayer Pattern")
    
    # Apply convolution to get values for neighboring color channels
    red_image += convolve(float_data, diag_kernel) * (red_image == 0)
    green_image += convolve(float_data, green_kernel) * (green_image == 0)
    blue_image += convolve(float_data, diag_kernel) * (blue_image == 0)
    
    return red_image, green_image, blue_image


def extract_rgb_CV2(float_data, bayer_pat):
    """
    Extracts the red, green, and blue channels from a FITS image based on Bayer pattern using OpenCV.
    
    Args:
        float_data (np.ndarray): 2D array of image data.
        bayer_pat (str): Bayer pattern (e.g., 'RGGB', 'BGGR', 'GRBG', 'GBRG').

    Returns:
        tuple: Three 2D arrays representing red, green, and blue channels.
    """
    # Optional: You can normalize the input data before processing
    # Example: Normalize based on the data's range to avoid clipping or saturation.
    min_val, max_val = float_data.min(), float_data.max()
    float_data_scaled = (float_data - min_val) / (max_val - min_val) * 255  # Rescale to 0-255
    float_data_scaled = np.clip(float_data_scaled, 0, 255).astype(np.uint8)

    # Map Bayer pattern to OpenCV constants
    if bayer_pat == 'RGGB':
        bayer_code = cv2.COLOR_BAYER_RG2RGB
    elif bayer_pat == 'BGGR':
        bayer_code = cv2.COLOR_BAYER_BG2RGB
    elif bayer_pat == 'GRBG':
        bayer_code = cv2.COLOR_BAYER_GR2RGB
    elif bayer_pat == 'GBRG':
        bayer_code = cv2.COLOR_BAYER_GB2RGB
    else:
        raise ValueError(f"Invalid Bayer Pattern: {bayer_pat}")

    # Apply OpenCV's Bayer demosaicing
    rgb_image = cv2.cvtColor(float_data_scaled, bayer_code)

    # Calculate luminance (optional)
    luminance_image = calculate_luminance(rgb_image)
    
    # Split the RGB image into individual channels
    blue_image, green_image, red_image = cv2.split(rgb_image)
    #r,g,b = helperfunc.color_equalize_data(red_image,blue_image,green_image)
    
    # Convert channels back to float and scale to match original range
    red_image = red_image.astype(float) / 255 * (max_val - min_val) + min_val
    green_image = green_image.astype(float) / 255 * (max_val - min_val) + min_val
    blue_image = blue_image.astype(float) / 255 * (max_val - min_val) + min_val

    return red_image, green_image, blue_image

def extract_rgb(float_data, bayer_pat):
    """
    Extract RGB images from Bayer-patterned data using NumPy for efficient processing.
    
    Parameters:
        float_data (np.ndarray): 2D numpy array representing the input Bayer-patterned data.
        bayer_pat (str): Bayer pattern string ('RGGB' or 'BGGR').
    
    Returns:
        tuple: (red_image, green_image, blue_image) as 2D numpy arrays.
    """
    if bayer_pat.upper() not in {"RGGB", "BGGR"}:
        raise ValueError("Invalid Bayer Pattern")
    
    # Get the image dimensions
    image_height, image_width = float_data.shape
    
    # Initialize output arrays
    red_image = np.zeros_like(float_data, dtype=float_data.dtype)
    green_image = np.zeros_like(float_data, dtype=float_data.dtype)
    blue_image = np.zeros_like(float_data, dtype=float_data.dtype)
    
    # Generate row and column remainder grids
    rows, cols = np.indices((image_height, image_width))
    row_remainder = rows % 2
    col_remainder = cols % 2
    
    if bayer_pat.upper() == "RGGB":
        # Red pixels
        red_pixels = (row_remainder == 0) & (col_remainder == 0)
        red_image[red_pixels] = float_data[red_pixels]
        
        # Green pixels (case 1 and case 2)
        green_pixels_case1 = (row_remainder == 0) & (col_remainder == 1)
        green_pixels_case2 = (row_remainder == 1) & (col_remainder == 0)
        green_image[green_pixels_case1] = float_data[green_pixels_case1]
        green_image[green_pixels_case2] = float_data[green_pixels_case2]
        
        # Blue pixels
        blue_pixels = (row_remainder == 1) & (col_remainder == 1)
        blue_image[blue_pixels] = float_data[blue_pixels]
        
        # Calculate neighboring averages
        green_image[red_pixels] = 0.25 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0) +
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[red_pixels]
        
        green_image[blue_pixels] = 0.25 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0) +
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[blue_pixels]
        
        blue_image[red_pixels] = 0.25 * (
            np.roll(np.roll(float_data, -1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, -1, axis=0), 1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), 1, axis=1)
        )[red_pixels]
        
        red_image[blue_pixels] = 0.25 * (
            np.roll(np.roll(float_data, -1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, -1, axis=0), 1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), 1, axis=1)
        )[blue_pixels]
        
        red_image[green_pixels_case1] = 0.5 * (
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[green_pixels_case1]
        
        red_image[green_pixels_case2] = 0.5 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0)
        )[green_pixels_case2]
        
        blue_image[green_pixels_case1] = 0.5 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0)
        )[green_pixels_case1]
        
        blue_image[green_pixels_case2] = 0.5 * (
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[green_pixels_case2]
    
    elif bayer_pat.upper() == "BGGR":
        # Blue pixels
        blue_pixels = (row_remainder == 0) & (col_remainder == 0)
        blue_image[blue_pixels] = float_data[blue_pixels]

        # Green pixels (case 1 and case 2)
        green_pixels_case1 = (row_remainder == 0) & (col_remainder == 1)
        green_pixels_case2 = (row_remainder == 1) & (col_remainder == 0)
        green_image[green_pixels_case1] = float_data[green_pixels_case1]
        green_image[green_pixels_case2] = float_data[green_pixels_case2]

        # Red pixels
        red_pixels = (row_remainder == 1) & (col_remainder == 1)
        red_image[red_pixels] = float_data[red_pixels]

        # Interpolate green for blue pixels
        green_image[blue_pixels] = 0.25 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0) +
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[blue_pixels]

        # Interpolate green for red pixels
        green_image[red_pixels] = 0.25 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0) +
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[red_pixels]

        # Interpolate red for blue pixels
        red_image[blue_pixels] = 0.25 * (
            np.roll(np.roll(float_data, -1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, -1, axis=0), 1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), 1, axis=1)
        )[blue_pixels]

        # Interpolate blue for red pixels
        blue_image[red_pixels] = 0.25 * (
            np.roll(np.roll(float_data, -1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, -1, axis=0), 1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), -1, axis=1) +
            np.roll(np.roll(float_data, 1, axis=0), 1, axis=1)
        )[red_pixels]

        # Interpolate red and blue for green pixels
        red_image[green_pixels_case1] = 0.5 * (
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[green_pixels_case1]

        red_image[green_pixels_case2] = 0.5 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0)
        )[green_pixels_case2]

        blue_image[green_pixels_case1] = 0.5 * (
            np.roll(float_data, -1, axis=0) + np.roll(float_data, 1, axis=0)
        )[green_pixels_case1]

        blue_image[green_pixels_case2] = 0.5 * (
            np.roll(float_data, -1, axis=1) + np.roll(float_data, 1, axis=1)
        )[green_pixels_case2]
    
    return red_image, green_image, blue_image


def calculate_luminance(rgb_image):
    """
    Calculate the luminance of an RGB image using the Rec. 709 formula.

    Args:
        rgb_image (np.ndarray): The input RGB image (3-channel).

    Returns:
        np.ndarray: The luminance image (single channel).
    """
    # Apply the Rec. 709 luminance formula
    luminance = 0.299 * rgb_image[:, :, 0] + 0.587 * rgb_image[:, :, 1] + 0.114 * rgb_image[:, :, 2]
    # Java code uses 0.222 * R + 0.707 * G + 0.071 * B for this might be better IDRK 
    return luminance

    
