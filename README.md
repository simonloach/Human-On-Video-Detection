# IO2020 
## Prerequisities
1. [Python (3.8.6 - 3.9 were using during implementation)](https://www.python.org/downloads/)
2. [pip](https://pip.pypa.io/en/stable/installing/) (Should get installed with Python on default)
3. [Git](https://git-scm.com/downloads)


## Instalation
To start do steps listed below assuming you are familiar with usage of GitBash. If not here is a [Git manual](https://git-scm.com/book/en/v2)

  1. ```git clone https://github.com/simonloach/IO2020.git```
  2. ```cd IO2020```
  3. ```python -m venv venv```
  4. Depending if you use powershell, cmd or gitbash accordingly use (order maintained):
      ```bash
      ./venv/Scripts/activate.ps1
      ```
      ```bash
      ./venv/Scripts/activate.bat
      ```
      ```bash
      . venv/Scripts/activate
      ```
      
  5. ```pip install -r requirements.txt```
  6. Download YOLOv3 weights yolov3.weights file: https://pjreddie.com/media/files/yolov3.weights
  7. Make sure your folder looks like that:
  ```
  IO2020
      |   backend.py
      |   gui.py
      |   README.md
      |   requirements.txt
      |   yolov3.cfg
      |   yolov3.weights 
      |   coco.names
      +---venv 
 ```     
8. 
```bash
python gui.py
```
