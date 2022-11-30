# planvec
Vectorizes a captured image of a drawn construction plan component.

## Installation

V0.0.8 for Ubuntu 22.04 LTS 
V0.0.7 for Ubuntu 20.04. LTS
https://github.com/cybathlon-at-school/planvec/releases

### For End-Users
1) Install **pdfunite** (contained in poppler-utils)  
    ```sudo apt install poppler-utils```
2) Install **pdfjam** (contained in texlive-extra-utils) - takes a few minutes  
    ```sudo apt-get install texlive-extra-utils ```
3) Download the executable `main` from the latest production release and run it via  
    ```./main``` (at the location of the file)
4) TODO: Add instructions on adding a Desktop entry to start the application with a double-click


### For Development
0) Make sure git is installed. If not (e.g. on a new machine): ```sudo apt install git```.  
0) Install zlib ```sudo apt-get install zlib1g-dev```.  
0) Install pip ```sudo apt install python-pip```.  
1) Clone this repo to a location of your choice.  
2) Install **pyenv**.
    For instructions, see https://github.com/pyenv/pyenv.  
    Also run (from pyenv common build problems)
    ```
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl
   ```
2) Install python 3.8.6 with pyenv ```pyenv install 3.8.6```
3) Install **pipenv** and do ```pipenv install``` before ```pipenv shell``` inside planvec.  
    For instructions, see https://github.com/pypa/pipenv.
4) Go to your cloned repo and do ```pipenv install``` and ```pipenv shell```.
4) Install a new **ipykernel** to be used inside a **jupyter notebook**:  
    ```python -m ipykernel install --user --name planvec --display-name "planvec env"```
5) Install **pdfunite** (contained in poppler-utils)  
    ```sudo apt install poppler-utils```
6) Install **pdfjam** (contained in texlive-extra-utils) - takes a few minutes  
    ```sudo apt-get install texlive-extra-utils ```

## How to use (for development)
### Python scripts
Before using those make sure you have the pipenv shell activated, i.e.  
```
cd <path/to/planvec/>
pipenv shell
```
#### main.py
```python main.py```   
This will run the main GUI to convert drawings to pdfs via vision.

#### scripts
There are couple of convenience scripts in ```planvec/scripts``` folder. For example the ```single_shot_planvec.py``` to run planvec on a single shot image taken with the camera without any GUI.

#### color_filter_app.py
```python color_filter_app.py```  
A utility tool to filter out color (ranges) from the webcam input. Can be used to determine the 
HSV values for color filters when doing image processing. Note to set the camera index in the script correctly.

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

## Author
Matthäus Heer, matthaeusheer@gmail.com
