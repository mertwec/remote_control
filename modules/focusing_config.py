from configparser import ConfigParser


class SettFOC(ConfigParser):
    #path = 'settings_focus.conf'
    def __init__(self, path = '/home/pi/spreli/remote_control/settings_focus.conf'):
        self.path = path
        self.start_valueparam = {'start_I_WELD':1,
                                'I_FOC':0, 
                                'I_FOC_MIN':0,
                                'I_FOC_MAX':1000,
                                'DAC_MIN':0,
                                'DAC_MAX':255,
                                #'I_BOMB':0.0,
                                #'U_ACC':0.0,
                                }
        self.config = ConfigParser()
        self.config.add_section("Settings")
        
    def __str__(self):
        return (f'in file:{self.config.read(self.path)}\n recorded parameters: {self.readConfig(list(self.start_valueparam.keys()))}')
    
    def createConfig(self, parameter:dict):
        """
        Create a config file
        """        
        for i in parameter:
            self.config.set("Settings", i, str(parameter[i]))
        with open(self.path, "w") as config_file:
            self.config.write(config_file)

    def readConfig(self, parameter=['I_FOC', 'I_FOC_MIN', 'I_FOC_MAX',
                                'DAC_MIN', 'DAC_MAX', 'start_I_WELD'])->dict:
        # returned param={parameter:value from conf-file} 
        self.config.read(self.path)
        return  {key:int(self.config.get('Settings',key)) for key in parameter}
    
    def read_ibomb(self, key='i_bomb'):
        return float(self.config.get('Settings', key))
        
    def calculateDAC(self, val:dict):#val = parameter
        self.DAC = val['DAC_MIN']+(
                (val['I_FOC']-val['I_FOC_MIN'])*
                (val['DAC_MAX']-val['DAC_MIN'])/
                (val['I_FOC_MAX']-val['I_FOC_MIN'])
                                    )
        print(f'dac = {int(self.DAC)}')
        return int(self.DAC)
 
        
if __name__ == '__main__':
    #path = 'settings_focus_t.conf'
    sf=SettFOC()
    
    print(sf.readConfig())
    print(sf.read_ibomb())
    '''
    #sf.createConfig(sf.start_valueparam)
    print(sf)  
    rcc = sf.readConfig(list(sf.start_valueparam.keys()))
    print(rcc)
    sf.calculateDAC(rcc)
    '''

        
        
        
