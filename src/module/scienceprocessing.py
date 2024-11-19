import astroalign
import numpy as np

from src.util.Fits import *

def find_matrix_t(target_fits: Fits, reference_fits: Fits):
    """
    get transformation matrix
    """

    target_data = np.array(target_fits.get_data())
    reference_data = np.array(reference_fits.get_data())

    # use 3 stddevs to consider star pixels
    t_matrix = astroalign.find_transform(target_data, reference_data, detection_sigma=3) 
    return t_matrix

def align_fits(target_fits:Fits, matrix_t, overwrite: bool=True, output_path: str=None):
    """
    apply transformation matrix to FITS
    """

    target_data = np.array(target_fits.get_data())
    shape = np.zeros(target_data.shape)
    transform = astroalign.apply_transform(matrix_t, target_data, shape)[0]

    if overwrite:
        target_fits.set_data(transform)
    else:
        # Get a copy of header to retain information from original FITS
        header_copy = target_fits.hdul[0].header

        # if output path is specified, do as so
        if (output_path):
            file_name = target_fits.path[target_fits.path.rfind("/") + 1:len(target_fits.path) - 5] + "_align.fits"  # get file name
            new_path = output_path + file_name
        # the new file will have the same path and named with "_align" at the end of it
        else:
            new_path = target_fits.path[:len(target_fits.path) - 5] + "_align.fits"

        return Fits.filecreate(new_path, target_data, header_copy)