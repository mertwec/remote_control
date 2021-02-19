import time
import sys
from pprint import pprint

#from mask_logging import *
import minimalmodbus as mm
import serial
from mask_logging import *


class ModbusConnect():
    def __init__(self):
        self.instrument = mm.Instrument(
                            port='/dev/serial0',    #/dev/ttyAMA0 or /dev/serial0
                            slaveaddress=1,
                            mode = mm.MODE_RTU,                            
                            close_port_after_each_call=False,
                            debug = False,
                            )
        self.instrument.serial.baudrate = 115200
        self.instrument.serial.timeout = 3
        
        self.instrument.parity = serial.PARITY_NONE, # 'N'
        self.instrument.stopbits = serial.STOPBITS_ONE,
        self.instrument.bytesize = serial.EIGHTBITS,
       
        #текущие параметры
        self.CURRENT_PARAMETER={'U_ACC':(3, 2),  # param:(register, degree) 
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
        # internal setpoint parameters
        # параметры уставки functionalcode = 3
        self.set_points = {'set_iweld':(119,1),
                            'set_uacc':(117,2),
                            'set_ibomb':(123,1)}
        
            # on/off 
        self.execution_commands = {'exec_U_ACC':(1,False),  #  param:(reg,default status)
                                    'exec_I_WELD':(2,False),
                                    'exec_I_BOMB':(3,False),}
        
    def __str__(self):
        return (f'port = {self.instrument.serial.port},/nbaudrate = {self.instrument.serial.baudrate}')
    
    def check_connect(self):
        ''' check connected (version PO -- register 33 and 34)'''
        check_pass1 = self.instrument.read_register(registeraddress=33,
                            functioncode=4)
        check_pass2 = self.instrument.read_register(registeraddress=34,
                            functioncode=4)
        print(f'connected: version = {check_pass1} {check_pass2}')
        return (check_pass1,check_pass2)
    
    def parsing_status_system(self, bss:bin):
        if len(bss[2:])<16:
            mfullbss=('0'*(16-len(bss[2:]))+bss[2:])[::-1]      
        else:
            mfullbss=bss[2:][::-1]
                        
        return {'stat_UACC':int(mfullbss[10]), #1 reg
                'stat_IBOMB':int(mfullbss[11]), #3 reg
                'stat_IWELD':int(mfullbss[12]), #2 reg
                
                'stat_failure':int(mfullbss[13]),
                'stat_run':int(mfullbss[8])}
    
    def read_status_system(self)->dict:
        ''' 8bit = run 
        
            10bit = UACC 0=off 1=on
            11bit = Ibomb 0=off 1=on
            12bit = Iweld 0=off 1=on
            13bit = failure
        '''
        try:
            status_system = self.instrument.read_register(registeraddress=0,
                                    functioncode=4)
            bss=bin(status_system)
            return self.parsing_status_system(bss)
            
        except IOError as ioe:
            print (f'Error reading "status system": {ioe}')
            debug_log(f'Error reading "status system": {ioe}')
            time.sleep(0.025)
            print('try reconect...')
            self.read_status_system()
            print('reconect')
    
    def read_current_parameters(self, curr_param:dict)->dict:  # curr_param = {param:register}
        '''
        чтение параметров по модбас из hvmcuti
        для отображения на дисплее
        
        '''
        total_list = []
        for i in curr_param.keys():     
            reg = curr_param[i][0]
            degree = curr_param[i][1]
            if i == 'TEMP':
                value_param = self.read_one_register(reg, functioncode_=4,
                                                        degree_=degree, 
                                                        signed_=True)
            else:
                value_param = self.read_one_register(reg, functioncode_=4,
                                                        degree_=degree, 
                                                        signed_=False)
            #info_log(f'current param: {i}:{value_param}')
            total_list.append((i,value_param))
        return dict(total_list)
    

    def write_execution_command(self, register_, value_):
        '''
        set execution command: true = on, false = off
        functioncode=5
			reg1 -- U_ACC
			reg2 -- I_WELD
			reg3 -- I_FIL
        '''
        try:
            self.instrument.write_bit(registeraddress=register_,
                                        value=value_,                                   
                                        functioncode=5,)
                                        
            print(f'{register_} - writed = {value_}' )
            info_log(f'{register_} - writed = {value_}' )
        except IOError as ioe:
            print (f'Error writing "execution_command": {ioe}')
            time.sleep(0.025) # time connection to system
            print('try reconect...')
            self.write_execution_command(register_, value_)
            print('reconect')
        

    def read_one_register(self, register_,functioncode_=3, degree_=0, signed_=False):
        try:
            reg_value = self.instrument.read_register(registeraddress=register_,
                                    number_of_decimals=degree_,
                                    functioncode=functioncode_,
                                    signed=signed_)
            print(f'read from {register_} = {reg_value}')
            info_log(f'read from {register_} = {reg_value}')
            return reg_value

        except IOError as ioe:
            print (f'Error reading one register: {ioe}')
            error_log(f'Error reading one register: {ioe}')
            time.sleep(0.025) # time connection to system
            print('try reconect...')
            self.read_one_register(register_)
            print('reconect')
    
    
    def write_one_register(self, register_, value_, degree_=0, signed_= False):
        try:
            self.instrument.write_register(registeraddress=register_,
                                            value=value_,
                                            number_of_decimals=degree_,
                                            functioncode=6,
                                            signed=signed_,)
            print(f'{register_} - writed' )
        
        except IOError as ioe:
            print(f'Error writing one register: {ioe}')
            time.sleep(0.025)
            print('try reconect...')
            self.write_one_register(register_,value_, degree_)
            print('reconect')
        
    
    def  read_all_parameters(self)->dict:
        try:
            unsigned_all_param = self.instrument.read_registers(registeraddress=0,
                                                        number_of_registers=25, 
                                                        functioncode=4)
            # преобразование всех чисел в знаковые
            signed_all_param = [i-65536 if i>32767 else i for i in unsigned_all_param]  # если число больше 32767 то оно отрицательно
        
            return {'U_ACC':round(signed_all_param[3]*10**(-2),2),                    
                    'I_FIL':round(signed_all_param[5]*10**(-2),2),
                    'I_BOMB':round(signed_all_param[6]*10**(-1),2),
                    'U_BOMB':signed_all_param[7], 
                    'I_WELD':round(signed_all_param[4]*10**(-1),2),
                    'U_LOCK':signed_all_param[9],
                    'AUX':round(signed_all_param[10]*10**-2, 2),
                    'U_WEHNELT':signed_all_param[8],
                    'TEMP':signed_all_param[12],
                    'U_POWER':round(signed_all_param[11]*10**-2,2),
                    
                    'Error_current':unsigned_all_param[1],
                    'Error_last':unsigned_all_param[2],
                    
                    'sets_UACC':round(signed_all_param[13]*10**(-2),2),
                    'sets_IWELD':round(signed_all_param[14]*10**(-1),2),
                    'sets_IBOMB':round(signed_all_param[16]*10**(-1),2),
                    
                    'status_system':bin(unsigned_all_param[0]),
                    }

        except IOError as ioe:
            info_log(f'Error reading all param: {ioe}')
            return (ioe)
           
            
    def close_connect(self):
        self.instrument.serial.close()

            
if __name__ == "__main__":
    from mask_logging import *
    con_ = ModbusConnect()      
    try:        
        con_.check_connect()
        #info_log(f'{con_.read_one_register(141,3,3)}')
        print(con_.instrument.serial)
        pprint(con_.read_current_parameters(con_.CURRENT_PARAMETER))
        
        con_.write_execution_command(register_=1, value_=0) #uacc
        con_.write_execution_command(register_=2, value_=0) #iweld
        con_.write_execution_command(register_=3, value_=0) #ibomb
        time.sleep(0.1)
        print('\tstatus system:\n')
        pprint(con_.read_status_system())
        print('\tall  parameters: \n', )
        pprint(con_.read_all_parameters())
    
    except Exception as e:
        print(e)        
    finally:
        con_.close_connect()

