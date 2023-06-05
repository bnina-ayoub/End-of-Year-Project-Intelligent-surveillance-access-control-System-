# Intelligent Surveillance Access Control System

This project is an intelligent surveillance access control system that uses computer vision and deep learning techniques to detect and recognize individuals and grant access based on their identity. The system uses a Raspberry Pi 4 with a camera module to capture images and videos, and an Azure Cognitive Services Custom Vision for student card detection and a local Face Recognition library to perform facial recognition.

## Getting Started

To run this project, you will need the following hardware and software:

### Hardware
- Raspberry Pi 4
- Micro HDMI Adapter
- Type C Cable
- Raspberry Pi Camera Module / USB Webcam
- RGB LED
- PIR Motion Detection
- 7 Jump wires

### Software
- Raspbian OS legacy
- Python 3.7+
- OpenCV 4.7.0
- Azure Cognitive Services API subscription
- Face_recognition
- gpiozero

### Installing Raspbian OS Legacy

To install Raspbian OS legacy on Raspberry Pi 4, follow these steps:

1. Download the Raspbian Buster with desktop (legacy) image from the official Raspberry Pi website.
2. Flash the image onto a microSD card using a software like BalenaEtcher.
3. Insert the microSD card into the Raspberry Pi and power it on.

### Building OpenCV from Scratch

To build OpenCV from scratch on Raspberry Pi 4, follow these steps:

1. Install the dependencies:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt-get install python3-dev python3-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
```
2. Clone the OpenCV repository:
```
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.7.0
cd ..
```
3. Clone the OpenCV contrib repository:
```
git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout 4.7.0
cd ..
```
4. Create a build directory and navigate into it:
```
mkdir build
cd build
```
5. Configure the build using cmake:
```
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules \
-D ENABLE_NEON=ON \
-D ENABLE_VFPV3=ON \
-D BUILD_TESTS=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF \
-D BUILD_EXAMPLES=OFF ..
```
6. Build and install OpenCV:
```
make -j4
sudo make install
sudo ldconfig
```
## Usage

To use this project, follow these steps:

1. Clone the repository:
```
git clone https://github.com/<username>/Intelligent-surveillance-access-control-system.git
cd Intelligent-surveillance-access-control-system
```
2. Install the required Python packages:
```
pip install -r requirements.txt
```
3. Update the `subscription_key` and `endpoint` variables in the `Système de surveillance automatisé.py` file with your own Azure Cognitive Services subscription key and endpoint and the prediction key for your trained model
4. Run the 
`Système de surveillance automatisé.py` script:
```
python "Système de surveillance automatisé.py"
```

## Contributing

Contributions are welcome.

