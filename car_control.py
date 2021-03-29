import RPi.GPIO as GPIO
import time
from threading import Event

IN1 = 11
IN2 = 12
IN3 = 13
IN4 = 15

steer = 22

pwm_a = 16
pwm_b = 18
pwm_frequency = 50


class CarController(object):
    def __init__(self):
        self.pwm_left = None
        self.pwm_right = None
        self.steer = None
        self.setup()
        self.last_time = 0
        self.lock2 = Event()
        self.lock2.set()

    @staticmethod
    def set_motor(w1, w2, w3, w4):
        GPIO.output(IN1, w1)
        GPIO.output(IN2, w2)
        GPIO.output(IN3, w3)
        GPIO.output(IN4, w4)

    def stop(self):
        self.set_motor(0, 0, 0, 0)

    def forward(self):
        self.set_motor(1, 0, 0, 1)

    def backward(self):
        self.set_motor(0, 1, 1, 0)

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        for i in [IN1, IN2, IN3, IN4, pwm_a, pwm_b, steer]:
            GPIO.setup(i, GPIO.OUT)

        self.pwm_left = GPIO.PWM(pwm_a, pwm_frequency)
        self.pwm_right = GPIO.PWM(pwm_b, pwm_frequency)
        self.pwm_left.start(100)
        self.pwm_right.start(100)

        self.steer = GPIO.PWM(steer, pwm_frequency)
        # 90°
        self.steer.start(7.5)
        self.stop()

    def parse_req(self, data):
        print(data)
        if data['type'] == 'left-right':
            pass
        elif data['type'] == 'forward-backward':
            self.forward_backward(data['value'])

    '''
        control
    '''
    def forward_backward(self, val):
        """
        前后
        """
        if not self.lock2.is_set:
            self.lock2.wait()
        self.lock2.clear()
        if val > 0:
            self.backward()
        elif val < 0:
            self.forward()
        else:
            self.stop()
            return
        self.change_speed_strength(10*abs(val))
        self.lock2.set()

    def left_right(self, val):
        """
        左右
        """
        time_now = time.time()
        if time_now - self.last_time <= 0.1:
            return
        self.last_time = time_now
        deg = 90-val*30
        degrees = 2.5+deg*10/180
        self.steer.ChangeDutyCycle(degrees)

    def change_speed_strength(self, speed):
        """
        速度倍率
        """
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    def change_steer_angle(self, val):
        """
        转弯角度
        """
        pass

    @staticmethod
    def destroy():
        GPIO.cleanup()


if __name__ == '__main__':
    server = CarController()
    server.forward()
    server.destroy()
