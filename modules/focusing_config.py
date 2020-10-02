
from configparser import ConfigParser


class SettFOC(ConfigParser):
    #path = 'settings_focus.conf'
    def __init__(self,path = '/home/pi/Desktop/pult_spreli_program/remote_control_SPRELI/settings_focus.conf'):
        self.path = path
        self.start_valueparam = {'I_FOC':0, 
                                'I_FOC_MIN':0,
                                'I_FOC_MAX':1000,
                                'DAC_MIN':0,
                                'DAC_MAX':255}
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

    def readConfig(self, param=['I_FOC', 'I_FOC_MIN','I_FOC_MAX','DAC_MIN','DAC_MAX'])->dict:
        # returned param={parameter:value from conf-file} 

        self.config.read(self.path)
        return  {key:int(self.config.get('Settings',key)) for key in param}
        
       
    def calculateDAC(self, parameter:dict):
        self.DAC = parameter['I_FOC']*(parameter['DAC_MAX']-parameter['DAC_MIN'])/(parameter['I_FOC_MAX']-parameter['I_FOC_MIN'])
        print(self.DAC)
        
        #self.config.set("Settings", 'DAC_', str(self.DAC))
        #with open(self.path, "w") as config_file:
        #    self.config.write(config_file)
        
        return int(self.DAC)
 
        
if __name__ == '__main__':
    path = 'settings_focus_temp.conf'
    sf=SettFOC(path)
    sf.createConfig(sf.start_valueparam)
    print(sf)  
    rcc = sf.readConfig(list(sf.start_valueparam.keys()))
    print(rcc)
    sf.calculateDAC(rcc)
         
        
        
        
