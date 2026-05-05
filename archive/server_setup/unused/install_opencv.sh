#!/bin/bash
cd ~/src
git clone https://github.com/Itseez/opencv.git
cd opencv
git checkout 3.1.0
mkdir build
cd build
cmake .. -DBUILD_opencv_python3=ON  -DENABLE_PRECOMPILED_HEADERS=OFF 
make -j4
sudo make install
