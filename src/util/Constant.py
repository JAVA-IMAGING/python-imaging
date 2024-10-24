class Constant:
    '''
    Store values of HEADER variables in FITS headers
    '''
    class HeaderObj:
        DARK_IMG = "dark"
        FLAT_IMG = "flat"
        BIAS_IMG = "bias"
        SCIENCE_IMG = "science"
        
        # Not all images use TARGET as reference to type, so for any new keys just put here
        TYPE_KEY = ["TARGET", "OBJECT"]
    


    # File path constatnts, leaving it here for convenience
    RESOURCE_PATH = r"resource/"
    OUTPUT_PATH = r"resource/output/"
    PNG_PATH = r"resource/output/image_png/"

    DARK_PATH = r"resource/dark_images/"
    FLAT_PATH = r"resource/flat_images/"
    BIAS_PATH = r"resource/bias_images/"
    SCIENCE_PATH = r"resource/science_images/"
    