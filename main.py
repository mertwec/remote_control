#!/usr/bin/python3.7

import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import minimalmodbus
#import threading

from modules.mask_logging import *
from modules.display_GUI import MainWindow
from modules.in_out_buttons import PinIO, check_system_knobs
#check_system_knobs -- переменная служащая для определения включать или нет кнопки на пульте

from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC
'''
sys.path.append(['/home/pi/spreli/remote_control',
                '/home/pi/spreli/remote_control/modules'])
'''
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

def update_all_display(appl, gpio, connect_mb, startiweld, system_parameters):
    # read current parameters
    try:            
        system_parameters = connect_mb.read_all_parameters()
        if isinstance(system_parameters, dict):            
            status_system = connect_mb.parsing_status_system(system_parameters['status_system'])
            iweld=ExtSwitcher().value_iweld()        
            appl.set_parameters(system_parameters) 
            appl.set_indicator(status_system)
            #self.set_progressbar(startiweld)
            if iweld!=startiweld:
                appl.progress_bar['value'] = iweld
                startiweld = iweld

                connect_mb.write_one_register(
                                    register_=connect_mb.set_points['set_iweld'][0],
                                    value_=iweld,
                                    degree_=connect_mb.set_points['set_iweld'][1])
            
            gpio.read_outside_knob(status_system)                
            gpio.set_output_VD(status_system, 
                                value_ibomb=system_parameters['I_BOMB'],
                                setted_ibomb=system_parameters['sets_IBOMB']) #register
        else:
            print('____________________________________________')
            appl.master.update()
            print(f'error in {update_all_display.__name__}: {system_parameters}')
            error_log(f'error in {update_all_display.__name__}: {system_parameters}')
                   
        appl.master.update_idletasks()
        appl.master.after(appl.time_total_update, 
                        update_all_display, 
                        appl, gpio, connect_mb, startiweld, system_parameters)
    except Exception as e:
        print (f'error in UPDATE_all: {e}')
        time.sleep(0.1)
        appl.master.after(appl.time_total_update, 
                        update_all_display, 
                        appl, gpio, connect_mb, startiweld, system_parameters)
                        
def main_connect_to_system(appl, gpio, connect_mb, swiweld, dac, sfoc):
    '''init: проверка связи. конект через modbus'''
    # проверка связи с контроллером
    try:
        conn = connect_mb.check_connect()
        info_log(f'version: {conn}')
        
        set_start_system(appl, connect_mb, swiweld, dac, sfoc)

        system_parameters = connect_mb.read_all_parameters()
        status_system = connect_mb.read_status_system()
        start_iweld = switch.value_iweld()
            
        info_log(f'start parameters: {system_parameters}')   
        print(f'system_parameters:{system_parameters} \nI weld: {start_iweld}')
        
        #GIL
        #'''
        gpio.run_system_on_signal() # listen on_uacc and on_weld
        gpio.run_system_on_knob()   # listen knob
        
        update_all_display(application, gpio, connect_mb, start_iweld, system_parameters)

        #'''
        #Thread
        '''
        run1 = threading.Thread(target=gpio.run_system_on_signal, daemon=True)
        run2 = threading.Thread(target=gpio.run_system_on_knob,daemon=True)
        run3 = threading.Thread(target=update_all_display,
                                    args=(application, gpio, connect_mb, start_iweld, system_parameters),daemon=True)
        run4 = threading.Thread(target=gpio.run_knob_iweld,daemon=True)
        run1.start()
        run2.start()
        run3.start()
        run4.start()
        '''
    except Exception as e:
        print('Error in "main conect to system":', e)
        error_log(f'Error in "main conect to system": {e}')
        time.sleep(0.05)
        #main_connect_to_system(appl, gpio, connect_mb, swiweld, dac, sfoc)    
        
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
    root.attributes('-fullscreen', True)    # на весь экраna
    root.config(cursor='none')              # скрыть курсор
    application = MainWindow(root)
    application.mGrid()    

    main_connect_to_system(application, gpio, connect_mb, switch, dac, sfoc) 
    root.mainloop()
    #application.disconnect(root)




