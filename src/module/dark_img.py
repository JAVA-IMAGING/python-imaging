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

# TODO: do the mean stack they did
def mean_stack_fits(fits_files: list[Fits], output_file: str):
    '''
    Create a mean-stacked image from a list of FITS images

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
    dark_image = []

    # Read each FITS file and append the data to the list
    for file in fits_files:
        image_data.append(file.get_data())

    stdev = np.std(np.array(image_data), axis=0)
    mean = np.mean(np.array(image_data), axis=0)

    # Create a mask to filter out outliers, and average the values that are left
    mask = np.abs(image_data - mean) <= 1.5 * stdev     # formula taken from Swift team's code
    masked_data = np.where(mask, image_data, np.nan)    # this was what Elaine meant by using mask
    mean_masked = np.nanmean(masked_data, axis=0)

    return Fits.create_fits(output_file, mean_masked)

def subtract_fits(target_img: Fits, dark_img: Fits, output_path: str = None):
    '''
    Subtract master dark from target FITS image

    params
    ------
    target_img: Fits
        Fits object of target image
    dark_img: Fits
        Fits object of dark image
    output_path: str, optional
        Path for the resulting subtraction

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

    # if output path is specified, do as so
    if (output_path):
        file_name = target_img.path[target_img.path.rfind("/") + 1:] + "_subdark"   # get file name
        new_path = output_path + file_name
    
    # the new file will have the same path and named with "_subdark" at the end of it
    else:
        new_path = target_img.path[:len(target_img.path)-5] + "_subdark" + target_img.path[len(target_img.path)-5:] 

    return Fits.create_fits(new_path,target_data)

def divide_fits(target_img: Fits, flat_img: Fits, output_path: str = None):
    '''
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
    '''

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
        file_name = target_img.path[target_img.path.rfind("/") + 1:] + "_divflat"  # get file name
        new_path = output_path + file_name
    else:
        # The new file will have the same path and be named with "_divflat" at the end of it
        new_path = target_img.path[:len(target_img.path)-5] + "_divflat" + target_img.path[len(target_img.path)-5:]

    return Fits.create_fits(new_path, divided_data)
