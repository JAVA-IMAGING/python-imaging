import astroalign
import numpy as np
from src.util.Fits import *
def find_matrix_t(target_fits: Fits, reference_fits: Fits):
    """
    Get transformation matrix.
    This function now handles the case when the transformation fails due to insufficient stars.
    """

    # Ensure data is in native byte order
    target_data = np.asarray(target_fits.get_data(), dtype=target_fits.get_data().dtype.newbyteorder('='))
    reference_data = np.asarray(reference_fits.get_data(), dtype=reference_fits.get_data().dtype.newbyteorder('='))

    try:
        # Use 3 stddevs to consider star pixels
        t_matrix = astroalign.find_transform(target_data, reference_data, detection_sigma=3)
        return t_matrix
    except Exception as e:
        print(f"Error during alignment: {e}")
        # Return None or some indication that the alignment failed
        return None

def align_fits(target_fits: Fits, matrix_t, overwrite: bool = True, output_path: str = None):
    """
    Apply transformation matrix to FITS.
    Handles the case where the transformation matrix could not be computed.
    """

    if matrix_t is None:
        print("Skipping alignment: Transformation matrix is None.")
        return None

    # Ensure data is in native byte order
    target_data = np.asarray(target_fits.get_data(), dtype=target_fits.get_data().dtype.newbyteorder('='))
    shape = np.zeros(target_data.shape, dtype=target_data.dtype)

    try:
        # Apply transformation to the target data
        transform = astroalign.apply_transform(matrix_t, target_data, shape)[0]  # index 0 is the actual matrix

        if overwrite:
            target_fits.set_data(transform)
        else:
            # Get a copy of header to retain information from original FITS
            header_copy = target_fits.hdul[0].header

            # If output path is specified, use that
            if output_path:
                file_name = target_fits.path[target_fits.path.rfind("/") + 1:len(target_fits.path) - 5] + "_align.fits"
                new_path = output_path + file_name
            else:
                # Default path if not specified
                new_path = target_fits.path[:len(target_fits.path) - 5] + "_align.fits"

            return Fits.filecreate(new_path, transform, header_copy)

    except Exception as e:
        print(f"Error during applying transformation: {e}")
        return None
