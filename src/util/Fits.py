from astropy.io import fits
import numpy as np
import os

from src.util.Constant import *

class Fits:
    """
    Class to handle FITS files
    
    Current implementation opens FITS header upon initialization 
    to avoid repeated open() which in turn improves performance, 
    assuming memory is of no concern. Otherwise, change class to 
    implement lazy-loading.
    """
    
    def __init__(self, path: str=None):
        self.path = None
        self.hdul = None
        
        if (path):
            self.set(path)
    
    # TODO: Handle the case when creating a new FITS object from a newly created FITS data is assigned 
    #       to an existing path. For now, just dont't be dumb and make sure the path is for its own.
    def set(self, path: str, hdu: fits.PrimaryHDU=None):
        """
        Create Fits object from given path

        params
        ------
        path: str
            File path to FITS file
        hdu: PrimaryHDU, optional
            Optional HDU argument for creation of new FITS
        """
    
        # change windows path to POSIX, for consistency sake
        format_path = path.replace("\\", "/")
        
        # if given path points to existing FITS file, open HDUL
        if (self.check_path(format_path)) and not hdu:
            self.path = format_path
            self.hdul = fits.open(format_path)
        elif hdu:
            self.path = format_path
            self.hdul = fits.HDUList([hdu])
        else:
            raise FileNotFoundError(f"Provided path {format_path} is not a FITS file")

    def fits_hdul_info(self):
        """
        Helper function to see header info. From what I understand, a FITS file can have multiple image data.\n    
        Typically if we are looking for only the primary data it should be on index zero, the rest is irrelevant.
        """
        
        self.hdul.info()
        print(self.hdul[0].header)

    def bayerpat(self):
        """
        get bayer pattern
        """

        header = self.hdul[0].header

        if header.get(Constant.HeaderObj.BAYER_KEY) is not None:
            return header[Constant.HeaderObj.BAYER_KEY]
        
        raise ValueError(f"{Constant.HeaderObj.BAYER_KEY} not found in FITS header.")

    def get_data(self, index: int = 0):
        """
        Retrieve data from selected HDU

        params
        ------
        index: int
            The index of the HDU from which data is to be pulled from. Default is 0 (primary HDU)

        return
        ------
        list
            The data from the selected HDU in list form
        """

        if (index < 0):
            raise IndexError("Invalid negative index")
        return self.hdul[index].data
    
    def set_data(self, data: np.ndarray, index: int=0):
        """
        Set new data for a specified HDU in the FITS file.

        params
        ------
        data: np.ndarray
            New data array to set in the FITS file.
        index: int, optional
            The index of the HDU to modify. Default is 0 (primary HDU).
        """

        if index < 0 or index >= len(self.hdul):
            raise IndexError(f"Invalid HDU index {index}.")
        self.hdul[index].data = data
        print(f"Data successfully set for HDU index {index} in FITS file {self.path}.")
    
    def diskwrite(self, overwrite: bool = True):
        """
        Write the current HDU list to a FITS file.

        params
        ------
        overwrite: bool, optional
            Flag to overwrite existing files, default to True
        """

        fits.writeto(filename=self.path, data=self.get_data(), header=self.hdul[0].header, overwrite=overwrite)
        print(f"FITS file succesfully written to {self.path}")

    @staticmethod
    def filecreate(path: str, data: list, header: fits.Header=None):
        """
        Static method to write data into new FITS file or overwrite existing FITS file given in path

        params
        ------
        path: str
            Path to where FITS is to be written to
        data: list
            List of data that will be stored in this file
        header: fits.Header
            Header of a FITS file with information to be carried over
        
        return
        ------
        Fits
            Creates a new Fits object with hdul and path
        """
        
        new_obj = Fits()
        new_obj.set(path, fits.PrimaryHDU(data=data, header=header))
        return new_obj

    @staticmethod
    def check_type(path: str):
        """
        Method to check image type without making FITS object

        params
        ------
        path: str
            Complete path to FITS file

        return
        ------
        str
            Image type as string
        """

        header = fits.open(path)[0].header

        # Checks through list of "known" key values that stores the image type in the FITS file we handle
        for key in Constant.HeaderObj.TYPE_KEY:
            if header.get(key) is not None:
                return header[key]
        
        raise KeyError(f"Unable to find image type of {path}. Perhaps a different key is used to store the image type?")

    @staticmethod
    def check_path(path: str):
        """
        Static method to check if given path is valid FITS file

        params
        ------
        path: str
            String of file path to FITS file

        return
        ------
        bool
            True if given path points to an existing Fits file, false otherwise
        """

        if os.path.isfile(path) and path.endswith('.fits'):
            return True
        return False

    @staticmethod
    def batchload(path: str, type: str="N/A"):
        """
        Creates FITS object for every image found in given directory and return a list of FITS objects

        params
        ------
        path: str
            Path to directory with FITS images
        type: str, optional
            Type of images to collect, default assumes that we are pulling everything in the given directory

        return
        ------
        list
            List of Fits objects
        """

        # change to POSIX format for consistency
        format_path = path.replace("\\", "/")

        fits_list = []

        if (os.path.isdir(path)):
            for files in os.listdir(path):
                if (Fits.check_path(f"{path}/{files}") and type == 'N/A') :
                    fits_list.append(Fits(f"{path}/{files}"))
                elif (Fits.check_path(f"{path}/{files}") and type == Fits.check_type(f"{path}/{files}")):
                    fits_list.append(Fits(f"{path}/{files}"))

            print(f"Batch collect found {len(fits_list)} {type} files in {path}")

            return fits_list
        else:
            raise NotADirectoryError(f"Provided path {path} is not a directory")
