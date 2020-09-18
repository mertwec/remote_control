#!/usr/bin/env python3
import sys
import time
from tkinter import *
import RPi.GPIO as GPIO

sys.path.append('/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI')

from modules.mask_logging import *

from modules.display_GUI import MainWindow
from modules.in_out_buttons import PinIO
from modules.i2c_bus import DACModule, ExtSwitcher
from modules.modbus485_mm import ModbusConnect
from modules.focusing_config import SettFOC

connect_mb = ModbusConnect()
sfoc = SettFOC()#path='/home/pi/Desktop/pult_spreli_program/modules/settings_focus.conf')
gpio = PinIO(GPIO)

UACC = 116 # Использование канала задания высокого напряжения (0-off;1-on)
IBOMB = 122 # Использование канала задания тока бомбардировки (0-off;1-on)
IWELD = 118 # Использование канала задания тока сварки  (0-off;1-on)

current_registers={'U_ACC':(3, 2),  # param:(register, degree)
					'I_FIL':(5, 2),
					'I_BOMB':(6, 0),
					'U_BOMB':(7, 0),
					'I_WELD':(4, 1),
					'U_LOCK':(9, 0),
					'AUX':(10, 2),
					'U_WEHNELT':(8, 0),
					'TEMP':(12, 0),
					'U_POWER':(11, 2)
					}


def set_start_system(connect):
	'''проверка связи. конект через modbus'''
	# проверка связи с контроллером
	conn = connect._check_connect()
	if conn:
		info_log(f'Settings connection: {conn}')		
		for reg in [UACC, IBOMB, IWELD]:
			connect.write_one_register(reg, 0)
			status = connect.read_one_register(reg)
			print(f'{reg}: {status}')		
			
		# init
	else:
		time.sleep(1)
		error_log('Can`t connected to system: {e}')
		print('not connect')
		# reconnect ??
		
def read_current_parameters(curr_param:dict)->dict:  # curr_param = {param:register}
	'''
	чтение параметров по модбас из hvmcuti
	для отображения на дисплее
	'''
	total_list = []
	for i in curr_param.keys():		
		reg = curr_param[i][0]
		degree = curr_param[i][1]
		if i == 'TEMP':
			value_param = connect_mb.read_one_register(reg, functioncode_=4,
													degree_=degree, 
													signed_=True)
		else:
			value_param = connect_mb.read_one_register(reg, functioncode_=4,
													degree_=degree, 
													signed_=False)
		info_log(f'current param: {i}:{value_param}')
		total_list.append((i,value_param))
	return dict(total_list)

def change_label(label, valueparam):
	'''help function'''
	label.config(text=str(valueparam))	
	label.after(300, change_label,label,valueparam)
	
def view_current_parameters(appl, parameters_:dict):  # param = (parameter, value)  
	'''display new value of parameters
	'''     
	change_label(appl.label_displ_U_ACC, parameters_['U_ACC'])
	change_label(appl.label_displ_U_POW, parameters_['U_POWER'])
	change_label(appl.label_displ_U_LOCK, parameters_['U_LOCK'])
	change_label(appl.label_displ_U_BOMB, parameters_['U_BOMB'])
	change_label(appl.label_displ_I_BOMB, parameters_['I_BOMB'])
	change_label(appl.label_displ_I_FIL, parameters_['I_FIL'])
	change_label(appl.label_displ_U_WEHNELT, parameters_['U_WEHNELT'])
	change_label(appl.label_displ_AUX, parameters_['AUX'])
	change_label(appl.label_displ_TEMP, parameters_['TEMP'])
	change_label(appl.label_displ_I_WELD, parameters_['I_WELD'])
	
		
def general():	
		
	set_start_system(connect_mb)
	gpio.set_start_state()
	print(gpio)
	
	
	root = Tk()
	root.geometry("850x500+50+50")  # поместить окно в точку с координатам 100,100 и установить размер в 810x450
	application = MainWindow(root)
	# root.attributes('-fullscreen', True) 	#на весь экран
	root.configure(background=application.main_bg)
	application.mGrid()	
	
	parameters_values = read_current_parameters(current_registers)
	print(parameters_values)
	view_current_parameters(application, parameters_values)
	
	root.mainloop() 




if __name__ == "__main__":

	print(sfoc)
	
	general()




