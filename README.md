#   python-imaging
Rebrand to Python Imaging, still hoping to process astro-pics

## Table of Contents
1. [Overview](#overview)
2. [Packages used](#packages-used)
3. [Project Setup](#project-setup)

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