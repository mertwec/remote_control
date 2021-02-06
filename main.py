#!/usr/bin/python3.7

import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import minimalmodbus
import asyncio

sys.path.append(['/home/pi/spreli/remote_control',
                '/home/pi/spreli/remote_control/modules'])

from modules.mask_logging import *

from modules.display_GUI import MainWindow,StartWindow
from modules.in_out_buttons import PinIO
from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC


def view_all_display(appl, gpio, parameters_:dict):
    '''main display update loop wrapper'''
    try:
        appl.change_all_display(gpio, parameters_)
    except Exception as e:
        print (f'error in "view_all_display": {e}')
        error_log(f'error in "view_all_display": {e}')
        appl.label_title['text'] = '-SPRELI PARAMETERS- status disconnect'
        appl.indicator_error['bg'] = 'red'
        time.sleep(0.1)
        view_all_display(appl, gpio, parameters_)
        
def view_indicator_system(appl, gpio, parameters_:dict):
    '''temp    '''
    try:
        appl.change_indicator(gpio, parameters_)
    except Exception as e:
        print (f'error in "view_indicator_system": {e}')
        error_log(f'error in "view_indicator_system": {e}')

        time.sleep(0.1)
        view_indicator_system(appl, gpio, parameters_)

def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)
    '''temp    '''
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
    воспомогательная ф-ция -- задаётся внешнее или внутреннее чтение уставок
    i=True: remote control
    i=False: internal control
    """
    # using the internal welding current channel
    connect_mb.write_one_register(118,i)  # i weld
    connect_mb.write_one_register(116,i)  # uacc
    connect_mb.write_one_register(122,i) # i bomb

def set_start_system(appl, connect, swiweld, dac, sfoc):
    # начальные уставки системы при запуске
    appl.label_title['text'] = '-SPRELI PARAMETERS- status: conected'
    
    # Передача команд на выключение источника высокого напряжения, тока бомбардировки и тока сварки
    ce=connect.execution_commands
    for i in ce:
        connect.write_execution_command(register_=ce[i][0], value_=ce[i][1])
    info_log(f'Settings connection: {connect.read_status_system()}')

    # Задание тока сварки в соответствии с положением переключателя
    sw_iweld = swiweld.value_iweld()
    info_log(f'on switch IWELD: {sw_iweld}')
    connect.write_one_register(register_=connect.set_points['set_iweld'][0],
                                value_=sw_iweld,
                                degree_=connect.set_points['set_iweld'][1],)
    appl.progress_bar['value'] = sw_iweld
    
    # Чтение с накопителя уставки и калибровочных коэффициентов источника фокусировки
    dict_rc = sfoc.readConfig() # dict of parameters in config
    info_log(f'settings config: {dict_rc}')
    dac_out = sfoc.calculateDAC(dict_rc)
    dac.write_byte_dac(byte=dac_out)        
    debug_log(f'DAC OUT = {dac_out}')

async def thread_gpio():
    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob()   # listen knobs

async def thread_view(application, gpio,start_iweld, system_parameters):
    view_all_display(application, gpio, system_parameters)
    #view_current_parameters(application, system_parameters)       
    #view_indicator_system(application, gpio, status_system)
    view_progressbar(application, start_iweld)

async def thread_mainloop(root):
    info_log('start mainloop')
    root.mainloop()      

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
        print(f'status system: {status_system} \n, system_parameters:{system_parameters}')
        
        #thread_gpio()
        #thread_view(appl, gpio, start_iweld, system_parameters)
        
        async def main():
            taskg = asyncio.create_task(thread_gpio())
            taskv = asyncio.create_task(thread_view(appl, gpio, start_iweld, system_parameters))
            taskm = asyncio.create_task(thread_mainloop(root))
            
            await taskg
            await taskv
            await taskm
        
        asyncio.run(main())

    except Exception as e:
        print('Error in "conect to system":', e)
        error_log(f'Error in "conect to system": {e}')
        connect_to_system(appl, connect, swiweld, dac, sfoc)
    
    
if __name__ == "__main__":
    # создание экземпляров
    connect_mb = ModbusConnect()
    sfoc = SettFOC(path='/home/pi/spreli/remote_control/settings_focus.conf')
    gpio = PinIO(GPIO)
    switch = ExtSwitcher()
    dac = DACModule()
    
    # уставки начального состояния пинов GPIO
    gpio.set_start_state()     
    
    info_log(f'modbus: {connect_mb}')
    info_log(f'switcher: {switch}')
    info_log(f'{gpio}')
    
    root = Tk()
    #root.geometry("850x500+50+50")          # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    root.attributes('-fullscreen', True)    #на весь экраna
    root.config(cursor='none')              # скрыть курсор
    application = MainWindow(root)
    application.mGrid()
    
    try:
        connect_to_system(application, connect_mb, switch, dac, sfoc)
        
        #info_log('start mainloop')
        #root.mainloop()
        
    except Exception as e:
        print(e)
        error_log(f'Error in __main__: {e} ')
        time.sleep(0.1)
        application.disconnect(root)
        error_log('try reconnect')
        connect_to_system(appl, connect, swiweld, dac, sfoc)
        root.mainloop()



