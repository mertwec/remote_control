#!/usr/bin/python3.7


import sys
import time
from tkinter import *
import RPi.GPIO as GPIO
import threading

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

lock = threading.Lock()

def set_start_system(connect, swiweld, dac, sfoc):
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
        connect.write_one_register(register_=connect.register_set_i_weld[0],
                                    value_=sw_iweld,
                                    degree_=connect.register_set_i_weld[1])
        # Чтение с накопителя уставки и калибровочных коэффициентов источника фокусировки
        dict_rc = sfoc.readConfig() # dict of  parameters in config
        dac_out = sfoc.calculateDAC(dict_rc)
        print(dac_out)
        dac.write_byte_dac(byte=dac_out)


    else:
        time.sleep(1)
        error_log('Can`t connected to system: {e}')
        print('not connect')

        set_start_system(connect, swiweld, dac)
        # reconnect ??

def view_indicator_system(appl,parameters_:dict):
    appl.change_indicator(parameters_)
    
    #appl.change_indicator(appl.fild_indicator_AW, parameters_['stat_UACC'])
    #appl.change_indicator(appl.fild_indicator_CH, parameters_['stat_IBOMB'])
    #appl.change_indicator(appl.fild_indicator_WC, parameters_['stat_IWELD'])

def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)
    '''display new value of parameters
    '''
    appl.change_label(appl.label_displ_U_ACC, parameters_['U_ACC'])
    appl.change_label(appl.label_displ_U_POW, parameters_['U_POWER'])
    appl.change_label(appl.label_displ_U_LOCK, parameters_['U_LOCK'])
    appl.change_label(appl.label_displ_U_BOMB, parameters_['U_BOMB'])
    appl.change_label(appl.label_displ_I_BOMB, parameters_['I_BOMB'])
    appl.change_label(appl.label_displ_I_FIL, parameters_['I_FIL'])
    appl.change_label(appl.label_displ_U_WEHNELT, parameters_['U_WEHNELT'])
    appl.change_label(appl.label_displ_AUX, parameters_['AUX'])
    appl.change_label(appl.label_displ_TEMP, parameters_['TEMP'])
    appl.change_label(appl.label_displ_I_WELD, parameters_['I_WELD'])

    #change_label(appl.text_inform, f'''set: U_ACC={parameters_['set_U_ACC']}\n I_BOMB={parameters_['set_I_BOMB']}\nI_WELD={parameters_['sei_I_WELD']}''')

def view_indicator_error(appl, statsyst):
    appl.change_label_err(appl.indicator_error, statsyst)

def view_progressbar(appl,): #switch
    appl.change_progressbar(appl.progress_bar,) #switch)

def view_information(appl, iweld):
    appl.change_information(appl.text_inform, iweld)
    
def udate_parameters():
    global status_system
    global set_i_weld 
    global parameters_values
    while 1:
        with  lock:
            status_system = connect_mb.read_status_system()    
            #stat_err = connect_mb.read_one_register(register_= 1, functioncode_=4)
            #stat_err_last = connect_mb.read_one_register(register_= 2, functioncode_=4)
            set_i_weld = connect_mb.read_one_register(register_= 119, degree_=1)
            parameters_values = connect_mb.read_current_parameters(connect_mb.CURRENT_PARAMETER)
            time.sleep(0.5)    

#---------------------------------------------------------------------#

def debug_priint():
    while True:
        print(status_system, '\n', parameters_values, '\n', f'err:{stat_err}',
                    '\n', f'err__last:{stat_err_last}')
        time.sleep(3)

def general():
    
    set_start_system(connect_mb, switch, dac, sfoc)
    gpio.set_start_state()
    dac.set_dac_in_null()
    # print(gpio)
    
    gpio.run_system_on_signal() # listen on_uacc and on_weld
    gpio.run_system_on_knob() # listen knobs

    status_system = connect_mb.read_status_system()    
    stat_err = connect_mb.read_one_register(register_= 1, functioncode_=4)
    stat_err_last = connect_mb.read_one_register(register_= 2, functioncode_=4)
    set_i_weld = connect_mb.read_one_register(register_= 119, degree_=1)
    parameters_values = connect_mb.read_current_parameters(connect_mb.CURRENT_PARAMETER)
#thread
    my_t = threading.Thread(target=udate_parameters())

    root = Tk()
    root.geometry("850x500+50+50")  # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    application = MainWindow(root)
    # root.attributes('-fullscreen', True)  #на весь экран
    root.configure(background=application.main_bg)
    application.mGrid()
 
    print(status_system, '\n', parameters_values, '\n', f'err:{stat_err}',
    '\n', f'err__last:{stat_err_last}')

    view_current_parameters(application, parameters_values)
    
    #view_indicator_error(application,  status_system)
    view_indicator_system(application, status_system)
    view_information(application, set_i_weld)
    view_progressbar(application,)# switch)
    me_t.start()
    root.mainloop()


if __name__ == "__main__":

    print(sfoc)

    general()




