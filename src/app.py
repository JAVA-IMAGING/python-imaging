import sys
import argparse

from src.module import darkprocessing, flatprocessing
from src.util import helperfunc, outputimg
from src.util.Fits import Fits
from src.util.Constant import Constant

# TODO: Consider using logging to better organize the execution and any errors arising.
#       For now, the prints serve as our only logs.

# cmd constants, refer here
# TODO: Choose a better name, it's similar to Constant. Moving it to Constant is prolly a better idea.
class CONST:
    # path to store median-stacked frames
    DARK_MEDSTACK = Constant.DARK_PATH + "median_stacked_dark.fits"
    FLAT_MEDSTACK = Constant.FLAT_PATH + "median_stacked_flat.fits"

    # path to store color channels extracted from dark frames
    DARK_R = Constant.DARK_PATH + "dark_r.fits"
    DARK_G = Constant.DARK_PATH + "dark_g.fits"
    DARK_B = Constant.DARK_PATH + "dark_b.fits"

    # path to store color channels extracted from flat frames
    FLATPATH_R = Constant.FLAT_PATH + "flat_r.fits"
    FLATPATH_G = Constant.FLAT_PATH + "flat_g.fits"
    FLATPATH_B = Constant.FLAT_PATH + "flat_b.fits"

    # path to store color channels extracted from target/science image
    # TODO: make up your mind whether to call it science or target
    TARGET_R = Constant.SCIENCE_PATH + "sci_r.fits"
    TARGET_G = Constant.SCIENCE_PATH + "sci_g.fits"
    TARGET_B = Constant.SCIENCE_PATH + "sci_b.fits"

def main():
    parser = argparse.ArgumentParser()
    
    # declaring positional arguments needed
    parser.add_argument("drk_path", help="path to directory containing dark frames", type=str) 
    parser.add_argument("flt_path", help="path to directory containing flat frames", type=str) 
    parser.add_argument("trg_path", help="path to target image for processing", type=str)      # For now, only point to a single image  

    # declaring optional arguments / flags
    # TODO: add optional arg for boost factor, gamma, etc.
    parser.add_argument("-dt", "--dark_type", help="filter dark frames from drk_path", action="store_true")
    parser.add_argument("-ft", "--flat_type", help="filter flat frames from flt_path", action="store_true")
    parser.add_argument("-w", "--write", help="write every FITS file created to disk", action="store_true")

    args = parser.parse_args()

    # arguments
    # format path to POSIX
    dark_path = args.drk_path.replace("\\", "/")
    flat_path = args.flt_path.replace("\\", "/")
    target_path = args.trg_path.replace("\\", "/")

    # flags
    dt = "N/A"
    ft = "N/A"

    if args.dark_type:
        dt = Constant.HeaderObj.DARK_IMG
        print(f"filtering dark frames from directory {args.drk_path}")

    if args.flat_type:
        ft = Constant.HeaderObj.FLAT_IMG
        print(f"filtering flat frames from directory {args.flt_path}")

    dark_frame_list = Fits.batchload(dark_path, dt)
    flat_frame_list = Fits.batchload(flat_path, ft)
    target_img = Fits(target_path)

    # median stack flat and dark frames
    medStack_dark = darkprocessing.median_stack_fits(dark_frame_list, CONST.DARK_MEDSTACK)
    medStack_flat = darkprocessing.median_stack_fits(flat_frame_list, CONST.FLAT_MEDSTACK)

    # extract RGB channels
    dark_rgb = helperfunc.extract_rgb_from_fits(medStack_dark, CONST.DARK_R, CONST.DARK_G, CONST.DARK_B)
    flat_rgb = helperfunc.extract_rgb_from_fits(medStack_flat, CONST.FLATPATH_R, CONST.FLATPATH_G, CONST.FLATPATH_B)  
    target_rgb = helperfunc.extract_rgb_from_fits(target_img, CONST.TARGET_R, CONST.TARGET_G, CONST.TARGET_B)

    # TODO: think of a way to avoid this when bayer pattern matches, I CBA rn
    for i in range(0, 3):
        # subtract dark per channel, will work despite bayer pattern mismatch
        darkprocessing.subtract_fits(flat_rgb[i], dark_rgb[i])
        darkprocessing.subtract_fits(target_rgb[i], dark_rgb[i])

        # normalize flats as well
        flatprocessing.normalize_fits(flat_rgb[i])

        # flat correct science
        flatprocessing.divide_fits(target_rgb[i], flat_rgb[i])

    # setup image generation
    name = target_path[target_path.rfind("/") + 1: len(target_path) - 5] + ".png"
    outputimg.generate_PNG(name, target_rgb[0], target_rgb[1], target_rgb[2], boost_factor=8)

    # write to disk
    if args.write:
        medStack_dark.diskwrite()   # write median-stacked dark frame
        medStack_flat.diskwrite()   # write median-stacked flat frame

        for channel in flat_rgb:
            channel.diskwrite()     # write dark processed and normalized flat channels

        for channel in target_rgb:
            channel.diskwrite()     # write dark and flat processed target channels

# run main
if __name__ == "__main__":
    # exec main function
    main()
    sys.exit(0)