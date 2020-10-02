#!/usr/bin/python3.7


import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import minimalmodbus

sys.path.append(['/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI',
                '/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI/modules'])

from modules.mask_logging import *

from modules.display_GUI import MainWindow,StartWindow
from modules.in_out_buttons import PinIO
from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC



        
def open_startWindow():
    roots = Tk()
    roots.geometry("500x350+25+25")
    appl_sw = StartWindow(roots)
    roots.configure(background = appl_sw.main_bg)  
    appl_sw.mGrid_sw()
    
    roots.mainloop()

def view_indicator_system(appl,parameters_:dict):
    appl.change_indicator(parameters_)

def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)
    appl.change_parameters(parameters_)

def view_indicator_error(appl, statsyst):
    appl.change_label_err(appl.indicator_error, statsyst)

def view_progressbar(appl,startiweld): 
    appl.change_progressbar(appl.progress_bar,startiweld) 

#---------------------------------------------------------------------#
def change_use_chanel(i:bool):
    """
    i=True remote control
    i=False internal control
    """
    # using the internal welding current channel
    connect_mb.write_one_register(118,i)  # i weld
    connect_mb.write_one_register(116,i)  # uacc
    connect_mb.write_one_register(122,i) # i bomb

def set_start_system(appl, connect, swiweld, dac, sfoc):
    appl.label_title['text'] = '-SPRELI PARAMETERS- status: conected'
    
    # Передача команд на выключение источника высокого напряжения, тока бомбардировки и тока сварки
    ce=connect.execution_commands
    for i in ce:
        connect.write_execution_command(register_=ce[i][0], value_=ce[i][1])
    info_log(f'Settings connection: {connect.read_status_system()}')

    # Задание тока сварки в соответствии с положением переключателя
    sw_iweld = swiweld.value_iweld()
    info_log(f'on switch IWELD: {sw_iweld}')
    connect.write_one_register(register_=connect.register_set_i_weld[0],
                                value_=sw_iweld,
                                degree_=connect.register_set_i_weld[1])
    appl.progress_bar['value'] = sw_iweld
    
    # Чтение с накопителя уставки и калибровочных коэффициентов источника фокусировки
    dict_rc = sfoc.readConfig() # dict of parameters in config
    info_log(f'settings config: {dict_rc}')
    dac_out = sfoc.calculateDAC(dict_rc)
    dac.write_byte_dac(byte=dac_out)        
    debug_log(f'DAC OUT = {dac_out}')



def general():

    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob() # listen knobs

    system_parameters = connect_mb.read_all_parameters()
    status_system = connect_mb.read_status_system()
    start_iweld = switch.value_iweld()

        
    info_log(f'start parameters: {system_parameters}')
    
    print(status_system, '\n', system_parameters)

    view_current_parameters(application, system_parameters)       
    view_indicator_system(application, status_system)
    view_progressbar(application, start_iweld)

def connect_to_system(appl, connect, swiweld, dac, sfoc):
    '''init: проверка связи. конект через modbus'''
    # проверка связи с контроллером
    try:
        conn = connect.check_connect()
        info_log(f'version:{conn}')
        set_start_system(appl, connect, swiweld, dac, sfoc)
        general()
        
    except Exception as e:
        print(e)
        connect_to_system(appl, connect, swiweld, dac, sfoc)
        
        
    
    '''if conn:
        info_log(f'version:{conn}')
        set_start_system(appl, connect, swiweld, dac, sfoc)

    else:
        time.sleep(1)
        appl.label_title['text'] = '-SPRELI PARAMETERS- status: not conection'
        error_log('Can`t connected to system: no connect by modbus')
        error_log('Try reconnect...')
        # reconnect 
        connect_to_system(appl, connect, swiweld, dac, sfoc)
        
        '''


if __name__ == "__main__":
    
    connect_mb = ModbusConnect()
    sfoc = SettFOC(path='/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI/settings_focus.conf')
    gpio = PinIO(GPIO)
    switch = ExtSwitcher()
    dac = DACModule()
    
    gpio.set_start_state()    
    info_log(f'modbus: {connect_mb} \n switcher: {switch}')
    info_log(f'{gpio}')

    root = Tk()
    root.geometry("850x500+50+50")  # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    #root.attributes('-fullscreen', True)  #на весь экраna
    application = MainWindow(root)
    application.mGrid()
    
    connect_to_system(application, connect_mb, switch, dac, sfoc)

    root.mainloop()
'''
    except Exception as e:
        print(f'---------------\n\n\n-----------------------')
        #error_log(f'unknown error \n\t\t{e}')
        #root.mainloop()
        application.label_title['text'] = '-SPRELI PARAMETERS- status: reconection'
        time.sleep(1)
        
        connect_to_system(application, connect_mb, switch, dac, sfoc)

    else:
        pass
        
        
'''


