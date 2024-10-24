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


