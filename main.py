#!/usr/bin/python3.7

import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import minimalmodbus
#import asyncio
import threading
from multiprocessing import Process

sys.path.append(['/home/pi/spreli/remote_control',
                '/home/pi/spreli/remote_control/modules'])

from modules.mask_logging import *

from modules.display_GUI import MainWindow
from modules.in_out_buttons import PinIO
from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC


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

def thread_gpio():
    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob()   # listen knobs

def thread_view(application, gpio, start_iweld, system_parameters):
    print('start "change_all_display"')
    application.change_all_display(gpio, start_iweld, system_parameters)

def thread_mainloop(root):
    print('start mainloop')
    info_log('start mainloop')
    root.mainloop()      

def main_connect_to_system(appl, connect, swiweld, dac, sfoc):
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
        print(f'system_parameters:{system_parameters} \nI weld: {start_iweld}')
        
        #GIL
        '''
        gpio.run_system_on_signal() # listen on_uacc and on_weld
        gpio.run_system_on_knob()   # listen knobs
        application.change_all_display(gpio, start_iweld, system_parameters)
        '''
        #Thread
        
        run1 = threading.Thread(target=gpio.run_system_on_signal)
        run2 = threading.Thread(target=gpio.run_system_on_knob)
        run3 = threading.Thread(target=application.change_all_display,
                                    args=(gpio, start_iweld, system_parameters))
        run4 = threading.Thread(target=gpio.run_knob_iweld)
        
        run4.daemon = True
        run1.daemon = True
        run2.daemon = True
        run3.daemon = True
        
        run1.start()
        run2.start()
        run3.start()
        run4.start()
       
    except Exception as e:
        print('Error in "conect to system":', e)
        error_log(f'Error in "conect to system": {e}')
        time.sleep(0.05)
        main_connect_to_system(appl, connect, swiweld, dac, sfoc)
    
    
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
    

    main_connect_to_system(application, connect_mb, switch, dac, sfoc) 
    root.mainloop()       

    #application.disconnect(root)




