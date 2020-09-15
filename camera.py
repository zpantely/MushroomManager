from time import sleep
from picamera import PiCamera

import utility

class Camera():
    def __init__(self, resX=2592, resY=1944):
        self.pi_camera = PiCamera()
        self.pi_camera.resolution = (resX, resY)
        self.pi_camera.start_preview()
        # Camera warm-up time
        #     sleep(1)

    def snap_preview(self):
        utility.ensure_directory_exists('photos')
        self.pi_camera.capture('photos/last.jpg')
