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
    return Fits.create_fits(output_file, stacked_median)

'''
Subtract master dark from target FITS image
@arg target_img:    Fits object of target image
@arg dark_img:      Fits object of dark image
@return:            new Fits object of resulting subtraction
'''
def subtract_dark(target_img: Fits, dark_img: Fits):
    dark_data = np.array(dark_img.get_data())
    target_data = np.array(target_img.get_data())

    dark_dimension = (dark_data.shape[0], dark_data.shape[1])
    target_dimension = (target_data.shape[0], target_data.shape[1])

    # ensure same image dimensions
    if (dark_dimension != target_dimension):
        raise BaseException(f"Different image dimensons!\ndark image dimension: {dark_dimension}\ntarget image dimension: {target_dimension}")
    
    target_data = np.subtract(target_data, dark_data)
    # the new file will have the same path and named with "_subdark" at the end of it
    new_path = target_img.path[:len(target_img.path)-5] + "_subdark" + target_img.path[len(target_img.path)-5:] 

    return Fits.create_fits(new_path,target_data)