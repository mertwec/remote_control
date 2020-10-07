
import time
import RPi.GPIO as GPIO
from modbus485_mm import ModbusConnect



class PinIO(ModbusConnect):
    def __init__(self, GPIO):
        ModbusConnect.__init__(self)

        GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by name gpio
        GPIO.setwarnings(False)       # for detects that a pin has been configured to something other than the default (input)

        self.KN_UACC = 10
        self.KN_I_BOMB = 9
        self.KN_I_WELD = 11
        self.pins_knob = [self.KN_UACC, self.KN_I_BOMB, self.KN_I_WELD]

        self.ON_UACC = 19
        self.ON_WELD = 26
        self.pins_rule = [self.ON_UACC, self.ON_WELD]

        self.VD_ON_UACC = 20
        self.VD_ON_WELD = 16
        self.VD_ON_FIL = 21
        self.pins_vd = [self.VD_ON_UACC, self.VD_ON_WELD, self.VD_ON_FIL]

    def __str__(self):
        status_on_uacc = GPIO.input(self.ON_UACC)
        status_on_weld = GPIO.input(self.ON_WELD)
        vd = [GPIO.input(i) for i in self.pins_vd]
        mess = f'''status:
        \t-ON_UACC:{status_on_uacc}
        \t-ON_WELD:{status_on_weld}
        \t--------------
        \t VD_ON_UACC {self.pins_vd[0]}:{vd[0]}
        \t VD_ON_WELD {self.pins_vd[1]}:{vd[1]}
        \t VD_ON_FIL {self.pins_vd[2]}:{vd[2]}
        '''
        return mess

    def set_start_state(self):
        '''initial state of pins'''

        GPIO.setup(self.pins_knob, GPIO.IN, pull_up_down=GPIO.PUD_UP) # knobs
        GPIO.setup(self.pins_rule, GPIO.IN, pull_up_down=GPIO.PUD_UP) #
        GPIO.setup(self.pins_vd, GPIO.OUT, initial=GPIO.HIGH) # OUT signal in 1

    #!!!!!!!!! run in cykle
    def set_output_VD(self, stat_system:dict):
        '''
            1.1.	Выходной сигнал VD_ON_UACC:
                0 – источник ускоряющего напряжения включен,
                1 – источник ускоряющего напряжения выключен;
            1.2.	Выходной сигнал VD_ON_FIL:
                0 – ток бомбардировки включен,
                1 – ток бомбардировки выключен;
            1.3.	Выходной сигнал VD_ON_WELD:
                0 – ток сварки включен,
                1 – ток сварки выключен.
        '''
        GPIO.output(self.VD_ON_UACC,stat_system['stat_UACC'])
        GPIO.output(self.VD_ON_WELD,stat_system['stat_IWELD'])
        GPIO.output(self.VD_ON_FIL,stat_system['stat_IBOMB'])

    def fwrite_for_callback(self, register:int, value:bool):
        # helper function
        self.write_execution_command(register_=register, value_=value)
        
    def callback_ON_WELD(self, chanel):
        # вызов при изменении состояния на пине ON-I_WELD
        #time.sleep(0.1)
        if GPIO.input(self.ON_WELD) == 1:
            print('callback_ON_WELD off',GPIO.input(self.ON_WELD))
            self.fwrite_for_callback(register=self.execution_commands['exec_I_WELD'][0], value=False)
        elif GPIO.input(self.ON_WELD) == 0:
            print('callback_ON_WELD on',GPIO.input(self.ON_WELD))
            self.fwrite_for_callback(register=self.execution_commands['exec_I_WELD'][0], value=True)

    def callback_ON_UACC(self,chanel):
        # вызов при изменении состояния на пине ON-UACC
        if GPIO.input(self.ON_UACC) == 1:
            print('callback_ON_uacc  off - ',GPIO.input(self.ON_UACC))
            self.fwrite_for_callback(register=self.execution_commands['exec_I_BOMB'][0], value=False)
            time.sleep(0.15)
            self.fwrite_for_callback(register=self.execution_commands['exec_U_ACC'][0], value=False)
        elif GPIO.input(self.ON_UACC) == 0:
            print('callback_ON_uacc on',GPIO.input(self.ON_WELD))
            self.fwrite_for_callback(register=self.execution_commands['exec_U_ACC'][0], value=True)
            time.sleep(0.15)
            self.fwrite_for_callback(register=self.execution_commands['exec_I_BOMB'][0], value=True)

    def run_system_on_signal(self):
        '''    Входной сигнал ON_WELD:
            фронт из 1 в 0 – команда контроллеру на включение тока сварки,
            фронт из 0 в 1 – команда контроллеру на выключение тока сварки;
        '''
        GPIO.add_event_detect(self.ON_WELD, GPIO.BOTH, callback=self.callback_ON_WELD, bouncetime=500)
        print('event ON_WELD run')

        '''     Входной сигнал ON_UACC:
            фронт из 1 в 0 – команда контроллеру на включение источника ускоряющего напряжения, затем команда контроллеру на включение тока бомбардировки,
            фронт из 0 в 1 – команда контроллеру на выключение тока бомбардировки, затем команда контроллеру на выключение источника ускоряющего напряжения;
        '''
        GPIO.add_event_detect(self.ON_UACC, GPIO.BOTH, callback=self.callback_ON_UACC, bouncetime=500)
        print('event ON_UACC run')

    def callback_knob(self,chanel):

        stat_system = self.read_status_system()  #read status system
        
        if chanel == self.KN_UACC:
            if stat_system['stat_UACC'] == 1: # UACC - on
                # off
                self.fwrite_for_callback(register=self.execution_commands['exec_U_ACC'][0], value=False)
            elif stat_system['stat_UACC'] == 0: # UACC - off
                # on
                self.fwrite_for_callback(register=self.execution_commands['exec_U_ACC'][0], value=True)
        
        elif chanel == self.KN_I_BOMB:
            if stat_system['stat_IBOMB'] == 1: # ibomb - on
                # off
                self.fwrite_for_callback(register=self.execution_commands['exec_I_BOMB'][0], value=False)
            elif stat_system['stat_IBOMB'] == 0: # ibomb - off
                # on
                self.fwrite_for_callback(register=self.execution_commands['exec_I_BOMB'][0], value=True)
        
        elif chanel == self.KN_I_WELD:
            if stat_system['stat_IWELD'] == 1: # ibomb - on
                # off
                self.fwrite_for_callback(register=self.execution_commands['exec_I_WELD'][0], value=False)
            elif stat_system['stat_IWELD'] == 0: # ibomb - off
                # on
                self.fwrite_for_callback(register=self.execution_commands['exec_I_WELD'][0], value=True)
        else:
            pass
        
    def run_system_on_knob(self): # btn = [self.KN_UACC, self.KN_I_BOMB, self.KN_I_WELD]
        '''
        Bходной сигнал KN_ON_OFF_UACC:
            фронт из 1 в 0 – команда контроллеру на включение источника ускоряющего напряжения, при текущем статусе «Выкл»; на выключение при статусе «Вкл»;
        Входной сигнал KN_ON_OFF_I_BOMB:
            фронт из 1 в 0 – команда контроллеру на включение тока бомбардировки при текущем статусе «Выкл»; на выключение при статусе «Вкл»;
        Входной сигнал KN_ON_OFF_I_WELD:
            фронт из 1 в 0 – команда контроллеру на включение тока сварки при текущем статусе «Выкл», на выключение при статусе «Вкл»;

        '''
        for knob in self.pins_knob:
            GPIO.add_event_detect(knob, GPIO.FALLING, bouncetime=100,
                                callback=self.callback_knob)
            print(f'event knob {knob} run')



if __name__ == "__main__":

    gpio = PinIO(GPIO)
    mm = ModbusConnect()

    gpio.set_start_state()
    #print(gpio)

    # выкл все выходы
    ce=mm.execution_commands
    for i in ce:
        mm.write_execution_command(register_=ce[i][0], value_=ce[i][1]) # ce[i][1] = False
    print(gpio)

    gpio.run_system_on_signal()
    gpio.run_system_on_knob()

    try:
        n=0
        while True:
            stat_system = mm.read_status_system()
            print(stat_system)
            gpio.set_output_VD(stat_system)

            print('...')
            for i in gpio.pins_knob+gpio.pins_rule:
                if  GPIO.event_detected(i):
                    print(i, ':------\n', gpio)
            n+=1
            time.sleep(3)
            print(n,gpio)

    except KeyboardInterrupt:
        GPIO.cleanup()
        input('cleaned')

