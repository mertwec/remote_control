#!/usr/bin/python3.7


import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
#import threading

sys.path.append(['/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI',
                '/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI/modules'])

from modules.mask_logging import *

from modules.display_GUI import MainWindow
from modules.in_out_buttons import PinIO
from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC


connect_mb = ModbusConnect()
sfoc = SettFOC() #path='/home/pi/Desktop/pult_spreli_program/settings_focus.conf')
gpio = PinIO(GPIO)
switch = ExtSwitcher()
dac = DACModule()

#lock = threading.Lock()

def set_start_system(appl, connect, swiweld, dac, sfoc):
    '''init: проверка связи. конект через modbus'''
    # проверка связи с контроллером
    conn = connect.check_connect()
    if conn:
        info_log(f'Settings connection: {conn}')

        # Передача команд на выключение источника высокого напряжения, тока бомбардировки и тока сварки
        ce=connect.execution_commands
        for i in ce:
            connect.write_execution_command(register_=ce[i][0], value_=ce[i][1])
        info_log(f'Settings connection: {connect.read_status_system()}')

        # Задание тока сварки в соответствии с положением переключателя
        sw_iweld = swiweld.value_iweld()
        #print(sw_iweld)
        connect.write_one_register(register_=connect.register_set_i_weld[0],
                                    value_=sw_iweld,
                                    degree_=connect.register_set_i_weld[1])
        appl.progress_bar['value'] = sw_iweld
        # Чтение с накопителя уставки и калибровочных коэффициентов источника фокусировки
        dict_rc = sfoc.readConfig() # dict of parameters in config
        time.sleep(0.7)
        dac.write_byte_dac(byte=sfoc.calculateDAC(dict_rc))
        
        dac_out = sfoc.calculateDAC(dict_rc)
        print(dac_out)

        #dac.write_byte_dac(byte=dac_out)

    else:
        time.sleep(1)
        error_log('Can`t connected to system: {e}')
        print('not connect')

        # reconnect 
        set_start_system(connect, swiweld, dac,sfoc)
        

def view_indicator_system(appl,parameters_:dict):
    appl.change_indicator(parameters_)


def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)
    appl.change_parameters(parameters_)

def view_indicator_error(appl, statsyst):
    appl.change_label_err(appl.indicator_error, statsyst)

def view_progressbar(appl,startiweld): 
    appl.change_progressbar(appl.progress_bar,startiweld) 

#---------------------------------------------------------------------#

def debug_priint():
    while True:
        print(status_system, '\n', parameters_values, '\n', f'err:{stat_err}',
                    '\n', f'err__last:{stat_err_last}')
        time.sleep(3)


if __name__ == "__main__":

    gpio.set_start_state()
    # dac.set_dac_in_null()
    # print(gpio)
    
    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob() # listen knobs

    root = Tk()
    root.geometry("850x500+50+50")  # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    application = MainWindow(root)
    # root.attributes('-fullscreen', True)  #на весь экран
    root.configure(background=application.main_bg)
    application.mGrid()
    
    set_start_system(application, connect_mb, switch, dac, sfoc)
    
    system_parameters = connect_mb.read_all_parameters()
    status_system = connect_mb.read_status_system()
    start_iweld = switch.value_iweld()
    
    print(status_system, '\n', system_parameters)

    view_current_parameters(application, system_parameters)
   
    view_indicator_system(application, status_system)
    view_progressbar(application, start_iweld)
    
    print(status_system)
    root.mainloop()




