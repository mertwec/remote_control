
import time
import RPi.GPIO as GPIO


class PinIO():            
    def __init__(self,GPIO):
        #self.GPIO = GPIO
        GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by name gpio
        GPIO.setwarnings(True)       # for detects that a pin has been configured to something other than the default (input)

        self.KN_UACC = 10
        self.KN_I_BOMB = 9
        self.KN_I_WELD = 11

        self.VD_ON_UACC = 20
        self.VD_ON_WELD = 16
        self.VD_ON_FIL = 21

        self.ON_UACC = 19
        self.ON_WELD = 26

    def __str__(self):
        status_on_uacc = GPIO.input(self.ON_UACC)
        status_on_weld = GPIO.input(self.ON_WELD)

        mess = f'status:\n\t -ON_UACC:{status_on_uacc}\n\t-ON_UACC:{status_on_weld}'
        return mess

    def set_start_state(self):
        pins_vd = [self.VD_ON_UACC, self.VD_ON_WELD, self.VD_ON_FIL]
        GPIO.setup(pins_vd, GPIO.IN, )

        pins_knob = [self.KN_UACC, self.KN_I_BOMB, self.KN_I_WELD]
        GPIO.setup(pins_knob, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        pins_rule = [self.ON_UACC, self.ON_WELD]
        GPIO.setup(pins_rule, GPIO.OUT, initial=GPIO.LOW,)# pull_up_down=GPIO.PUD_DOWN

    @staticmethod
    def add_event_knob(btn, callback_func): # btn = [self.KN_UACC, self.KN_I_BOMB, self.KN_I_WELD]
        '''
        RISING -- watchdog on button from LOW to HIGH
        FALLING -- watchdog on button from HIGH to LOW'''
        GPIO.add_event_detect(btn,
                              GPIO.FALLING,
                              callback=callback_func,
                              bouncetime=50)
    @staticmethod
    def add_event_vd(vd, callback_func):    # vd = [self.VD_ON_UACC, self.VD_ON_WELD, self.VD_ON_FIL]
        GPIO.add_event_detect(vd,
                              GPIO.BOTH,    # ??
                              callback=callback_func)

    def on_knob(self):          # callback_func
        """set bomb, uacc out"""
        pass

    def on_vd(self):
        """set tkinter.Canvas in red/green"""
        pass

def test(GPIO):
    gpio = PinIO(GPIO)
    gpio.set_start_state()
    
    print(gpio)


if __name__ == "__main__":
    test(GPIO)



