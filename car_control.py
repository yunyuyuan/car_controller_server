import RPi.GPIO as GPIO
import time

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
        self.speed_strength = 1
        self.max_steer_angle = 30
        self.margin = -2.5

    @staticmethod
    def set_motor(w1, w2, w3, w4):
        GPIO.output(IN1, w1)
        GPIO.output(IN2, w2)
        GPIO.output(IN3, w3)
        GPIO.output(IN4, w4)

    def stop(self):
        self.set_motor(0, 0, 0, 0)

    def backward(self):
        self.set_motor(1, 0, 1, 0)

    def forward(self):
        self.set_motor(0, 1, 0, 1)

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
        value = data['value']
        if data['type'] == 'left-right':
            self.left_right(value)
        elif data['type'] == 'forward-backward':
            self.forward_backward(value)
        elif data['type'] == 'speed-strength':
            self.speed_strength = value
        elif data['type'] == 'steer-angle':
            self.max_steer_angle = value

    '''
        control
    '''
    def forward_backward(self, val):
        """
        前后
        """
        if val > 0:
            self.backward()
        elif val < 0:
            self.forward()
        else:
            self.stop()
            return
        self.change_speed_strength(10*abs(val)/(8/self.speed_strength))

    def left_right(self, val):
        """
        左右
        """
        deg = 90+self.margin-(val/10)*self.max_steer_angle
        degrees = 2.5+deg*10/180
        self.steer.ChangeDutyCycle(degrees)

    def change_speed_strength(self, speed):
        """
        速度
        """
        self.pwm_left.ChangeDutyCycle(speed)
        self.pwm_right.ChangeDutyCycle(speed)

    @staticmethod
    def destroy():
        GPIO.cleanup()


if __name__ == '__main__':
    server = CarController()
    i = 10
    while 1:
        server.left_right(i)
        time.sleep(0.2)
        i *= -1
