import time
import sys
from pprint import pprint

#from mask_logging import *
import minimalmodbus as mm
import serial



class ModbusConnect():
	def __init__(self):
		self.instrument = mm.Instrument(
    						port='/dev/serial0', #/dev/ttyAMA0 or /dev/serial0
                            slaveaddress=1,
                            mode = mm.MODE_RTU,                            
                            close_port_after_each_call=False,
                            debug = False,
                            )
		self.instrument.serial.baudrate = 115200
		self.instrument.serial.timeout = 3
		
		self.instrument.parity=serial.PARITY_NONE, # 'N'
		self.instrument.stopbits=serial.STOPBITS_ONE,
		self.instrument.bytesize=serial.EIGHTBITS,

	def __str__(self):
		return (f'port = {self.instrument.serial.port}, baudrate = {self.instrument.serial.baudrate}')
    
	def _check_connect(self):
		''' check connected (state of the system -- register 0)'''
		try:
			check = self.instrument.read_register(registeraddress=0,
								functioncode=4)
			print(f'connected: system check = {check}')
			#info_log(f'connected: system check = {check}')
			return check
		except Exception as e:			
			print('no conn:', e)
			#error_log(f'Can`t connected to system: {e}')
			return False
    

	def read_one_register(self, register_,functioncode_=3, degree_=0, signed_=False):
		try:
			reg_value = self.instrument.read_register(registeraddress=register_,
									number_of_decimals=degree_,
									functioncode=functioncode_,
									signed=signed_)
			return reg_value
		except Exception as e:
			print(e)
		
			

	def write_one_register(self, register_, value_, degree_=0, signed_= False):
		try:
			self.instrument.write_register(registeraddress=register_,
										value=value_,
										number_of_decimals=degree_,
										functioncode=6,
										signed=signed_,)
			print(f'{register_} - writed' )
		except Exception as e:
			print(f'Error writing: {e}')
			#warning_log(f'Error writing: {e}')


	def close_connect(self):
		self.instrument.serial.close()
		print()

			
if __name__ == "__main__":
	from mask_logging import *
	
	try:
		con_ = ModbusConnect()
		con_._check_connect()
		#info_log(f'{con_.read_one_register(141,3,3)}')
		print(con_.instrument.serial)
	except Exception as e:
		print(e)		
	finally:
		con_.close_connect()

