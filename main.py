#!/usr/bin/python3.7


import sys
import time
from tkinter import *
import RPi.GPIO as GPIO

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
switch_iweld = ExtSwitcher()
dac = DACModule()

register_set_I_WELD = 119

current_registers={'U_ACC':(3, 2),  # param:(register, degree)
					'I_FIL':(5, 2),
					'I_BOMB':(6, 0),
					'U_BOMB':(7, 0),
					'I_WELD':(4, 1),
					'U_LOCK':(9, 0),
					'AUX':(10, 2),
					'U_WEHNELT':(8, 0),
					'TEMP':(12, 0),
					'U_POWER':(11, 2),
					}
					
execution_commands = {'exec_U_ACC':(1,False),  #  param:(reg,default status)
					'exec_I_WELD':(2,False),
					'exec_I_BOMB':(3,False),}


def set_start_system(connect, swiweld, dac):
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
		connect.write_one_register(register_=register_set_I_WELD,
									value_=sw_iweld, 
									degree_=1)
		# Чтение с накопителя уставки и калибровочных коэффициентов источника фокусировки
		dict_rc = sfoc.readConfig() # dict of  parameters in config
		value_dac = sfoc.calculateDAC(dict_rc)
		dac.write_byte_dac(value_dac)
		
		
	else:
		time.sleep(1)
		error_log('Can`t connected to system: {e}')
		print('not connect')
		
		set_start_system(connect, swiweld, dac)
		# reconnect ??

def view_indicator_system(appl,parameters_:dict):
	
	appl.change_indicator(appl.fild_indicator_AW, parameters_['stat_UACC'])		
	appl.change_indicator(appl.fild_indicator_CH, parameters_['stat_IBOMB'])
	appl.change_indicator(appl.fild_indicator_WC, parameters_['stat_IWELD'])
	
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
	
	#change_label(appl.text_inform, f'''set: U_ACC={parameters_['set_U_ACC']}\n	I_BOMB={parameters_['set_I_BOMB']}\nI_WELD={parameters_['sei_I_WELD']}''')

def view_indicator_error(appl, staterr):
	appl.change_label_err(appl.indicator_error, staterr)

def vieW_progressbar(appl, value_):
	appl.change_progressbar(appl.progress_bar, value_)

#---------------------------------------------------------------------#
		
def general():	
		
	set_start_system(connect_mb, switch_iweld, dac)
	gpio.set_start_state()
	# print(gpio)
	
	
	root = Tk()
	root.geometry("850x500+50+50")  # поместить окно в точку с координатам 100,100 и установить размер в 810x450
	application = MainWindow(root)
	# root.attributes('-fullscreen', True) 	#на весь экран
	root.configure(background=application.main_bg)
	application.mGrid()	
	'''
	connect_mb.write_execution_command(register_=1, value_=1)
	connect_mb.write_execution_command(register_=2, value_=0)
	connect_mb.write_execution_command(register_=3, value_=0)
	time.sleep(0.2)
	'''
	status_system = connect_mb.read_status_system()
	stat_err = connect_mb.read_one_register(register_= 1, functioncode_=4)
	stat_err_last =	connect_mb.read_one_register(register_= 2, functioncode_=4)
	parameters_values = connect_mb.read_current_parameters(current_registers)
	
	print(status_system, '\n', parameters_values, '\n', f'err:{stat_err}',
	'\n', f'err__last:{stat_err_last}')
	
	view_current_parameters(application, parameters_values)
	view_indicator_system(application, status_system)
	view_indicator_error(application, stat_err)
	vieW_progressbar(application, switch_iweld.read_switcher())
	root.mainloop() 




if __name__ == "__main__":

	print(sfoc)
	
	general()




