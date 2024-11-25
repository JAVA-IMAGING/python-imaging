from astropy.io import fits
import numpy as np
import os

from src.util.Constant import *

class Fits:
    """
    Class to handle FITS files
    
    Adjusted to load data, return it, and close the file for every function 
    without altering how the methods are invoked.
    """

    def __init__(self, path: str=None):
        self.path = path
        
    def fits_hdul_info(self):
        """
        Helper function to see header info.
        """
        with fits.open(self.path) as hdul:
            hdul.info()
            print(hdul[0].header)

    def bayerpat(self):
        """
        Get Bayer pattern from the FITS header.
        """
        with fits.open(self.path) as hdul:
            header = hdul[0].header
            if header.get(Constant.HeaderObj.BAYER_KEY) is not None:
                return header[Constant.HeaderObj.BAYER_KEY]
        raise ValueError(f"{Constant.HeaderObj.BAYER_KEY} not found in FITS header.")

    def get_data(self, index: int = 0):
        """
        Retrieve data from the specified HDU index.
        """
        if index < 0:
            raise IndexError("Invalid negative index")
        with fits.open(self.path) as hdul:
            return hdul[index].data
    
    def set_data(self, data: np.ndarray, index: int=0):
        """
        Set new data for a specified HDU index.
        """
        with fits.open(self.path, mode='update') as hdul:
            if index < 0 or index >= len(hdul):
                raise IndexError(f"Invalid HDU index {index}.")
            hdul[index].data = data

    def diskwrite(self, overwrite: bool = True):
        """
        Write the current data to a FITS file.
        """
        with fits.open(self.path) as hdul:
            
            fits.writeto(
                filename=self.path,
                data=hdul[0].data,
                header=hdul[0].header,
                overwrite=overwrite
            )
    
    @staticmethod
    def filecreate(path: str, data: list, header: fits.Header=None):
        """
        Create a new FITS file with the provided data and header.
        """
        hdu = fits.PrimaryHDU(data=data, header=header)
        hdu.writeto(path, overwrite=True)
        return Fits(path)

    @staticmethod
    def check_type(path: str):
        """
        Check the image type from the FITS header.
        """
        with fits.open(path, memmap=True) as hdul:
            header = hdul[0].header
            for key in Constant.HeaderObj.TYPE_KEY:
                if header.get(key) is not None:
                    return header[key]
        raise KeyError(f"Unable to find image type for {path}.")
    @staticmethod
    def check_path(path: str):
        """
        Check if the given path points to a valid FITS file.
        """
        return os.path.isfile(path) and path.endswith('.fits')

    @staticmethod
    def batchload(path: str):
        """
        Load valid FITS files from a directory.
        """
        format_path = path.replace("\\", "/")
        fits_list = []

        if os.path.isdir(format_path):
            for file_name in os.listdir(format_path):
                file_path = f"{format_path}/{file_name}"

                try:
                    with fits.open(file_path) as hdul:
                        header = hdul[0].header
                        fits_list.append(Fits(file_path))
                except Exception:
                    continue

            if fits_list:
                print(f"Batch collect found {len(fits_list)} valid FITS files in {format_path}.")
                return fits_list
            else:
                raise FileNotFoundError(f"No valid FITS files found in {format_path}.")
        else:
            raise NotADirectoryError(f"Provided path {format_path} is not a directory.")

    @staticmethod
    def load(path: str):
        """
        Load a FITS file from the given path.
        """
        format_path = path.replace("\\", "/")
        if Fits.check_path(format_path):
            return Fits(format_path)
        else:
            raise FileNotFoundError(f"Provided path {format_path} is not a valid FITS file.")