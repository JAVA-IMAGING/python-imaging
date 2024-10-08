# tests can go here, or not doesn't really matter
from src.module import *
from src.util import *

def test_Fits():
    # check HDUL info function
    # two.fits_hdul_info()

    # check get_data from FITS object
    # print(two.get_data())

    # check batch loading FITS
    for files in (Fits.batch_fits(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)):
        print(files.path)


# ngetes dark_img
def test_dark_img():
    # CHECKING MAKING MASTER DARK
    # fits_files = Fits.batch_fits(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)
    # output_file = Constant.OUTPUT_PATH + "ngentot_gasih.fits" # or change this to a path

    # make_dark = median_stack_fits(fits_files, output_file)
    
    # tulis ke kaset
    # make_dark.write_to_disk()

    # CHECKING SUBTRACT DARK
    one = Fits(Constant.DARK_PATH + "dark_3_000_1681706713.fits")
    two = Fits(r"c:\Users\bloon\Desktop\project-ctn-tcom-018-iit\java-imaging\src\test\fits\20181002_16.fits")
    three = Fits(Constant.DARK_PATH + "dark_3_001_1681706376.fits")

    result = subtract_dark(one, one)

    print(result.path)
    result.write_to_disk()
    print(result.get_data())



if __name__ == "__main__":
    # test_Fits()
    test_dark_img()