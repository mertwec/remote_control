#!/usr/bin/python3.7


import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import minimalmodbus
import asyncio

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
    appl_sw.mGrid_sw()
    
    roots.mainloop()

def view_all_display(appl, gpio, parameters_:dict):
    appl.change_all_display(gpio, parameters_)

def view_indicator_system(appl, gpio, parameters_:dict):
    try:
        appl.change_indicator(gpio, parameters_)
    except Exception as e:
        print (f'error in "view_indicator_system": {e}')
        error_log(f'error in "view_indicator_system": {e}')

        time.sleep(0.1)
        view_indicator_system(appl, gpio, parameters_)

def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)
    try:
        appl.change_parameters(parameters_)
    except Exception as e:
        print (f'error in "view_current_parameters": {e}')
        error_log(f'error in "viev_current_parameter": {e}')
        appl.label_title['text'] = '-SPRELI PARAMETERS- status disconnect'
        appl.indicator_error['bg'] = 'red'
        time.sleep(0.1)
        view_current_parameters(appl, parameters_)

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

async def thread_gpio():
    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob() # listen knobs

async def thread_view(application, gpio,start_iweld, system_parameters):
    view_all_display(application, gpio, system_parameters)
    #view_current_parameters(application, system_parameters)       
    #view_indicator_system(application, gpio, status_system)
    view_progressbar(application, start_iweld)

        

def connect_to_system(appl, connect, swiweld, dac, sfoc):
    '''init: проверка связи. конект через modbus'''
    # проверка связи с контроллером
    try:
        conn = connect.check_connect()
        info_log(f'version: {conn}')
        
        set_start_system(appl, connect, swiweld, dac, sfoc)

        system_parameters = connect_mb.read_all_parameters()
        status_system = connect_mb.read_status_system()
        start_iweld = switch.value_iweld()
            
        info_log(f'start parameters: {system_parameters}')    
        print(status_system, '\n', system_parameters)
        
        #thread_gpio()
        #thread_view(appl, gpio, start_iweld, system_parameters)
        
        async def main():
            taskg = asyncio.create_task(thread_gpio())
            taskv = asyncio.create_task(thread_view(appl, gpio, start_iweld, system_parameters))
            
            await taskg
            await taskv
        
        asyncio.run(main())

    except Exception as e:
        print('Error in "conect to system":', e)
        error_log(f'Error in "conect to system": {e}')
        connect_to_system(appl, connect, swiweld, dac, sfoc)
    
    
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
    
    try:
        connect_to_system(application, connect_mb, switch, dac, sfoc)
        info_log('start mainloop')
        root.mainloop()
        
    except Exception as e:
        print(e)
        error_log(f'Error in __main__: {e} ')
        application.disconnect(root)
        connect_to_system(appl, connect, swiweld, dac, sfoc)
        root.mainloop()



