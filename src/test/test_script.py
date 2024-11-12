# tests can go here, or not doesn't really matter
from src.module import darkprocessing, flatprocessing
from src.util import helperfunc, Fits, Constant, outputimg

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
    outputimg(img_test)

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

def test_teddy():
    # dark_list = Fits.batchload(r"E:/IPRO Images/expert-mode/dark-25C/no_flip/")

    # master_dark_path = Constant.DARK_PATH + "master_dark.fits"
    # master_dark = median_stack_fits(dark_list, master_dark_path)
    # print(f"master dark data:\n{master_dark.get_data()}\n")

    # target_img = Fits(r"E:\IPRO Images\2023-05-23_04-03-47_observation_M101\01-images-initial\img-0002r.fits")
    # print(f"target image data:\n{target_img.get_data()}\n")
    # target_img.fits_hdul_info()
    # generate_img(target_img)

    # target_subdark = darkprocessing.subtract_fits(target_img, master_dark, Constant.OUTPUT_PATH)
    # print(f"subtracted data:\n{target_subdark.get_data()}\n")

    # target_subdark.diskwrite()
    # generate_img(target_subdark)

    # path = Constant.RESOURCE_PATH + "fits/"
    # dark_list = Fits.batchload(path, Constant.HeaderObj.DARK_IMG)

    # mean_dark = mean_stack_fits(dark_list, Constant.DARK_PATH + "mean_dark.fits")
    # median_dark = median_stack_fits(dark_list, Constant.DARK_PATH + "median_dark.fits")

    # generate_img(mean_dark, 100)
    # generate_img(median_dark, 100)

    test = Fits(r"C:\Users\bloon\Desktop\python-imaging\resource\actual_images\flat-5sheets\no_flip\IMG_0005.fits")
    print(test.bayerpat())

    red_channel = Constant.FLAT_PATH + "red_channel.fits"
    green_channel = Constant.FLAT_PATH + "green_channel.fits"
    blue_channel = Constant.FLAT_PATH + "blue_channel.fits"

    result = helperfunc.extract_rgb_from_fits(test, red_channel, green_channel, blue_channel)

    for channels in result:
        print("HADIR")

    pass

if __name__ == "__main__":
    # test_Fits()
    # test_darkprocessing()
    # test_generate_img()
    # test_batch_load()
    # test_actual_processing()
    test_teddy()