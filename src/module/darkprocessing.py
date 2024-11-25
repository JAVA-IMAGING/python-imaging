import numpy as np
from concurrent.futures import ThreadPoolExecutor

from src.util.Fits import *

def load_fits_data(fits_file):
    """Helper function to get FITS data from an open FITS object."""
    return fits_file.get_data()

def median_stack_fits(fits_files: list[Fits], output_file: str):
    """
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
        Newly created Fits object with median-stacked data
    """

    # Get a copy of header to retain information from original FITS
    with fits.open(fits_files[0].path) as hdul:
        header_copy = hdul[0].header

    # List to store data arrays from FITS files
    image_data = []

    # Read each FITS file and append the data to the list
    for file in fits_files:
        image_data.append(file.get_data())

    # tried threading, kek tai anjing
    '''
    with ThreadPoolExecutor() as executor:
        image_data = list(executor.map(load_fits_data, fits_files))

    # Stack the images and compute the median along the stack axis
    image_data = np.stack(image_data, axis=0)
    '''

    # Stack the images and compute the median along the stack axis
    stacked_median = np.median(np.array(image_data), axis=0)

    # Return new Fits object with the calculated data
    return Fits.filecreate(output_file, stacked_median, header_copy)


def median_stack_fits_directory(directory: str, output_file: str, type: str):
    """
    Create a median-stacked image from all FITS images of a specified type (red, green, or blue)
    in a specified directory using a memory-efficient approach.

    params
    ------
    directory: str
        Path to the directory containing FITS files.
    output_file: str
        Path to where the output is going to be written.
    type: str
        The type of image to process ("red", "green", or "blue").

    return
    ------
    None
        The result is written to `output_file`.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Provided path '{directory}' is not a valid directory.")

    type_suffix_map = {
        "red": "_r.fits",
        "green": "_g.fits",
        "blue": "_b.fits"
    }
    if type not in type_suffix_map:
        raise ValueError(f"Invalid type '{type}'. Must be one of 'red', 'green', or 'blue'.")

    suffix = type_suffix_map[type]

    fits_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(suffix)]
    if not fits_files:
        raise ValueError(f"No FITS files ending with '{suffix}' found in the directory '{directory}'.")

    header_copy = None
    image_shape = None

    # Read files one by one to determine shape and header (from the first file)
    for i, file in enumerate(fits_files):
        with fits.open(file) as hdul:
            data = hdul[0].data
            if header_copy is None:
                header_copy = hdul[0].header
                image_shape = data.shape
            elif data.shape != image_shape:
                raise ValueError(f"File '{file}' has a different shape from the first FITS file.")

    # Median calculation by blocks
    temp_data = np.zeros(image_shape, dtype=np.float64)
    file_count = 0

    for file in fits_files:
        with fits.open(file) as hdul:
            temp_data += hdul[0].data
        file_count += 1

    # Compute final median
    stacked_median = temp_data / file_count

    # Write the result to a FITS file
    hdu = fits.PrimaryHDU(data=stacked_median, header=header_copy)
    hdu.writeto(output_file, overwrite=True)

    print(f"Median-stacked FITS file created at {output_file}.")



def mean_stack_fits(fits_files: list[Fits], output_file: str):
    """
    Create a mean-stacked image from a list of FITS images

    params
    ------
    fits_file: list[Fits]
        List of FITS objects to be median-stacked
    output_file: str
        Path to where the output is going to be written

    return
    ------
    Fits object
    """

    # List to store data arrays from FITS files
    image_data = []
    # Get a copy of header to retain information from original FITS
    header_copy = fits_files[0].hdul[0].header

    # Read each FITS file and append the data to the list
    for file in fits_files:
        image_data.append(file.get_data())

    stdev = np.std(np.array(image_data), axis=0)
    mean = np.mean(np.array(image_data), axis=0)

    # Create a mask to filter out outliers, and average the values that are left
    mask = np.abs(image_data - mean) <= 1.5 * stdev  # formula taken from Swift team's code
    masked_data = np.where(mask, image_data, np.nan)  # this was what Elaine meant by using mask
    mean_masked = np.nanmean(masked_data, axis=0)

    return Fits.filecreate(output_file, mean_masked, header_copy)


def subtract_fits(target_img: Fits, dark_img: Fits, overwrite: bool=True, output_path: str=None):
    """
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
    """

    dark_data = np.array(dark_img.get_data())
    target_data = np.array(target_img.get_data())

    dark_dimension = (dark_data.shape[0], dark_data.shape[1])
    target_dimension = (target_data.shape[0], target_data.shape[1])

    # ensure same image dimensions
    if (dark_dimension != target_dimension):
        raise BaseException(
            f"Different image dimensons!\ndark image dimension: {dark_dimension}\ntarget image dimension: {target_dimension}")

    target_data = np.subtract(target_data, dark_data)
    target_data = np.where(target_data < 0, 0, target_data) # for some reason this fixes the white-washing

    if overwrite:
        target_img.set_data(target_data)
    else:
        # Get a copy of header to retain information from original FITS
        header_copy = target_img.hdul[0].header

        # if output path is specified, do as so
        if (output_path):
            file_name = target_img.path[target_img.path.rfind("/") + 1:len(target_img.path) - 5] + "_subdark.fits"  # get file name
            new_path = output_path + file_name
        # the new file will have the same path and named with "_subdark" at the end of it
        else:
            new_path = target_img.path[:len(target_img.path) - 5] + "_subdark.fits"

        return Fits.filecreate(new_path, target_data, header_copy)
