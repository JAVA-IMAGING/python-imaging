import numpy as np
from src.util import *

def create_master_flat(images):
    """Create a master flat by median stacking the images."""
    image_data = []

    # Read each FITS file and append the data to the list
    for file in images:
        image_data.append(file.get_data())
        
    master_flat = np.median(np.array(image_data), axis=0)
    return master_flat

def normalize_master_flat(master_flat, output_file):
    """Normalize the master flat by dividing it by its median."""
    
    median_master_flat = np.median(master_flat)

    normalized_master_flat = master_flat / median_master_flat
    return Fits.create_fits(output_file, normalized_master_flat)

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
        #bayer_pat = 'RGGB'
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
    
