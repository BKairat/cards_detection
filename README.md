## Installation

``git clone https://github.com/BKairat/cards_detection.git``

#### Create virtual environment 

``python3 -m venv venv``

#### Activete venv Mac/Linux

``sourse venv/bin/activate``

#### Activate venv Win

``venv\Scripts\activate``

#### Install requirements

``pip install -r requirements.txt``

## Calibration
to calibrate colors for your camera add your "callibration_image.png" to images/camera

``python3 calibration.py camera``

or you can test on prepared images

``python3 calibration.py test``

## Example of usage
testing on prepared images:

``python3 image_processing.py``

