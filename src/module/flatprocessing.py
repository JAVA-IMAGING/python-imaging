import numpy as np
from scipy.ndimage import convolve

from src.util.Fits import *

def normalize_fits(fits, output_file):
    """
    Normalize the master flat by dividing it by its median.
    """
    
    median_master_flat = np.median(fits)

    normalized_master_flat = fits / median_master_flat
    return Fits.filecreate(output_file, normalized_master_flat)

def divide_fits(target_img: Fits, flat_img: Fits, output_path: str=None):
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


def extract_rgb(float_data, bayer_pat):
        """
        Extracts the red, green, and blue channels from a FITS image based on Bayer pattern.
        
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

        # Bayer Pattern Handling
        bayer_pat = bayer_pat.upper()
        # bayer_pat = 'BGGR'
        
        if bayer_pat == 'RGGB':
            # Loop through pixels excluding border pixels
            for row in range(1, image_height - 1):
                for col in range(1, image_width - 1):
                    row_rem = row % 2
                    col_rem = col % 2

                    # Red pixel
                    if row_rem == 0 and col_rem == 0:
                        red_image[row, col] = float_data[row, col]
                        green_image[row, col] = 0.25 * (
                            float_data[row - 1, col] + float_data[row + 1, col] + 
                            float_data[row, col - 1] + float_data[row, col + 1]
                        )
                        blue_image[row, col] = 0.25 * (
                            float_data[row - 1, col - 1] + float_data[row - 1, col + 1] + 
                            float_data[row + 1, col - 1] + float_data[row + 1, col + 1]
                        )
                    
                    # Blue pixel
                    elif row_rem == 1 and col_rem == 1:
                        red_image[row, col] = 0.25 * (
                            float_data[row - 1, col - 1] + float_data[row - 1, col + 1] + 
                            float_data[row + 1, col - 1] + float_data[row + 1, col + 1]
                        )
                        green_image[row, col] = 0.25 * (
                            float_data[row - 1, col] + float_data[row + 1, col] + 
                            float_data[row, col - 1] + float_data[row, col + 1]
                        )
                        blue_image[row, col] = float_data[row, col]

                    # Green pixels
                    elif row_rem == 0 and col_rem == 1:
                        red_image[row, col] = 0.5 * (float_data[row, col - 1] + float_data[row, col + 1])
                        green_image[row, col] = float_data[row, col]
                        blue_image[row, col] = 0.5 * (float_data[row - 1, col] + float_data[row + 1, col])

                    elif row_rem == 1 and col_rem == 0:
                        red_image[row, col] = 0.5 * (float_data[row - 1, col] + float_data[row + 1, col])
                        green_image[row, col] = float_data[row, col]
                        blue_image[row, col] = 0.5 * (float_data[row, col - 1] + float_data[row, col + 1])

        elif bayer_pat == 'BGGR':
            # Loop through pixels excluding border pixels
            for row in range(1, image_height - 1):
                for col in range(1, image_width - 1):
                    row_rem = row % 2
                    col_rem = col % 2

                    # Blue pixel
                    if row_rem == 0 and col_rem == 0:
                        blue_image[row, col] = float_data[row, col]
                        green_image[row, col] = 0.25 * (
                            float_data[row - 1, col] + float_data[row + 1, col] + 
                            float_data[row, col - 1] + float_data[row, col + 1]
                        )
                        red_image[row, col] = 0.25 * (
                            float_data[row - 1, col - 1] + float_data[row - 1, col + 1] + 
                            float_data[row + 1, col - 1] + float_data[row + 1, col + 1]
                        )

                    # Red pixel
                    elif row_rem == 1 and col_rem == 1:
                        red_image[row, col] = float_data[row, col]
                        green_image[row, col] = 0.25 * (
                            float_data[row - 1, col] + float_data[row + 1, col] + 
                            float_data[row, col - 1] + float_data[row, col + 1]
                        )
                        blue_image[row, col] = 0.25 * (
                            float_data[row - 1, col - 1] + float_data[row - 1, col + 1] + 
                            float_data[row + 1, col - 1] + float_data[row + 1, col + 1]
                        )

                    # Green pixels
                    elif row_rem == 0 and col_rem == 1:
                        blue_image[row, col] = 0.5 * (float_data[row, col - 1] + float_data[row, col + 1])
                        green_image[row, col] = float_data[row, col]
                        red_image[row, col] = 0.5 * (float_data[row - 1, col] + float_data[row + 1, col])

                    elif row_rem == 1 and col_rem == 0:
                        blue_image[row, col] = 0.5 * (float_data[row - 1, col] + float_data[row + 1, col])
                        green_image[row, col] = float_data[row, col]
                        red_image[row, col] = 0.5 * (float_data[row, col - 1] + float_data[row, col + 1])
        else:
            raise ValueError("Invalid Bayer Pattern")

        return red_image, green_image, blue_image
    
    
    

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
    print(red_image)
    # Apply convolution to get values for neighboring color channels
    red_image += convolve(float_data, diag_kernel) * (red_image == 0)
    green_image += convolve(float_data, green_kernel) * (green_image == 0)
    blue_image += convolve(float_data, diag_kernel) * (blue_image == 0)

    return red_image, green_image, blue_image
    
