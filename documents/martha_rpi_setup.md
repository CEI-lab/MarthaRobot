setup new rpi sd with official Raspberry Pi Imager

- os (bullseye 32 bit)
- enable ssh
- setup username/password (default pi/raspberry)
- optionally setup wifi, or use lan

Setup pi

```
sudo raspi-config
```

Advanced Options ->
Expand Filesystem ->
Finish/Reboot

Optionally setup VNC viewer or similar for GUI access

## Update RPI

```
sudo apt-get update
sudo apt-get upgrade
```

## Installing/Reinstalling Python

This guide was developed with python 3.7.15. Modifications may be needed for alternate versions
To install python 3.7 on an RPi that comes with a different version,

check version of python

```
python --version
python3 --version
```

Find link to the gzipped source tarball for desired version of python

```
wget https://www.python.org/ftp/python/3.7.15/Python-3.7.15.tgz
tar -zxvf Python-3.7.15.tgz
cd Python-3.7.15
./configure --enable-optimizations

# This step may take a few minutes
sudo make altinstall
```

Set the default python and pip executables

```
cd /usr/bin
sudo rm python
sudo ln -s /usr/local/bin/python3.7 python
sudo rm python3
sudo ln -s /usr/local/bin/python3.7 python3

sudo rm pip
sudo ln -s /usr/local/bin/pip3.7 pip
sudo rm pip3
sudo ln -s /usr/local/bin/pip3.7 pip3

```

Check that updates were succesful

```
python --version
python3 --version
pip -V
pip3 -V
```

# OpenCV Installation

[opencv install guide](https://qengineering.eu/install-opencv-4.5-on-raspberry-pi-4.html)

[opencv install script from guide](https://raw.githubusercontent.com/Qengineering/Install-OpenCV-Raspberry-Pi-32-bits/main/OpenCV-4-5-5.sh)

This process will take around 2 hours. Make sure that you have atleast 6.5GB of memory; If not increase swap.

## Install with script

better option:
https://singleboardbytes.com/647/install-opencv-raspberry-pi-4.htm

```
wget https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-32-bits/raw/main/OpenCV-4-5-5.sh
sudo chmod 755 ./OpenCV-4-5-5.sh
./OpenCV-4-5-5.sh
```

sudo apt-get install cmake gfortran
sudo apt-get install python3-dev python3-numpy
sudo apt-get install libjpeg-dev libtiff-dev libgif-dev
sudo apt-get install libgstreamer1.0-dev gstreamer1.0-gtk3
sudo apt-get install libgstreamer-plugins-base1.0-dev gstreamer1.0-gl
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgtk2.0-dev libcanberra-gtk\*
sudo apt-get install libxvidcore-dev libx264-dev libgtk-3-dev
sudo apt-get install libtbb2 libtbb-dev libdc1394-22-dev libv4l-dev
sudo apt-get install libopenblas-dev libatlas-base-dev libblas-dev
sudo apt-get install libjasper-dev liblapack-dev libhdf5-dev
sudo apt-get install protobuf-compiler

## download the latest version

cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/4.5.5.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.5.5.zip

## unpack

unzip opencv.zip
unzip opencv_contrib.zip

## some administration to make live easier later on

mv opencv-4.5.5 opencv
mv opencv_contrib-4.5.5 opencv_contrib

## clean up the zip files

rm opencv.zip
rm opencv_contrib.zip

# Simple Motor Controller from Pololu

Command line tool to control the USB motor controllers from Pololu which are used for the drive motors.

[Official docs](https://www.pololu.com/docs/0J41)

[Installation Guide](https://www.pololu.com/docs/0J44/3.2) is summarized and expanded below.

## Install dependencies

```
sudo apt-get install libusb-1.0-0-dev mono-runtime libmono-winforms2.0-cil
```

Only if the previous command fails, run this instead.

```
sudo apt-get install libusb-1.0-0-dev mono-runtime mono-devel
```

## Download and unzip the software

Can check the official website to find updated versions, or if this link dissapears.

```
wget https://www.pololu.com/file/0J411/smc-linux-101119.tar.gz
tar -xzvf smc-linux-101119.tar.gz
```

The control center can be used if you have access to a GUI.
Otherwise you are limited to using the command line utility.

Copy 99-pololu.rules to /etc/udev/rules.d/

```
sudo cp smc_linux/99-pololu.rules /etc/udev/rules.d/99-pololu.rules
```

To add the scripts to the path, modify your .bashrc file

```
nano .bashrc
```

Append

```
export PATH="/smc_linux:$PATH"
```

to the end of the file, save and exit with ^O [enter] ^X

Test that it runs

```bash
pi@raspberrypi:~ $ SmcCmd
WARNING: The runtime version supported by this application is unavailable.
Using default runtime: v4.0.30319
SmcCmd: Configuration and control utility for the Simple Motor Controller.
Version: 1.1.0.0
Options:
 -l, --list                   list available devices
 -d, --device SERIALNUM       (optional) select device with given serial number
 -s, --status                 display complete device status
     --stop                   stop the motor
     --resume                 allow motor to start
     --speed NUM              set motor speed (-3200 to 3200)
     --brake NUM              stop motor with variable braking.  32=full brake
     --restoredefaults        restore factory settings
     --configure FILE         load settings file into device
     --getconf FILE           read device settings and write to file
     --bootloader             put device in bootloader (firmware upgrade) mode
Options for changing motor limits until next reset:
     --max-speed NUM          (3200 means no limit)
     --max-speed-forward NUM  (3200 means no limit)
     --max-speed-reverse NUM  (3200 means no limit)
     --max-accel NUM
     --max-accel-forward NUM
     --max-accel-reverse NUM
     --max-decel NUM
     --max-decel-forward NUM
     --max-decel-reverse NUM
     --brake-dur NUM          units are ms.  rounds up to nearest 4 ms
     --brake-dur-forward NUM  units are ms.  rounds up to nearest 4 ms
     --brake-dur-reverse NUM  units are ms.  rounds up to nearest 4 ms
```

# Qwiic_SCMD_Py

Python motor driver module for the qwiic motor controllers used to control the bladder.

PyPi installation

```bash
pip install sparkfun-qwiic-scmd
```

If you get errors or warnings similar to

```bash
WARNING: pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available.
```

Then follow these instructions (from [here](https://stackoverflow.com/a/49696062)) before trying to pip install again.

Otherwise, skip to [Intel Realsense](#intel-realsense)

```bash
sudo apt install libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev
```

cd into the Python3.x directory. These may take a short while to run.

```
./configure
make
sudo make install
```

# Intel Realsense

[Guide to installing on RPi 3](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md) has been copied/addapted below for RPi 4.

## Install packages

```bash
sudo apt-get install -y libdrm-amdgpu1 libdrm-amdgpu1-dbgsym libdrm-dev libdrm-exynos1 libdrm-exynos1-dbgsym libdrm-freedreno1 libdrm-freedreno1-dbgsym libdrm-nouveau2 libdrm-nouveau2-dbgsym libdrm-omap1 libdrm-omap1-dbgsym libdrm-radeon1 libdrm-radeon1-dbgsym libdrm-tegra0 libdrm-tegra0-dbgsym libdrm2 libdrm2-dbgsym

sudo apt-get install -y libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2

sudo apt-get install -y libglu1-mesa libglu1-mesa-dev mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev
```

## Get Source

```bash
cd ~
git clone https://github.com/IntelRealSense/librealsense.git
```

## Update udev rule

```bash
cd ~/librealsense
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Install Bazel

(may no longer be needed)

https://github.com/koenvervloesem/bazel-on-arm

```
cd ~

sudo apt-get install openjdk-8-jdk
sudo update-alternatives --config java


sudo nano /etc/dphys-swapfile
# modify swap to be double ram

#restart swap service
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

wget https://github.com/bazelbuild/bazel/releases/download/6.2.1/bazel-6.2.1-dist.zip
unzip -d bazel bazel-6.2.1-dist.zip
cd bazel

sudo chmod u+w ./* -R

#compile
env BAZEL_JAVAC_OPTS="-J-Xms384m -J-Xmx800m" \
JAVA_TOOL_OPTS="-Xmx800m" \
EXTRA_BAZEL_ARGS="--host_javabase=@local_jdk//:jdk" \
bash ./compile.sh

sudo cp output/bazel /usr/local/bin/bazel


wget https://github.com/bazelbuild/bazel/releases/download/0.5.1/bazel-0.5.1-dist.zip
unzip -d bazel bazel-0.5.1-dist.zip

cd bazel
sudo chmod u+w ./* -R

sudo nano ~/.bashrc

#add to bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf
export PATH=$JAVA_HOME/bin:$PATH

```

limit javac heap size

```
nano scripts/bootstrap/compile.sh
```

replace this

```
run "${JAVAC}" -classpath "${classpath}" -sourcepath "${sourcepath}" \
      -d "${output}/classes" -source "$JAVA_VERSION" -target "$JAVA_VERSION" \
      -encoding UTF-8 "@${paramfile}"
```

with this

```
run "${JAVAC}" -classpath "${classpath}" -sourcepath "${sourcepath}" \
      -d "${output}/classes" -source "$JAVA_VERSION" -target "$JAVA_VERSION" \
      -encoding UTF-8 "@${paramfile}" -J-Xmx500M
```

<!-- git clone https://github.com/koenvervloesem/bazel-on-arm.git
cd bazel-on-arm/
#This may take a while (~1gb download potentially)
sudo make requirements
make bazel -->

## Install abseil

(may no longer be needed)

https://github.com/abseil/abseil-cpp

```

```

## Install protobuf

(Pretty sure this first step is no longer needed)

```
wget https://github.com/protocolbuffers/protobuf/archive/refs/tags/v23.3.tar.gz
tar -xzvf v23.3.tar.gz

```

```
cd ~
git clone --depth=1 -b v3.10.0 https://github.com/google/protobuf.git
cd protobuf
./autogen.sh
./configure
make -j1
sudo make install
cd python
export LD_LIBRARY_PATH=../src/.libs
python3 setup.py build --cpp_implementation
python3 setup.py test --cpp_implementation
sudo python3 setup.py install --cpp_implementation
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=3
sudo ldconfig
protoc --version
```

## Install TBB

```
cd ~
wget https://github.com/PINTO0309/TBBonARMv7/raw/master/libtbb-dev_2018U2_armhf.b
sudo dpkg -i ~/libtbb-dev_2018U2_armhf.deb
sudo ldconfig
rm libtbb-dev_2018U2_armhf.deb
```

<!-- opencv is installed separately, hopefully not needed here -->
<!-- ## Install OpenCV

```
sudo apt autoremove libopencv3

wget https://github.com/mt08xx/files/raw/master/opencv-rpi/libopencv3_3.4.20180907.1_armhf.deb
sudo apt install -y ./libopencv3_3.4.3-20180907.1_armhf.deb
sudo ldconfig
``` -->

## Install RealSense SDK

For issues with "undefined reference to '\_\_atomic_load_8'" try
[this](https://github.com/IntelRealSense/librealsense/issues/9962#issuecomment-998392844)

These may take a while to run.

```bash
cd ~/librealsense
mkdir  build
cd build
cmake .. -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true
#
make -j4
sudo make install
```

## Install pyrealsense2

```bash
cd ~/librealsense/build

cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j4

sudo make install
```

Current versions of the makefile dont install to the correct directory. So the next step may be needed

Find and copy "pyrealsense2.so" and "librealsense2.so" to a directory in your python installation.

```bash
cd /usr/local/lib/python3.7/site-packages/
mkdir pyrealsense2

cp pyrealsense2.cpython-37m-arm-linux-gnueabihf.so.2.54.1 pyrealsense2.cpython-37m-arm-linux-gnueabihf.so
```

Append

```bash
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.7/site-packages/pyrealsense2
```

to ~/.bashrc

Then source ~/.bashrc

```
source ~/.bashrc
```

## RPi Settings

```
sudo apt-get install python-opengl
sudo -H pip3 install pyopengl
sudo -H pip3 install pyopengl_accelerate==3.1.3rc1
sudo raspi-config
```

"7.Advanced Options" -> "A7 GL Driver" -> "G2 GL (Fake KMS)"

## Reboot RPi

```
sudo reboot now
```

# Install AprilTag

```
pip install apriltag
```
