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
    boost = 5   # add option to set this later

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
    sci_img_list = Fits.batchload(target_path)

    # BAYER PATTERN MUST MATCH!!
    darkpat = dark_frame_list[0].bayerpat()
    flatpat = flat_frame_list[0].bayerpat()
    scipat = sci_img_list[0].bayerpat()
    bayermatch = darkpat == flatpat and scipat == darkpat

    if not bayermatch:
        raise ValueError("Bayer pattern mismatch!")

    # median stack flat and dark frames
    medStack_dark = darkprocessing.median_stack_fits(dark_frame_list, CONST.DARK_MEDSTACK)
    medStack_flat = darkprocessing.median_stack_fits(flat_frame_list, CONST.FLAT_MEDSTACK)

    # Green tint is noraml due to more green pixels than the others, fixed in post processing
    # Still using subtraction per channel cuz it look nice
    #darkprocessing.subtract_fits(medStack_flat, medStack_dark)
    #darkprocessing.subtract_fits(sci_img_list, medStack_dark)

    ### pre-process per channel (switch this to above if you want proper/expected result) ###
    dark_rgb = helperfunc.extract_rgb_from_fits(medStack_dark, Constant.DARK_PATH)
    flat_rgb = helperfunc.extract_rgb_from_fits(medStack_flat, Constant.FLAT_PATH)
    
    for i in range(0,3):
        darkprocessing.subtract_fits(flat_rgb[i], dark_rgb[i])
        flatprocessing.normalize_fits(flat_rgb[i])
    ### --------------------------------------------------------------------------------- ###

    # process science images
    for i in range(0, len(sci_img_list)):
        fp = sci_img_list[i].path
        fn = fp[fp.rfind("/") + 1: len(fp) - 5] # get filename

        sci_img_list[i] = helperfunc.extract_rgb_from_fits(sci_img_list[i], Constant.SCIENCE_PATH) + (fn,) # tuple is now (r, g, b, fn)

        for j in range(0, 3):
            darkprocessing.subtract_fits(sci_img_list[i][j], dark_rgb[j])   # subtract darks per channel, move to outer loop for raw subtraction
            flatprocessing.divide_fits(sci_img_list[i][j], flat_rgb[j])

        outputimg.generate_PNG(sci_img_list[i][3] + "_pre_align.png", sci_img_list[i][0], sci_img_list[i][1], sci_img_list[i][2], boost_factor=boost)

    # write to disk
    if args.write:
        medStack_dark.diskwrite()   # write median-stacked dark frame
        medStack_flat.diskwrite()   # write median-stacked flat frame

        for channel in flat_rgb:
            channel.diskwrite()     # write dark processed and normalized flat channels

        for i in range(0, len(sci_img_list)):
            for j in range(0, 3):
                sci_img_list[i][j].diskwrite()

# run main
if __name__ == "__main__":
    # exec main function
    main()
    sys.exit(0)