from astropy.io import fits
from src.util.Constant import *
import os

'''
Class to handle FITS files

Current implementation opens FITS header upon initialization 
to avoid repeated open() which in turn improves performance, 
assuming memory is of no concern. Otherwise, change class to 
implement lazy-loading.
'''
class Fits:
    def __init__(self, path: str = None):
        self.path = None
        self.hdul = None
        
        if (path):
            self.fits_set(path)

    '''
    Retrieve the FITS image's type. 
    @return str: Image type of FITS object

    TODO:   Take into account different standards of storing 
            image type, not always the case it's in "TARGET"
    '''
    def fits_type(self):
            return self.hdul[0].header[Constant.HeaderObj.TYPE_KEY]
    
    '''
    Create Fits object from given path
    @arg path:  String of file path to FITS file
    @arg hdu:   Optional HDU argument for creation of new FITS
    '''
    def fits_set(self, path: str, hdu: fits.PrimaryHDU = None):
        # if given path points to existing FITS file, open HDUL
        if (self.path_check(path)):
            self.path = path
            self.hdul = fits.open(path)
        elif hdu:
            self.path = path
            self.hdul = fits.HDUList([hdu])
        else:
            raise FileNotFoundError(f"Provided path {path} is not a FITS file")

    '''
    Helper function to see header info. From what I understand,
    a FITS file can have multiple image data. Typically if we
    are looking for only the primary data it should be on index
    zero, the rest is irrelevant.
    '''
    def fits_hdul_info(self):
        self.hdul.info()

    '''
    Retrieve data from selected HDU
    @arg index:     The index of the HDU from which data is to
                    be pulled from. Default is 0 (primary HDU)
    @return lst:    The data from the selected HDU
    '''
    def get_data(self, index: int = 0):
        if (index < 0):
            raise IndexError("Invalid negative index")
        return self.hdul[index].data
    
    '''
    Write the current HDU list to a FITS file.
    @arg path:      Path to where FITS is to be written to
    @arg overwrite: Flag to overwrite existing files
    '''
    def write_to_disk(self, overwrite: bool = False):
        fits.writeto(filename=self.path, data=self.get_data(), header=self.hdul[0].header, overwrite=overwrite)

    '''
    Static method to write data into new FITS file or overwrite
    existing FITS file given in path
    @arg path:      Path to where FITS is to be written to
    @arg data:      List of data that will be storedi in this file
    @return Fits:   Creates a new Fits object with hdul and path
    '''
    @staticmethod
    def create_fits(path: str, data: list, write: bool = False):
        new_obj = Fits()
        new_obj.fits_set(path, fits.PrimaryHDU(data=data))
        return new_obj

    '''
    Method to check image type without making FITS object
    @arg path:      Complete path to FITS file
    @return str:    Image type as string
    '''
    @staticmethod
    def check_type(path: str):
        return fits.open(path)[0].header[Constant.HeaderObj.TYPE_KEY]

    '''
    Static method to check if given path is valid FITS file
    @arg path:      String of file path to FITS file
    @return bool:   True if given path points to an existing 
                    Fits file, false otherwise
    '''
    @staticmethod
    def path_check(path: str):
        if os.path.isfile(path) and path.endswith('.fits'):
            return True
        return False

    '''
    Creates FITS object for every image found in given 
    directory and return a list of FITS objects
    @arg path:      Path to directory with FITS images
    @arg type:      Type of images to collect
    @return list:   List of FITS objects
    '''
    @staticmethod
    def batch_fits(path: str, type: str):
        fits_list = []

        if (os.path.isdir(path)):
            for files in os.listdir(path):
                # find FITS with specified type
                if (Fits.path_check(path + files) and type == Fits.check_type(path + files)):
                    fits_list.append(Fits(path + files))
           
            return fits_list
        else:
            raise NotADirectoryError(f"Provided path {path} is not a directory")