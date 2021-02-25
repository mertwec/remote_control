
import time
import RPi.GPIO as GPIO
from modbus485_mm import ModbusConnect
from i2c_bus import ExtSwitcher
from focusing_config import SettFOC

import threading as thr


def decorator_call_in_thread(function_):
    def wrapper(self,*args,**kwargs):
        try:
            run_thread=thr.Thread(target=function_, args=(self,*args,))
            run_thread.daemon = True
            run_thread.start() 
            print(run_thread.getName())
        except TypeError as te:
            print(f'Error in modul: "in_out_buttons" {function_.__name__}: {te}')
            time.sleep(0.05)
            return wrapper(self, chanel)
    return wrapper

class PinIO(ModbusConnect, ExtSwitcher, SettFOC):
    
    def __init__(self, GPIO):
        GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by name gpio
        GPIO.setwarnings(False)      # for detects that a pin has been configured to something other than the default (input)

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
        GPIO.setup(self.pins_vd, GPIO.OUT, initial=GPIO.LOW) # OUT signal in 1
    
#!!!!!!!!!!!!!! run in cykle !!!!!!!!!!!!!!!!!!!
    def set_output_VD(self, stat_system:dict, value_ibomb, setted_ibomb): #
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
        GPIO.output(self.VD_ON_UACC, stat_system['stat_UACC'])      
        GPIO.output(self.VD_ON_WELD, stat_system['stat_IWELD'])        
        #GPIO.output(self.VD_ON_FIL, stat_system['stat_IBOMB'])
        if value_ibomb >= setted_ibomb*0.85:
            GPIO.output(self.VD_ON_FIL, stat_system['stat_IBOMB'])
        else:
            GPIO.output(self.VD_ON_FIL, 0)

    def set_outside_knob(self, status_system:dict):
        '''если кнопка нажата (on), а система не включена (off) то вызвать 
        обработчик сигнала "calback_on_weld " или "callback_on_uacc"
        in pin --- 1=off; 0=on
        in system --- 1=on: 0=off
        '''
        try:
            pin_iweld = GPIO.input(self.ON_WELD) # 1=off; 0=on
            pin_uacc = GPIO.input(self.ON_UACC)
            status_on_iweld = status_system['stat_IWELD'] # 1=on: 0=off
            status_on_uacc = status_system['stat_UACC']
            if pin_iweld==0 or pin_uacc == 0:
                self.remove_system_on_knob()
                if pin_iweld == status_on_iweld:
                    self.callback_ON_WELD(self.ON_WELD)
                if pin_uacc == status_on_uacc:
                    self.callback_ON_UACC(self.ON_UACC)
            elif pin_iweld==1 or pin_uacc==1:
                self.run_system_on_knob()
        except RuntimeError as rte:
            #print(f'RuntimeError {rte}')
            pass
    
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!    
        
    def fwrite_for_callback(self, register:int, value:bool):
        # helper function
        ModbusConnect().write_execution_command(register_=register, value_=value)
    
    def fwrite_softstart_IWELD(self, register, time_wait=5):
        value_start = SettFOC().readConfig()['start_I_WELD'] # from 'settings_focus.conf' get start IWELD
        value_set = ExtSwitcher().value_iweld() # get switch state
        if value_start >= value_set:
            self.fwrite_for_callback(register, True) # on IWELD if Iswitch>=Istart
        elif value_start < value_set:
            ModbusConnect().write_one_register(register_=ModbusConnect().set_points['set_iweld'][0],     
                                    value_=value_start,     # set IWELD in start value
                                    degree_=ModbusConnect().set_points['set_iweld'][1], 
                                    signed_= False)
            self.fwrite_for_callback(register, True)        # on Iweld
            
            for i in range(time_wait):
                print(f'sleep {i}')
                time.sleep(1)
                
            value_set = ExtSwitcher().value_iweld()
            ModbusConnect().write_one_register(register_=ModbusConnect().set_points['set_iweld'][0],     
                                    value_=value_set,       # set IWELD in set value
                                    degree_=ModbusConnect().set_points['set_iweld'][1], 
                                    signed_= False)
        else:
            print(f'Error in {fwrite_softstart_IWELD.__name__}')
            self.fwrite_for_callback(register, False)
    
    @decorator_call_in_thread
    def callback_ON_WELD(self, chanel): #self.ON_WELD
        ''' вызов при изменении состояния на пине ON-I_WELD
        execution_commands from modbus485_mm
        '''        
        if GPIO.input(chanel) == 1:
            print('callback_ON_WELD off', GPIO.input(chanel))
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0], 
                                    value=False)
        elif GPIO.input(chanel) == 0:
            print('callback_ON_WELD on', GPIO.input(chanel))
            #self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0], value=True)
            self.fwrite_softstart_IWELD(register=ModbusConnect().execution_commands['exec_I_WELD'][0])
        else:
            print(f' in chanel {chanel} -- none type')
            
    #@decorator_call_in_thread
    def callback_ON_UACC(self, chanel):
        # вызов при изменении состояния на пине ON-UACC
        if GPIO.input(self.ON_UACC) == 1:
            print('callback_ON_uacc  off - ',GPIO.input(self.ON_UACC))
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_BOMB'][0], value=False)
            time.sleep(0.15)
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_U_ACC'][0], value=False)
        elif GPIO.input(self.ON_UACC) == 0:
            print('callback_ON_uacc on',GPIO.input(self.ON_WELD))
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_U_ACC'][0], value=True)
            time.sleep(0.15)
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_BOMB'][0], value=True)
        else:
            print(f' in chanel {chanel} -- none type')
     
    #@decorator_call_in_thread
    def callback_knob(self, chanel):
        '''действие при нажатии кнопки
        '''
        stat_system = ModbusConnect().read_status_system()  #read status system

        if chanel == self.KN_UACC:
            if stat_system['stat_UACC'] == 1: # UACC - on
                # off
                self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_U_ACC'][0],
                                            value=False)
            elif stat_system['stat_UACC'] == 0: # UACC - off
                # on
                self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_U_ACC'][0],
                                            value=True)
        elif chanel == self.KN_I_BOMB:
            if stat_system['stat_IBOMB'] == 1: # ibomb - on
                # off
                self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_BOMB'][0],
                                            value=False)
            elif stat_system['stat_IBOMB'] == 0: # ibomb - off
                # on
                self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_BOMB'][0],
                                            value=True)        
        elif chanel == self.KN_I_WELD:
            if stat_system['stat_IWELD'] == 1: # ibomb - on
                # off
                self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0],
                                            value=False)
            elif stat_system['stat_IWELD'] == 0: # ibomb - off
                # on
                #self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0], value=True)
                self.fwrite_softstart_IWELD(register=ModbusConnect().execution_commands['exec_I_WELD'][0],
                                                        )
        else:
            pass
    
    @decorator_call_in_thread
    def callback_knob_iweld(self, chanel):
        stat_system = ModbusConnect().read_status_system()  #read status system
        if stat_system['stat_IWELD'] == 1: # ibomb - on
            # off
            self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0],
                                        value=False)
        elif stat_system['stat_IWELD'] == 0: # ibomb - off
            # on
            #self.fwrite_for_callback(register=ModbusConnect().execution_commands['exec_I_WELD'][0], value=True)
            self.fwrite_softstart_IWELD(register=ModbusConnect().execution_commands['exec_I_WELD'][0],)
            
    def run_knob_iweld(self):
        GPIO.add_event_detect(self.KN_I_WELD, GPIO.FALLING, bouncetime=300,
                                callback=self.callback_knob_iweld)
        print(f'event knob {self.KN_I_WELD} run')
            
    def run_system_on_signal(self):
        '''    Входной сигнал ON_WELD:
            фронт из 1 в 0 – команда контроллеру на включение тока сварки,
            фронт из 0 в 1 – команда контроллеру на выключение тока сварки;
        '''
        GPIO.add_event_detect(self.ON_WELD, GPIO.BOTH, 
                                callback=self.callback_ON_WELD, bouncetime=100)
        print('event ON_WELD run')

        '''     Входной сигнал ON_UACC:
            фронт из 1 в 0 – команда контроллеру на включение источника ускоряющего напряжения, затем команда контроллеру на включение тока бомбардировки,
            фронт из 0 в 1 – команда контроллеру на выключение тока бомбардировки, затем команда контроллеру на выключение источника ускоряющего напряжения;
        '''
        GPIO.add_event_detect(self.ON_UACC, GPIO.BOTH, 
                                callback=self.callback_ON_UACC, bouncetime=100)
        print('event ON_UACC run')

    def run_system_on_knob(self): # btn = [self.KN_UACC, self.KN_I_BOMB]
        '''
        Bходной сигнал KN_ON_OFF_UACC:
            фронт из 1 в 0 – команда контроллеру на включение источника ускоряющего напряжения, при текущем статусе «Выкл»; на выключение при статусе «Вкл»;
        Входной сигнал KN_ON_OFF_I_BOMB:
            фронт из 1 в 0 – команда контроллеру на включение тока бомбардировки при текущем статусе «Выкл»; на выключение при статусе «Вкл»;
        Входной сигнал KN_ON_OFF_I_WELD:
            фронт из 1 в 0 – команда контроллеру на включение тока сварки при текущем статусе «Выкл», на выключение при статусе «Вкл»;

        '''
        for knob in self.pins_knob[:2]:
            GPIO.add_event_detect(knob, GPIO.FALLING, bouncetime=300,
                                callback=self.callback_knob)
            print(f'event knob {knob} runed')
    
    def remove_system_on_knob(self):
        for knob in self.pins_knob:
            GPIO.remove_event_detect(knob)
            print(f'event knob {knob} stoped')
    
if __name__ == "__main__":
    gpio = PinIO(GPIO,)
    mm = ModbusConnect()

    gpio.set_start_state()
    print(gpio)

    # выкл все выходы
    ce=mm.execution_commands
    for i in ce:
        mm.write_execution_command(register_=ce[i][0], value_=ce[i][1]) # ce[i][1] = False
    print(gpio)

    gpio.run_system_on_signal()
    gpio.run_system_on_knob()
    #gpio.run_knob_iweld()
    try:
        n=0
        while True:
            status_system = mm.read_status_system()
            mm_bomb = mm.read_all_parameters()['I_BOMB']
            ss_bomb = mm.read_all_parameters()['sets_IBOMB']
            print(status_system,)
            print(mm_bomb,'------------', ss_bomb)
            gpio.set_output_VD(status_system, mm_bomb, ss_bomb)

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
    finally:
        GPIO.cleanup()
        mm.close_connect()
