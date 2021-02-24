import time
import sys
from pprint import pprint

import minimalmodbus as mm
import serial
from mask_logging import *


# декоратор переподключения команд обращения к модбас
def decorator_reconnect_for_exeption(function_):
    def func_wrapper(self,*args,**kwargs):
        try:
            return function_(self,*args,**kwargs)            
        except Exception as e: #IOError
            print (f'Error in {function_.__name__}: {e}')
            info_log(f'Error in {function_.__name__}: {e}')
            time.sleep(0.05)           # time modbus connection = 0.014/0.017 s
            print('try reconect...')            
            return func_wrapper(self,*args,**kwargs)
            info_log('reconnect')
            print('reconnect')
    return func_wrapper


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
        
        self.set_points = {'set_iweld':(113,1),
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
        #print(f'parsing stat syst:/n bss={bss}')
        if len(bss[2:])<16:
            mfullbss=('0'*(16-len(bss[2:]))+bss[2:])[::-1]      
        else:
            mfullbss=bss[2:][::-1]                                            
        return {'stat_UACC':int(mfullbss[10]), #1 reg
                'stat_IBOMB':int(mfullbss[11]), #3 reg
                'stat_IWELD':int(mfullbss[12]), #2 reg
                
                'stat_failure':int(mfullbss[13]),
                'stat_run':int(mfullbss[8])}
    
    @decorator_reconnect_for_exeption
    def read_status_system(self)->dict:
        ''' 8bit = run 
        
            10bit = UACC 0=off 1=on
            11bit = Ibomb 0=off 1=on
            12bit = Iweld 0=off 1=on
            13bit = failure
        '''
        status_system = self.instrument.read_register(registeraddress=0,
                                functioncode=4)
        bss=bin(status_system)
        return self.parsing_status_system(bss)

    def read_current_parameters(self, curr_param:dict)->dict:  # curr_param = {param:register}
        '''
        НЕ ИСПОЛЬЗУЕТСЯ  вместо нее "read_all_parameters"        
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
    
    @decorator_reconnect_for_exeption
    def write_execution_command(self, register_, value_):
        '''
        set execution command: true = on, false = off
        functioncode=5
			reg1 -- U_ACC
			reg2 -- I_WELD
			reg3 -- I_FIL
        '''
        self.instrument.write_bit(registeraddress=register_,
                                    value=value_,                                   
                                    functioncode=5,)
                                    
        print(f'{register_} - writed = {value_}' )
        info_log(f'{register_} - writed = {value_}' )

    @decorator_reconnect_for_exeption
    def read_one_register(self, register_,functioncode_=3, degree_=0, signed_=False):
        reg_value = self.instrument.read_register(registeraddress=register_,
                                number_of_decimals=degree_,
                                functioncode=functioncode_,
                                signed=signed_)
        print(f'read from {register_} = {reg_value}')
        info_log(f'read from {register_} = {reg_value}')
        return reg_value

    @decorator_reconnect_for_exeption
    def write_one_register(self, register_, value_, degree_=0, signed_= False):
        if value_ == None:
            pass
        else:
            self.instrument.write_register(registeraddress=register_,
                                                value=value_,
                                                number_of_decimals=degree_,
                                                functioncode=6,
                                                signed=signed_,)
            print(f'OK-{register_} - writed {value_}' )
            info_log(f'{register_} = writed {value_}')     
        
    @decorator_reconnect_for_exeption
    def  read_all_parameters(self)->dict:
        try:
            unsigned_all_param = self.instrument.read_registers(registeraddress=0,
                                                        number_of_registers=25, 
                                                        functioncode=4)
            # преобразование всех чисел в знаковые (может быть отрицателен)
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
    
    def parsing_parameters_for_label(self, parameters:dict):
        if isinstance (parameters, dict):
            pass
    
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
        print('\tall  parameters: \n', )
        pprint(con_.read_all_parameters())
        
        con_.write_execution_command(register_=1, value_=0) #uacc
        con_.write_execution_command(register_=2, value_=0) #iweld
        con_.write_execution_command(register_=3, value_=0) #ibomb
        time.sleep(0.1)
        
        print('\tstatus system:\n')
        pprint(con_.read_status_system())
        
        '''
        mall_param = con_.instrument.read_registers(registeraddress=0,
                                                        number_of_registers=25, 
                                                        functioncode=4)
        print(mall_param)
        print(mall_param[0])
        pprint(con_.read_all_parameters())
        '''
    except Exception as e:
        print(e)        
    finally:
        con_.close_connect()

