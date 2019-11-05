# planvec
Vectorizes a captured image of a drawn construction plan component.

## Installation
1) Install **pyenv** and python version **3.6.9**.  
    For instructions, see https://github.com/pyenv/pyenv.
2) Install **pipenv** and do ```pipenv install``` before ```pipenv shell``` inside planvec.  
    For instructions, see https://github.com/pypa/pipenv.
3) Install a new **ipykernel** to be used inside a **jupyter notebook**:  
    ```python -m ipykernel install --user --name planvec --display-name "planvec env"```
4) Install **pdfunite** (contained in poppler-utils)  
    ```sudo apt install sudo apt-get install poppler-utils```
5) Install **pdfjam** (contained in texlive-extra-utils)  
    ```sudo apt-get install texlive-extra-utils ```

## How to use?
### Python scripts
Before using those make sure you have the pipenv shell activated, i.e.  
```
cd <path/to/planvec/>
pipenv shell
```
#### qt_main_gui.py
```python qt_main_gui.py```   
This will run the main GUI to convert drawings to pdfs.

#### pdf_jammer.py
```python pdf_jammer.py <date-tag>```  
Utility to arrange the output from all teams into one or more pdf's ready for laser cutting. The <date-tag> 
is in the format yyyy-mm-dd, e.g. 2019-11-05, and is used to select the output folder to gather 
pdf files from.

#### color_filter_app.py
```python color_filter_app.py```  
A utility tool to filter out color (ranges) from the webcam input. Can be used to determine the 
HSV values for color filters when doing image processing.

#### tk_main_gui.py
Deprecated. Do not use.

## Tests
Description of tests and how to run. Coming soon.

## Author
Matthäus Heer, maheer@student.ethz.ch