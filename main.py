'''
Instructions to Run:

    Good idea to run 'sudo apt-get update' before all of this.

 - You must enable the camera first.
     1. In a Terminal window, type sudo raspi-config
     2. Go to Interfacing Options -> Camera and enable the camera
     3. Upon exiting raspi-config, reboot as prompted

 - Get dependencies for DHT22 humidity/temperature sensor
     1. pip3 install adafruit-circuitpython-dht
     2. sudo apt-get install libgpiod2

 - Get dependencies for SEN-CCS811
     1. Get dependency libraries:
         a. sudo apt-get install -y build-essential python-pip python-dev python-smbus git
         b. git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
         c. cd Adafruit_Python_GPIO
         d. sudo python3 setup.py install
     2. Get the CCS811 python library:
         a. sudo pip3 install Adafruit_CCS811
     3. Enable I2C:
         a. In a Terminal window, type sudo raspi-config
         b. Go to Interfacing Options -> I2C and enable I2C
     4. Slow down the I2C baud rate; in terminal enter:
         a. sudo nano /boot/config.txt
         b. Add the following line to the file: dtparam=i2c_baudrate=10000
         c. Press Ctrl+s to save and then Ctrl+x to exit
 
'''
from manager import Manager
import gui

manager = Manager()
gui.launch_gui()