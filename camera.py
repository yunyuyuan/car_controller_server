import picamera

class Outputer(object):
    def __init__(self, callback):
        self.callback = callback
    
    def write(self, s):
        self.callback(s)
    
    def flush(self):
        pass


class LiveCamera(object):
    def __init__(self, callback, fmt='h264'):
        self.camera = None
        self.format = fmt
        self.callback = callback
    
    def start(self, resolution = (1280, 720), fps = 30):
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = fps
    
    def pause(self):
        self.camera.stop_recording()
    
    def resume(self):
        self.camera.start_recording(Outputer(callback=self.callback), format=self.format)
    
    def stop(self):
        self.camera.close()
