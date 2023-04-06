import gpiozero as gpio
import time
import Encoder

class Motor:
    def __init__(self, m_pin, dir_1, dir_2, enc1=None, enc2=None,  polarity=0, freq=1000):

        self.motor = gpio.PWMOutputDevice(m_pin, frequency=freq)

        if enc1 and enc2:
            self.enc = Encoder.Encoder(enc1, enc2)
                
        else:
            self.enc = None

        if not polarity: 
            self.dir1 = gpio.DigitalOutputDevice(dir_1)
            self.dir2 = gpio.DigitalOutputDevice(dir_2)
        else:
            self.dir1 = gpio.DigitalOutputDevice(dir_2)
            self.dir2 = gpio.DigitalOutputDevice(dir_1)

    def set_direction(self, direction):
        if direction == 'out' or direction == 1:
            self.dir1.on()
            self.dir2.off()
        elif direction == 'in' or direction == 0:
            self.dir1.off()
            self.dir2.on()
        elif direction == 'stop' or direction < 1:
            self.dir1.off()
            self.dir2.off()
        
    def stop(self):
        self.motor.off()

    def move(self, direction, speed):
        self.set_direction(direction)
        self.motor.value = speed*.5
    
    def move_dist(self, distance, direction, speed):
        if self.enc:
            start_point = self.enc.read()
            self.move(direction, speed)
            while True:
                curr_distance = abs(start_point - self.enc.read())
                if curr_distance > distance:
                    break
            self.stop()

    def enc_read(self): 
        return self.enc.read()

    def get_direction(self):
        if self.dir1.value and not self.dir2.value:
            return('out')
        elif not self.dir1.value and self.dir2.value:
            return('in')
        else:
            return('stop')

    def get_speed(self):
        return self.motor.value



m1_dir1 = 10
m1_dir2 = 18
m1_pwm  = 17
m2_dir1 = 24
m2_dir2 = 15
m2_pwm  = 16
m3_dir1 = 0
m3_dir2 = 22
m3_pwm  = 23

enc11 = 9
enc12 = 11
enc21 = 25
enc22 = 5
enc31 = 20
enc32 = 12


m1 = Motor(m1_pwm, m1_dir1, m1_dir2, enc11, enc12, 0)
m2 = Motor(m2_pwm, m2_dir1, m2_dir2, enc21, enc22, 0)
m3 = Motor(m3_pwm, m3_dir1, m3_dir2, enc31, enc32, 1)
fan = gpio.PWMOutputDevice(21, 1000)

def stop():
    m1.stop()
    m2.stop()
    m3.stop()

def move_all(direction, speed):
    m1.move(direction, speed)
    m2.move(direction, speed)
    m3.move(direction, speed)

def read():
    print('M1 Reading: ', m1.enc_read())
    print('M2 Reading: ', m2.enc_read())
    print('M3 Reading: ', m3.enc_read())

def move_all_dist(dist1, dist2, dist3, direction, speed):
    start_1 = m1.enc_read()
    start_2 = m2.enc_read()
    start_3 = m3.enc_read()
    flag1 = False
    flag2 = False
    flag3 = False
    
    move_all(direction, speed)

    while True:
        curr_1 = abs(start_1 - m1.enc_read())
        curr_2 = abs(start_2 - m2.enc_read())
        curr_3 = abs(start_3 - m3.enc_read())

        if curr_1 > dist1:
            m1.stop()
            flag1 = True

        if curr_2 > dist2:
            m2.stop()
            flag2 = True 

        if curr_3 > dist3:
            m3.stop()
            flag3 = True
        
        if flag1 and flag2 and flag3:
            break

    stop()

