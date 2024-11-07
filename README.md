#   python-imaging
Rebrand to Python Imaging, still hoping to process astro-pics

## Table of Contents
1. [Overview](#overview)
2. [Packages used](#packages-used)
3. [Project Setup](#project-setup)
4. [Usage](#usage)
5. [Extra](#extra)


##  Overview

Just process the image

##  Packages used

List of packages used in this project can be found [here](./requirements.txt)

##  Project Setup

### Prerequisites

- Python3: [[download link]](https://www.python.org/downloads/) | [[Windows setup]](https://docs.python.org/3/using/windows.html) | [[Mac setup]](https://docs.python.org/3/using/mac.html)

### Installation

1. Clone the repository

    `git clone https://github.com/JAVA-IMAGING/python-imaging.git`

2. Navigate to project directory

    `cd ./python-imaging`

3. Install required packages

    `pip install -r requirements.txt`

4. Build project dependencies

    `pip install -e .`

    _This step fixes issues when sibling packages try to import from one another. \
     Consider a project management tool in the future, but this should suffice for now._

### Usage

1. Navigate to project directory

    `cd ./python-imaging`

2. Execute the help command `python src/app.py --help` or `python src/app.py -h`

3. Usage: `app.py [-h] [-dt] [-ft] [-w] drk_path flt_path trg_path`

    positional arguments:
    - `drk_path` path to directory containing dark frames
    - `flt_path` path to directory containing flat frames
    - `trg_path` path to target image for processing

    options:
    - `-h`, `--help`        show this help message and exit
    - `-dt`, `--dark_type`  filter dark frames from `drk_path`
    - `-ft`, `--flat_type`  filter flat frames from `flt_path`
    - `-w`, `--write`       write every FITS file created to disk

### Extra

Link of images for testing can be found [here](https://iit0-my.sharepoint.com/:f:/g/personal/wwardhana_hawk_iit_edu/EsHAoRq5BUBHkgIPb5H6_vsBGeuHyavdDJV1L-zBt-4YEg?e=XDoTTP)