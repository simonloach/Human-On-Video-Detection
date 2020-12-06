# IO2020 Instalation
To start do steps listed below:
  1. ```git clone https://github.com/simonloach/IO2020.git```
  2. ```cd IO2020```
  3. ```python -m venv venv```
  4. Depending if you use powershell, cmd or gitbash accordingly use (order maintained):
  
      ```./venv/Scripts/activate.ps1```
      ```./venv/Scripts/activate.bat```
      
      ```. /venv/Scripts/activate```
      
  5. ```pip install -r requirements.txt```
  6. Download YOLOv3 weights yolov3.weights file: https://pjreddie.com/media/files/yolov3.weights
  7. Make sure your folder looks like that:
  ```IO2020
      |   backend.py
      |   gui.py
      |   README.md
      |   requirements.txt
      |   yolov3.cfg
      |   yolov3.weights 
      |   coco.names
      +---venv 
 ```     
8. python gui.py
