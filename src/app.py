import sys
import argparse

from src.module import darkprocessing, flatprocessing
from src.util import helperfunc, outputimg
from src.util.Fits import Fits
from src.util.Constant import Constant

# code for main file goes here
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

    # thread this probably
    dark_frame_list = Fits.batchload(dark_path, dt)
    flat_frame_list = Fits.batchload(flat_path, ft)

    # ini nih yang bikin lemot
    medStack_dark = darkprocessing.median_stack_fits(dark_frame_list, Constant.DARK_PATH + "median_stacked_dark.fits")
    medStack_flat = darkprocessing.median_stack_fits(flat_frame_list, Constant.FLAT_PATH + "median_stacked_flat.fits")

    target_img = Fits(args.trg_path)

    # subtract darks
    flat_subdark = darkprocessing.subtract_fits(medStack_flat, medStack_dark, Constant.FLAT_PATH)
    target_subdark = darkprocessing.subtract_fits(target_img, medStack_dark, Constant.SCIENCE_PATH)

    # write to disk
    if args.write:
        medStack_dark.diskwrite()
        medStack_flat.diskwrite()
        flat_subdark.diskwrite()
        target_subdark.diskwrite()

# run main
if __name__ == "__main__":
    # exec main function
    main()
    sys.exit(0)