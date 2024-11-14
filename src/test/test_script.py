# tests can go here, or not doesn't really matter
import timeit

from src.module import darkprocessing, flatprocessing
from src.util.Fits import *
from src.util.Constant import *
from src.util import helperfunc, outputimg

# returns the time 
def time():
    return timeit.default_timer()

def test_Fits():
    # check HDUL info function
    # two.fits_hdul_info()

    # check get_data from FITS object
    two = Fits(r"c:\Users\bloon\Desktop\project-ctn-tcom-018-iit\java-imaging\src\test\fits\20181002_16.fits")
    print(two.get_data())

    # check batch loading FITS
    for files in (Fits.batchload(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)):
        print(files.path)

# ngetes darkprocessing
def test_darkprocessing():
    # CHECKING MAKING MASTER DARK
    fits_files = Fits.batchload(Constant.DARK_PATH, Constant.HeaderObj.DARK_IMG)
    output_file = Constant.OUTPUT_PATH + "ngentot_gasih.fits" # or change this to a path

    make_dark = darkprocessing.median_stack_fits(fits_files, output_file)
    
    # tulis ke kaset
    make_dark.diskwrite()

    # CHECKING SUBTRACT DARK
    one = Fits(Constant.DARK_PATH + "dark_3_000_1681706713.fits")
    two = Fits(r"c:\Users\bloon\Desktop\project-ctn-tcom-018-iit\java-imaging\src\test\fits\20181002_16.fits")
    three = Fits(Constant.DARK_PATH + "dark_3_001_1681706376.fits")

    result = darkprocessing.subtract_fits(one, one)

    print(result.path)
    result.diskwrite()
    print(result.get_data())

def test_generate_img():
    path = r"E:\IPRO Images\2023-05-23_04-03-47_observation_M101\02-images-adjust-focus\img-0001r.fits"
    img_test = Fits(path)

def test_batch_load():
    path1 = Constant.RESOURCE_PATH + "fits/"
    path2 = Constant.DARK_PATH
    path3 = Constant.RESOURCE_PATH + "fits/"

    """
    collect_dark = Fits.batchload(path1, "dark")
    master_dark = median_stack_fits(collect_dark, Constant.OUTPUT_PATH + "master_dark.fits")
    generate_img(master_dark, 150)
    """

    """
    collect_flat = Fits.batchload(path3, "flat")
    master_flat = median_stack_fits(collect_flat, Constant.OUTPUT_PATH + "master_flat.fits")
    generate_img(master_flat)
    """

    # this is from the SD card
    test_dir = Fits.batchload(r"E:/IPRO Images/expert-mode/dark-25C/no_flip/")

def test_actual_processing():
    path = Constant.RESOURCE_PATH + "fits/"
    output = Constant.OUTPUT_PATH + "master_dark_test.fits"
    dark_lists = Fits.batchload(path, Constant.HeaderObj.DARK_IMG)

    master_dark = darkprocessing.median_stack_fits(dark_lists, output)

    target_img = Fits(r"C:\Users\bloon\Desktop\python-imaging\resource\fits\20181005_39.fits")
    subtracted_image = darkprocessing.subtract_fits(target_img, master_dark)

    print(master_dark.get_data())

    # bandingin cok
    # generate_img(target_img)
    # generate_img(subtracted_image)
    # generate_img(master_dark)

def random_test():
    path = r"resource\testfolder\dark 1 sec\no_flip"
    batch = Fits.batchload(path)
    # print(batch[0].bayerpat())
    # print(batch[0].get_data())

    fp = r"resource\dark 1 sec\no_flip\IMG_0001.fits"
    # print(os.path.isfile(fp))
    # print(fp.endswith(".fits"))

    median = darkprocessing.median_stack_fits(batch, Constant.DARK_PATH + "ngentot.fits")

    # sum = 0
    # for i in range(0, 50):
    #     start = time()
    #     median = darkprocessing.median_stack_fits(batch, Constant.DARK_PATH + "ngentot.fits")
    #     end = time()
    #     sum = sum + (end - start)

    # print(f"Average runtime: {sum / 50}")

    print(median.bayerpat())
    # print(median.get_data())
    pass

def output_test():
    darks = Fits.batchload(r"resource\testfolder\dark-25C\no_flip")
    flats = Fits.batchload(r"resource\testfolder\Flat 4 Sheets no_flip")
    sci = Fits(r"resource\testfolder\scimage\img-0001r.fits")

    dpath = Constant.DARK_PATH + "dark_medstack.fits"
    fpath = Constant.FLAT_PATH + "flat_medstack.fits"

    # MEDIAN-STACKING FLATS AND DARKS
    meddark = darkprocessing.median_stack_fits(darks, dpath)
    medflat = darkprocessing.median_stack_fits(flats, fpath)

    # DARK FRAME COLOR EXTRACTION FOR PNG IMAGE
    darkpath_r = Constant.DARK_PATH + "dark_r.fits"
    darkpath_g = Constant.DARK_PATH + "dark_g.fits"
    darkpath_b = Constant.DARK_PATH + "dark_b.fits"
    dark_rgb = helperfunc.extract_rgb_from_fits(meddark, darkpath_r, darkpath_g, darkpath_b)
    outputimg.generate_PNG("dark_medstack.png", dark_rgb[0], dark_rgb[1], dark_rgb[2])


    # FLAT FRAME COLOR EXTRACTION PRE-SUBDARK
    flatpath_r = Constant.FLAT_PATH + "flat_r.fits"
    flatpath_g = Constant.FLAT_PATH + "flat_g.fits"
    flatpath_b = Constant.FLAT_PATH + "flat_b.fits"
    flat_rgb = helperfunc.extract_rgb_from_fits(medflat, flatpath_r, flatpath_g, flatpath_b)
    outputimg.generate_PNG("flat_medstack.png", flat_rgb[0], flat_rgb[1], flat_rgb[2])

    # DARK FRAME SUBTRACTION
    subflat = darkprocessing.subtract_fits(medflat, meddark, overwrite=False)

    # FLAT FRAME COLOR EXTRACTION POST-SUBDARK
    subflatpath_r = Constant.FLAT_PATH + "subflat_r.fits"
    subflatpath_g = Constant.FLAT_PATH + "subflat_g.fits"
    subflatpath_b = Constant.FLAT_PATH + "subflat_b.fits"
    subflat_rgb = helperfunc.extract_rgb_from_fits(subflat, subflatpath_r, subflatpath_g, subflatpath_b)
    outputimg.generate_PNG("flat_medstack_subdark.png", subflat_rgb[0], subflat_rgb[1], subflat_rgb[2])

    # NORMALIZING FLATS
    for channel in subflat_rgb:
        flatprocessing.normalize_fits(channel)

    # SCIENCE IMAGE COLOR EXTRACTION PRE-SUBDARK
    scipath_r = Constant.SCIENCE_PATH + "sci_r.fits"
    scipath_g = Constant.SCIENCE_PATH + "sci_g.fits"
    scipath_b = Constant.SCIENCE_PATH + "sci_b.fits"
    sci_rgb = helperfunc.extract_rgb_from_fits(sci, scipath_r, scipath_g, scipath_b)
    outputimg.generate_PNG("sci_img.png", sci_rgb[0], sci_rgb[1], sci_rgb[2])

    # they dont match bruh 😭🙏
    print(sci.bayerpat())
    print(meddark.bayerpat())

    # bismillah ini bener
    for i in range(0,3):
        darkprocessing.subtract_fits(sci_rgb[i], dark_rgb[i])
        flatprocessing.divide_fits(sci_rgb[i], subflat_rgb[i])
    
    outputimg.generate_PNG("sci_normalized_subdark.png", sci_rgb[0], sci_rgb[1], sci_rgb[2])

    pass

if __name__ == "__main__":
    # test_Fits()
    # test_darkprocessing()
    # test_generate_img()
    # test_batch_load()
    # test_actual_processing()
    # random_test()
    output_test()