import numpy as np
from src.util import *

def median_stack_fits(fits_files: list[Fits], output_file: str):
    '''
    Create a median-stacked image from a list of FITS images

    params
    ------
    fits_file: list[Fits]
        List of FITS objects to be median-stacked
    output_file: str
        Path to where the output is going to be written

    return
    ------
    Fits
        Fits object
    '''
    
    # List to store data arrays from FITS files
    image_data = []

    # Read each FITS file and append the data to the list
    for file in fits_files:
        image_data.append(file.get_data())
    
    # Stack the images and compute the median along the stack axis
    stacked_median = np.median(np.array(image_data), axis=0)

    # Return new Fits object with the calculated data
    return Fits.create_fits(output_file, stacked_median)

def subtract_dark(target_img: Fits, dark_img: Fits):
    '''
    Subtract master dark from target FITS image

    params
    ------
    target_img: Fits
        Fits object of target image
    dark_img: Fits
        Fits object of dark image

    return
    ------
    Fits
        new Fits object of resulting subtraction
    '''

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