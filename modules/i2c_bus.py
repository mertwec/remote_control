#!/usr/bin/env python3

import time
from smbus import SMBus


class MainBus:
    bus = SMBus(1)
    
    @staticmethod
    def closebus(bus):
        #self.bus.write_byte(self.ADR_EXPCH,0b11111111)
        bus.close()
        print('bus is clossed.....')
        time.sleep(0.25)


class DACModule(MainBus):
    def __init__(self, DEV_ADDR=(0x48, 0x49)):
        # Addres device = 0x48 or 0x49
        self.DAC_ADDR1=DEV_ADDR[0]
        self.DAC_ADDR2=DEV_ADDR[1] # not use
        self.dac_ch = 0b1000000     # 0x40
        
        self.I_FOC = 0   # tок фокусировки, диапазон от 0 до 1000мА
        self.I_FOC_MIN = 0 #диапазон от 0 до 1000мА
        self.I_FOC_MAX = 0 #диапазон от 0 до 1000мА
        self.DAC_MIN = 0   #диапазон от 0 до 255
        self.DAC_MAX = 0   # диапазон от 0 до 255
                
        
    def __str__(self):
        mess = f'PCF8591:/n --addres:{self.DAC_ADDR1}  and {self.DAC_ADDR2}'
        return mess
        

    
    def set_dac_in_null(self):
        self.write_byte_dac(self.DAC_ADDR1,0)
        self.write_byte_dac(self.DAC_ADDR2,0)
    
    def write_byte_dac(self, ADDR, byte:int): 
        """byte = 0 to 255 """
        self.bus.write_byte_data(ADDR, self.dac_ch, byte)

           
    def calculateDAC(self, parameter:dict):
        self.DAC = parameter['I_FOC']*(parameter['DAC_MAX']-parameter['DAC_MIN'])/(parameter['I_FOC_MAX']-parameter['I_FOC_MIN'])
        print(self.DAC)
        return self.DAC
	

class ExtSwitcher(MainBus):
    _keygen = [7,11,13,14,127,191,223,239,247,251,253,254]
    _i_weld = [1, 5, 10, 20, 35, 50, 75, 100, 130, 160, 200, 250]
    
    def __init__(self, DEV_ADDR=(0x38, 0x39), _keygen=_keygen,_i_weld=_i_weld):
        self.addr_exp1 = DEV_ADDR[0] # 0x38 exp1
        self.addr_exp2 = DEV_ADDR[1] # 0x38 exp2
        self.DEV_ADDR = DEV_ADDR
        
        self.key_welding = dict(zip(_keygen, _i_weld))
        
    def __str__(self):
        return f'status switcher: {self.read_switcher()}'

    def read_exp(self, EXP_ADDR) -> int:
        '''
        чтение состояния пинв expander по адресу     EXP_ADDR
        '''           
        value = self.bus.read_byte(EXP_ADDR)        
        return value
    
    def read_switcher(self) -> int:        
        '''
        считывание значения переключателя
        вернет одно из значений _keygen
        '''         
        part1 = self.read_exp(self.addr_exp1)
        part2 = self.read_exp(self.addr_exp2)
        if part1 == 255:
            switch = part2 # _keygen = 7,11,13,14
        else:
            switch = part1 # _keygen = 127,191,223,239,247,251,253,254
        return switch
    
    
    def set_value_from_key(self):
        '''
        демо заготовка
        '''        
        vk = {key:val+1 for val, key in enumerate(self._keygen)}
        return vk[self.read_switcher()]

if __name__ == '__main__':
    pass
    #exp = ExtSwitcher()
    #print(exp.key_welding)
          

