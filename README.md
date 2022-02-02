# qtCart

#export ui
python -m PyQt5.uic.pyuic -x ui/qtcart.ui -o ui/ui_qtcart.py

# get yolo model
- name: yolo-v4-tiny-tf_openvino_2021.4_6shave.blob
size: 12168064
sha256: 0229c068ff220631affd323b84eece865bfe28d5fe8950ab602825a8444b86f4
source: https://artifacts.luxonis.com/artifactory/luxonis-depthai-data-local/network/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob

# startup script
https://serverok.in/run-a-script-on-boot-using-systemd-on-ubuntu-18-04

# set hdmi as default audio output
https://itectec.com/ubuntu/ubuntu-how-do-you-set-a-default-audio-output-device-in-ubuntu-18-04/

pacmd list-sinks
pactl set-default-sink alsa_output.platform-3510000.hda.hdmi-stereo-extra1

# get pyqt5 for venv
pip3 install --upgrade pip
pip3 install --upgrade setuptools

sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtmultimedia

cp -rp /usr/lib/python3/dist-packages/sip* carEnv/lib/python3.6/site-packages/
cp -rp /usr/lib/python3/dist-packages/PyQt5/ carEnv/lib/python3.6/site-packages/

# ipconfig
sudo ifconfig eth0 169.254.1.10 netmask 255.255.0.0 up
sudo ifconfig eth0 192.168.1.203 netmask 255.255.255.0 up

# if shown CORE ENDED
export OPENBLAS_CORETYPE=ARMV8

nano ~/.bashrc