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
    parser.add_argument("-dt", "--dark_type", help="filter dark frames from drk_path", action="store_true")
    parser.add_argument("-ft", "--flat_type", help="filter flat frames from flt_path", action="store_true")
    parser.add_argument("-w", "--write", help="write every FITS file created to disk", action="store_true")

    args = parser.parse_args()

    # arguments
    dark_path = args.drk_path
    flat_path = args.flt_path

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
    target_img = Fits(args.trg_path)

    # ini nih yang bikin lemot
    medStack_dark = darkprocessing.median_stack_fits(dark_frame_list, CONST.DARK_MEDSTACK)
    medStack_flat = darkprocessing.median_stack_fits(flat_frame_list, CONST.FLAT_MEDSTACK)

    # subtract darks
    flat_subdark = darkprocessing.subtract_fits(medStack_flat, medStack_dark, overwrite=False, output_path=Constant.FLAT_PATH)
    target_subdark = darkprocessing.subtract_fits(target_img, medStack_dark, overwrite=False, output_path=Constant.SCIENCE_PATH)

    # extract RGB
    flat_rgb = helperfunc.extract_rgb_from_fits(flat_subdark, CONST.FLATPATH_R, CONST.FLATPATH_G, CONST.FLATPATH_B) # I tried to make this look neat 
    target_rgb = helperfunc.extract_rgb_from_fits(target_subdark, CONST.TARGET_R, CONST.TARGET_G, CONST.TARGET_B)

    # write to disk
    if args.write:
        medStack_dark.diskwrite()
        medStack_flat.diskwrite()
        flat_subdark.diskwrite()
        target_subdark.diskwrite()

        for channel in flat_rgb:
            channel.diskwrite()

        for channel in target_rgb:
            channel.diskwrite()

# run main
if __name__ == "__main__":
    # exec main function
    main()
    sys.exit(0)