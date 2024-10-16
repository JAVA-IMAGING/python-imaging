import numpy as np
from src.util import *

'''
Create the master dark image from a list of FITS images
@arg fits_file:     List of FITS objects to be median-stacked
@arg output_file:   Path to where the output is going to be 
                    written
@return:            Fits object
'''
def median_stack_fits(fits_files: list[Fits], output_file: str):
    # List to store data arrays from FITS files
    image_data = []

    # Read each FITS file and append the data to the list
    for file in fits_files:
        image_data.append(file.get_data())
    
    # Stack the images and compute the median along the stack axis
    stacked_median = np.median(np.array(image_data), axis=0)

    # Return new Fits object with the calculated data
    return Fits.create_fits(output_file, stacked_median, True)
