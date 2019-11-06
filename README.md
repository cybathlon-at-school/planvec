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
5) Install **pdfjam** (contained in texlive-extra-utils) - takes a few minutes  
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
```python pdf_jammer.py --help``` yields...  
```
    usage: pdf_jammer.py [-h] -d DATE_TAG [-o OUT_DIR]
    
    Arrange the single pdf outputs of a planvec session into one or more laser-
    cutting ready pdfs.
    
    optional arguments:
      -h, --help            show this help message and exit
      -d DATE_TAG, --date-tag DATE_TAG
                            Specify the date of the session you want to process,
                            e.g. "2019-31-05".
      -o OUT_DIR, --out-dir OUT_DIR
                            Absolute path - location to store created output
                            pdf's. Defaults to session folder given by --date-tag
                            field.
```

#### color_filter_app.py
```python color_filter_app.py```  
A utility tool to filter out color (ranges) from the webcam input. Can be used to determine the 
HSV values for color filters when doing image processing.

#### tk_main_gui.py
Deprecated. Do not use.

### How-To Laser Cut
The pdf_jammer command line tool informs you about the location of the created pdf's. This is how you laser-cut them.
1) Get the files on the Laser-Cutter PC
2) Open the PDF in Corel Draw (not Inkscape!)
3) Select all (Ctrl+A) and set the line width to "Hairline" at the center top in the tool bar
4) One sid-effect is that this creates black boundary boxes around the individual gripper drawings which would yield 
   slow engraving. The get rid of the black lines do:
   - Select All (*Ctr+A*) & Ungroup (possibly several times)
   - Unselect and while pressing *Alt*, select the boxes only by dragging in-between the gripper drawings horizontally
   - With two or three strokes you should be able to select all boundaries and delete them with *Delete*
5) *Ctrl+P* for printing. Select 5mm Wood.
6) Sent the print job which you can then position on the plate appropriately.
7) Do not forget vector ordering.

## Tests
Description of tests and how to run. Coming soon.

## Author
Matthäus Heer, maheer@student.ethz.ch