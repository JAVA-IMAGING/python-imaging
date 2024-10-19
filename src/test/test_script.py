# tests can go here, or not doesn't really matter
from src.module import *
from src.util import *

def test_Fits():
    # check HDUL info function
    # two.fits_hdul_info()

    # check get_data from FITS object
    two = Fits(r"c:\Users\bloon\Desktop\project-ctn-tcom-018-iit\java-imaging\src\test\fits\20181002_16.fits")
    print(two.get_data())

    # check batch loading FITS
    for files in (Fits.batch_fits(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)):
        print(files.path)

# ngetes dark_img
def test_dark_img():
    # CHECKING MAKING MASTER DARK
    fits_files = Fits.batch_fits(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)
    output_file = Constant.OUTPUT_PATH + "ngentot_gasih.fits" # or change this to a path

    make_dark = median_stack_fits(fits_files, output_file)
    
    # tulis ke kaset
    make_dark.write_to_disk()

    # CHECKING SUBTRACT DARK
    one = Fits(Constant.DARK_PATH + "dark_3_000_1681706713.fits")
    two = Fits(r"c:\Users\bloon\Desktop\project-ctn-tcom-018-iit\java-imaging\src\test\fits\20181002_16.fits")
    three = Fits(Constant.DARK_PATH + "dark_3_001_1681706376.fits")

    result = subtract_dark(one, one)

    print(result.path)
    result.write_to_disk()
    print(result.get_data())

def test_generate_img():
    path = r"E:\IPRO Images\2023-05-23_04-03-47_observation_M101\02-images-adjust-focus\img-0001r.fits"
    img_test = Fits(path)
    generate_img(img_test)

def test_batch_load():
    # path = Constant.RESOURCE_PATH + "fits/"
    path = Constant.DARK_PATH
    Fits.batch_fits(path, "dark")

if __name__ == "__main__":
    # test_Fits()
    # test_dark_img()
    # test_generate_img()
    test_batch_load()