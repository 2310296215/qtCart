exec > /tmp/debug-my-script.txt 2>&1

export OPENBLAS_CORETYPE=ARMV8

cd /home/nvidia/Documents/qtCart

echo $PWD > a.txt

carEnv/bin/python Program.py
