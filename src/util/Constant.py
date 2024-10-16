class Constant:
    '''
    Store values of HEADER variables in FITS headers
    '''
    class HeaderObj:
        DARK_IMG = "dark"
        FLAT_IMG = "flat"
        BIAS_IMG = "bias"
        SCIENCE_IMG = "science"
        
        # Not all images use TARGET as reference to type
        TYPE_KEY = "TARGET"
    

    '''
    File path constatnts, leaving it here in case we ever use it
    '''
    DARK_PATH = r"resource/dark_images/"
    FLAT_PATH = r"resource/flat_images/"
    BIAS_PATH = r"resource/bias_images/"
    SCIENCE_PATH = r"resource/science_images/"
    OUTPUT_PATH = r"resource/output/"
