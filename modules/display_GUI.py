#!/usr/bin/env python3

import time

from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox

from configparser import ConfigParser

from modbus485_mm import ModbusConnect
from focusing_config import SettFOC
from i2c_bus import DACModule, ExtSwitcher

sfoc = SettFOC()

class MainWindow(SettFOC, ModbusConnect,DACModule, ExtSwitcher):
    def __init__(self,master):
        ModbusConnect.__init__(self)
        
        # const
        self.master=master                          # root
        self.main_bg='#9edcff'                      # задний фон поля
        self.font_labels=("FreeSans", 13)           # шрифт подписей
        self.font_displ=('DS-Digital', 33)          # шрифт на дисплейчике
        self.width_displ=8                          # ширина диспелйчика
        self.displ_fg='lime'                        # цвет цифер на диспл
        
        self.initUI()                               # виджеты
        
    def initUI(self):
        self.initUI_button()
        self.initUI_label_displ()
        self.initUI_inform_statisic()
        self.initUI_progress_bar()
        self.initUI_indicator()
        
    def initUI_label_displ(self):
        self.master.title("-=SPRELI PARAMETERS=-") # основное окно
        self.label_title = Label(self.master, text=('SPRELI PARAMETERS'),
                                font=self.font_labels,bg=self.main_bg)
            # labels and display
        self.label_text_U_ACC = Label(self.master,text=('Acceleration Volt,kV'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_displ_U_ACC = Label(self.master,text=('----'),anchor=E, height=1,
                                font=self.font_displ,width=self.width_displ, justify=LEFT,
                                fg=self.displ_fg, bg='black',)

        self.label_text_U_POW = Label(self.master,text=('Power Volt,V'),
                                font=self.font_labels, bg=self.main_bg)
        self.label_displ_U_POW = Label(self.master,text=('----'), anchor=E,
                                 font=self.font_displ,width=self.width_displ, justify=LEFT,
                                 fg=self.displ_fg, bg='black')

        ##############  ?????
        self.label_text_I_FOC = Label(self.master,text=('Focusing Cur,mA'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_displ_I_FOC = Label(self.master,text=('----'), anchor=E,
                                 font=self.font_displ,width=self.width_displ, justify=LEFT,
                                 fg=self.displ_fg, bg='black')
        ##############

        self.label_text_U_LOCK = Label(self.master,text=('Locking Volt,V'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_U_LOCK = Label(self.master,text=('----'),anchor=E,
                                 font=self.font_displ,width=self.width_displ, justify=LEFT,
                                 fg=self.displ_fg, bg='black')

        self.label_text_U_BOMB = Label(self.master,text=('Bombardment Volt,V'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_U_BOMB = Label(self.master,text=('----'),anchor=E,
                                 font=self.font_displ,width=self.width_displ, justify=LEFT,
                                 fg=self.displ_fg, bg='black')

        self.label_text_I_BOMB = Label(self.master, text=('Bombardment Cur,mA'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_I_BOMB = Label(self.master, text=('----'),anchor=E,
                                 font=self.font_displ, width=self.width_displ, justify=LEFT,
                                 fg=self.displ_fg, bg='black')

        self.label_text_I_FIL = Label(self.master,text=('Filament Cur,mA'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_displ_I_FIL = Label(self.master,text=('----'),anchor=E,
                                 font=self.font_displ, width=self.width_displ, fg=self.displ_fg,
                                 bg='black')

        self.label_text_U_WEHNELT = Label(self.master,text=('Wehnelt Volt,V'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_U_WEHNELT = Label(self.master,text=('----'),anchor=E,
                                 font=self.font_displ,width=self.width_displ, fg=self.displ_fg,
                                 bg='black')
        self.label_text_AUX = Label(self.master,text=('AUX,V'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_displ_AUX = Label(self.master,text=('----'),anchor=E,
                                 font=self.font_displ,width=self.width_displ, fg=self.displ_fg,
                                 bg='black')
        self.label_text_TEMP = Label(self.master,text=('Temp, C'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_TEMP = Label(self.master,text=('--'),anchor=E,
                                 font=self.font_displ,width=self.width_displ, fg=self.displ_fg,
                                 bg='black')

        self.label_displ_I_WELD = Label(self.master,text=('----'),anchor=E,
                                font=self.font_displ,width=self.width_displ, fg=self.displ_fg,
                                 bg='black')
    
    def initUI_progress_bar(self):
            # progress bar
        self.label_text_pb = Label(self.master,text=('Welding Curent,mA'),
                                font=self.font_labels, bg=self.main_bg )

        self.progress_bar = ttk.Progressbar(self.master, maximum = 250,
                                orient="vertical", mode="determinate", length=255, )
    
    def initUI_inform_statisic(self):
            # inform statistic
        self.label_text_inform = Label(self.master,text=('Information'),
                                font=self.font_labels, bg=self.main_bg )
        self.text_inform = Label(self.master,
                                text= (f''' Torsion Plus '''),
                                font=('Inconsolata',14), bg='black',fg='white',
                                height= 3, width=63,
                                anchor=W)
    
    def  initUI_indicator(self):
              
            # indcators
        self.label_indicator_AW = Label(self.master, text=('Aceleration Voltage'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_AW = Canvas(bg=self.main_bg, width=70, height=50)
        self.indicator_AW = self.fild_indicator_AW.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")

        self.label_indicator_CH = Label(self.master, text=('Cathode Heating'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_CH = Canvas(bg=self.main_bg, width=70, height=50)
        self.indicator_CH = self.fild_indicator_CH.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")

        self.label_indicator_WC = Label(self.master, text=('Welding Curent'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_WC = Canvas(bg=self.main_bg, width=70, height=50)
        self.indicator_WC = self.fild_indicator_WC.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")
        
                #indicator  error
        self.label_error = Label(self.master, text=('Error'),
                            font=self.font_labels, bg=self.main_bg)

        # self.fild_indcator_error = Canvas(bg='white', width=120, height=50)
        # self.indicator_error = self.fild_indcator_error.create_text(20,10,text='Err: 00', font=self.font_labels)

        self.indicator_error =  Label(self.master, text=('ERR: 00'),height=1, width=7,
                            font='LED 18', bg='green')
    
    def initUI_button(self):
            #button
        self.button_quit = Button(self.master,text='quit',width=10,height=1,
                            command=lambda:self.disconnect(self.master))
        self.button_focus = Button(self.master,text='set focus',width=10,height=1,
                            command=lambda:open_setFocWindows())

    # widget layout
    def mGrid(self):
        self.label_title.grid(row=0,column=0,columnspan=2,sticky=W,padx=25, pady=7)
        # button
        self.button_quit.grid(row=0,column=3, sticky=S)
        self.button_focus.grid(row=0, column=2, sticky=S)
        # display
        self.label_text_U_ACC.grid(row=1, column=0,sticky=W, padx=7, pady=2)
        self.label_displ_U_ACC.grid(row=2, column=0,sticky='NW',padx=7, pady=5)

        self.label_text_U_POW.grid(row=3, column=0,sticky=W, padx=7, pady=2)
        self.label_displ_U_POW.grid(row=4, column=0,sticky='NW',padx=7, pady=4)

        self.label_text_U_LOCK.grid(row=5, column=0,sticky=W, padx=7, pady=2)
        self.label_displ_U_LOCK.grid(row=6, column=0,sticky='NW',padx=7, pady=4)

        self.label_text_U_BOMB.grid(row=1, column=1,sticky=W, padx=7, pady=2)
        self.label_displ_U_BOMB.grid(row=2, column=1,sticky='NW',padx=7, pady=4)

        self.label_text_I_BOMB.grid(row=3, column=1,sticky=W, padx=7, pady=2)
        self.label_displ_I_BOMB.grid(row=4, column=1,sticky='NW',padx=7, pady=4)

        self.label_text_I_FIL.grid(row=5, column=1, sticky=W, padx=7, pady=2)
        self.label_displ_I_FIL.grid(row=6, column=1, sticky='NW',padx=7, pady=4)

        self.label_text_U_WEHNELT.grid(row=1, column=2, sticky=W, padx=7, pady=2)
        self.label_displ_U_WEHNELT.grid(row=2, column=2, sticky='NW',padx=7, pady=4)

        self.label_text_AUX.grid(row=3, column=2, sticky=W, padx=7, pady=2)
        self.label_displ_AUX.grid(row=4, column=2,sticky='NW',padx=7, pady=4)

        self.label_text_TEMP.grid(row=5, column=2, sticky=W, padx=7, pady=2)
        self.label_displ_TEMP.grid(row=6, column=2, sticky='NW', padx=7, pady=4)

        self.label_displ_I_WELD.grid(row=2, column=3, sticky='NW', padx=7, pady=4)

        # progress bar
        self.label_text_pb.grid(row=1, column=3,sticky=S, padx=7, pady=2)
        self.progress_bar.grid(row=4,column=3,rowspan=5)

        # inform statistic
        self.label_text_inform.grid(row=7, column=0, sticky=W, padx=7, pady=3)
        self.text_inform.grid(row=8, column=0 ,columnspan=3, sticky=W,
                            padx=7, pady=3)
        # indicator
        self.label_error.grid(row=9, column=0, sticky=N, padx=7, pady=3)
        self.indicator_error.grid(row=10, column=0, sticky=N, padx=7, pady=3)

        self.label_indicator_AW.grid(row=9, column=1,sticky=N, padx=7, pady=3)
        self.fild_indicator_AW.grid(row=10, column=1,padx=7, pady=1)

        self.label_indicator_CH.grid(row=9, column=2,sticky=N, padx=7, pady=3)
        self.fild_indicator_CH.grid(row=10, column=2,padx=7, pady=1)

        self.label_indicator_WC.grid(row=9, column=3,sticky=N, padx=7, pady=3)
        self.fild_indicator_WC.grid(row=10, column=3, padx=7, pady=1)


    #def change_label(self, label, valueparam,):
     #   '''help function'''
     #   label.config(text=str(valueparam))	
     #   label.after(300, self.change_label,label,valueparam)
    
    def update_system_value(self, label):
        global system_parameters
        global status_system
        
        system_parameters = self.read_all_parameters()
        status_system = self.read_status_system()
        
        #print(stat_system)
        label.after(300, self.update_system_value, label)
        
    def change_parameters(self, system_parameters):
        
        system_parameters = self.read_all_parameters()
        
        self.label_displ_U_ACC.config(text=system_parameters['U_ACC'])        
        self.label_displ_U_POW.config(text=system_parameters['U_POWER'])
        self.label_displ_U_LOCK.config(text=system_parameters['U_LOCK'])
        self.label_displ_U_BOMB.config(text=system_parameters['U_BOMB'])
        self.label_displ_I_BOMB.config(text=system_parameters['I_BOMB'])
        self.label_displ_I_FIL.config(text=system_parameters['I_FIL'])
        self.label_displ_U_WEHNELT.config(text=system_parameters['U_WEHNELT'])
        self.label_displ_AUX.config(text=system_parameters['AUX'])
        self.label_displ_TEMP.config(text=system_parameters['TEMP'])
        self.label_displ_I_WELD.config(text=system_parameters['I_WELD'])
        
        self.text_inform['text']=f'''TorsionPlus: I_WELD = {system_parameters["sets_IWELD"]}
               I_BOMB = {system_parameters["sets_IBOMB"]}
             U_ACC = {system_parameters["sets_UACC"]}'''
             
        self.label_title.after(300, self.change_parameters, system_parameters)

            
    def change_indicator(self, stat_system):
        '''
            'stat_UACC':int(mfullbss[10]), #1 reg
            'stat_IBOMB':int(mfullbss[11]), #3 reg
            'stat_IWELD':int(mfullbss[12]), #2 reg
                
            'stat_failure':int(mfullbss[13]),
            'stat_run':int(mfullbss[8])}'''
        stat_system = self.read_status_system()
        #print(stat_system)
        if stat_system['stat_failure']==1:
            valueparam = self.read_one_register(register_= 1, functioncode_=4) # read code of error
            self.indicator_error.config(text=f'ERR: {valueparam}',bg = 'red')
        else:
            self.indicator_error.config(text=f'ERR: 00',bg = 'green')
        
        if stat_system['stat_UACC']:
            self.fild_indicator_AW.create_oval(20,10,50,40,outline="black",
                                width=1, fill="red")
        else:
            self.fild_indicator_AW.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")
        
        if stat_system['stat_IBOMB']:
            self.fild_indicator_CH.create_oval(20,10,50,40,outline="black",
                                width=1, fill="red")
        else:
            self.fild_indicator_CH.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")
        
        if stat_system['stat_IWELD']:
            self.fild_indicator_WC.create_oval(20,10,50,40,outline="black",
                                width=1, fill="red")
        else:
            self.fild_indicator_WC.create_oval(20,10,50,40,outline="black",
                                width=1, fill="white")
        
        self.indicator_error.after(400, self.change_indicator, stat_system)

    def change_progressbar(self, prbar, startiweld):        # ekz_sw = ExtSwitcher()
        iweld = ExtSwitcher().value_iweld()
        if iweld!=startiweld:  
            prbar['value'] = iweld
            startiweld = iweld
            ModbusConnect().write_one_register(register_=ModbusConnect().register_set_i_weld[0],
                                    value_=iweld,
                                    degree_=ModbusConnect().register_set_i_weld[1])
            print(startiweld)
        prbar.after(500, self.change_progressbar, prbar, startiweld)
    
    def disconnect(self, master):
        print('disconnect')
        master.destroy()
        time.sleep(0.5)

class SetFocWindow(MainWindow):   # SettFOC, ModbusConnect):
    def __init__(self, master):
       
        MainWindow.__init__(self, master)
        SettFOC.__init__(self)  #,path='modules\settings_focus.conf')
        ModbusConnect.__init__(self)
        DACModule.__init__(self)
        
        self.I_FOC=self.readConfig(['I_FOC'])['I_FOC']
        self.I_BOMB_setting = self.read_one_register(123, functioncode_=3, degree_=1, signed_=False)
        
        self.initUI_foc()        
        self.set_entry_values(self.readConfig())
  
        

    def initUI_foc(self):
        #main title
        self.master.title("-=SETTINGS FOCUSING=-") # основное окно
        self.label_title = Label(self.master, text=('- Focus Source Control Menu -'),
                                font=self.font_labels,bg=self.main_bg)

        # labels
        self.label_ibomb_current = Label(self.master, text=(f'current setpoint I BOMB: {self.I_BOMB_setting}'),
                                font=self.font_labels,bg=self.main_bg)
        self.label_i_foc_current = Label(self.master, text=(f'current setpoint I FOCUS: {self.I_FOC}'),font=self.font_labels,bg=self.main_bg)

        # entry
        self.label_set_I_FOC = Label(self.master, text=(f'I FOCUS:'),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_I_FOC = Entry(self.master, width=10)

        self.label_set_I_FOC_MIN = Label(self.master, text=(f'I FOC MIN:'),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_I_FOC_MIN = Entry(self.master, width=10)

        self.label_set_I_FOC_MAX = Label(self.master, text=(f'I FOC MAX:'),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_I_FOC_MAX = Entry(self.master, width=10)

        self.label_set_DAC_MIN = Label(self.master, text=(f'DAC MIN:'),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_DAC_MIN = Entry(self.master, width=10)

        self.label_set_DAC_MAX = Label(self.master, text=(f'DAC_MAX:'),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_DAC_MAX = Entry(self.master, width=10)


        #buttons
        self.button_add = Button(self.master,text='+4mA',width=2,height=1,
                            command=lambda:self.change_i_focus('+')) 
        self.button_sub = Button(self.master,text='-4mA',width=2,height=1,
                            command=lambda:self.change_i_focus('-'))

        self.button_write = Button(self.master,text='write',width=10,height=1,
                            command=self.write_from_entry_fields)


        self.button_quit = Button(self.master,text='quit',width=10,height=1,
                            command=lambda:self.disconnect(self.master))

    def mGrid_foc(self):

        #label entry
        self.label_title.grid(row=0,column=0,columnspan=2,sticky=W,padx=25, pady=7)

        self.label_ibomb_current.grid(row=1, column=0, columnspan=2, sticky=W, padx=25, pady=7)
        self.label_i_foc_current.grid(row=2, column=0, columnspan=2, sticky=W, padx=25, pady=7)
        self.label_set_I_FOC.grid(row=3, column=0, sticky=W, padx=25, pady=7)
        self.entry_set_I_FOC.grid(row=3, column=1, sticky=W, padx=25, pady=7)

        self.label_set_I_FOC_MIN.grid(row=4,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_I_FOC_MIN.grid(row=4,column=1,sticky=W,padx=25, pady=7)

        self.label_set_I_FOC_MAX.grid(row=5,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_I_FOC_MAX.grid(row=5,column=1,sticky=W,padx=25, pady=7)

        self.label_set_DAC_MIN.grid(row=6,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_DAC_MIN.grid(row=6,column=1,sticky=W,padx=25, pady=7)

        self.label_set_DAC_MAX.grid(row=7,column=0,columnspan=2,sticky=W,padx=25, pady=7)
        self.entry_set_DAC_MAX.grid(row=7,column=1,columnspan=2,sticky=W,padx=25, pady=7)

        # buttons
        self.button_add.grid(row=2,column=3,sticky=W,padx=8, pady=7)
        self.button_sub.grid(row=2,column=2,sticky=W,padx=15, pady=7)

        self.button_write.grid(row=6,column=2,columnspan=2,sticky=W,padx=15, pady=7)
        self.button_quit.grid(row=7,column=2,columnspan=2,sticky=W,padx=15, pady=7)

    def set_entry_values(self,param:dict):
        self.entry_set_I_FOC.insert(0, param['I_FOC'])
        self.entry_set_I_FOC_MIN.insert(0, param['I_FOC_MIN'])
        self.entry_set_I_FOC_MAX.insert(0, param['I_FOC_MAX'])
        self.entry_set_DAC_MIN.insert(0, param['DAC_MIN'])
        self.entry_set_DAC_MAX.insert(0, param['DAC_MAX'])

    def read_entry_fields(self)-> dict:
        i_foc = self.entry_set_I_FOC.get()
        i_foc_min = self.entry_set_I_FOC_MIN.get()
        i_foc_max = self.entry_set_I_FOC_MAX.get()
        dac_min = self.entry_set_DAC_MIN.get()
        dac_max = self.entry_set_DAC_MAX.get()
        return {'I_FOC':int(i_foc),
                'I_FOC_MIN':int(i_foc_min),
                'I_FOC_MAX':int(i_foc_max),
                'DAC_MIN':int(dac_min),
                'DAC_MAX':int(dac_max),}
    
    def show_message(self, mess):
        messagebox.showwarning("error", mess)#, parent=Toplevel())

    
    def write_from_entry_fields(self):
        # read from entry 
        r_dict = self.read_entry_fields()
        I = (r_dict['I_FOC'], r_dict['I_FOC_MIN'], r_dict['I_FOC_MAX'])
        D = (r_dict['DAC_MIN'],r_dict['DAC_MAX'])
        
        for i in I:
            if i>1000 or i<0:
                self.show_message(f'uncorrect value {i}!')
                return None
        for d in D:
            if d>255 or d<0:
                self.show_message(f'uncorrect value dac{d}!')
                return None
        # запись в config file
        self.createConfig(r_dict)
        
        # calculate and and set DAC output
        dac_out = self.calculateDAC(r_dict)            
        self.write_byte_dac(byte=dac_out)

        
        self.I_FOC=self.read_entry_fields()['I_FOC']
        self.label_i_foc_current.config(text=f'current setpoint I FOCUS: {self.I_FOC}')
        print('writing to conf')


    def change_i_focus(self, sign):
        '''
        1) add to i_focos 4mA
        2) write i_foc to config
        3.1)calcDAC set in i2c-dac
        3.2) max 1000mA
        '''
        r_dict = self.read_entry_fields()
        if sign == '+':
            if r_dict['I_FOC'] < 1000:
                r_dict['I_FOC']+= 4
                print(r_dict)
                self.entry_set_I_FOC.delete(0,END)
                self.entry_set_I_FOC.insert(0,r_dict['I_FOC'])
                self.createConfig(r_dict)                        
                self.write_byte_dac(self.calculateDAC(r_dict))
                self.label_i_foc_current.config(text=f'current setpoint I FOCUS: {r_dict["I_FOC"]}')
        elif sign== '-':
            if r_dict['I_FOC'] > 0:
                r_dict['I_FOC']-= 4
                print(r_dict)
                self.entry_set_I_FOC.delete(0,END)
                self.entry_set_I_FOC.insert(0,r_dict['I_FOC'])
                self.createConfig(r_dict)                        
                self.write_byte_dac(self.calculateDAC(r_dict))
                self.label_i_foc_current.config(text=f'current setpoint I FOCUS: {r_dict["I_FOC"]}')
        

    def sub_i_focus():
        '''
        1) sub to i_focos 4mA
        2) write i_foc to config
        3) min 0mA
        '''
        pass

def open_setFocWindows():
    '''open windows setting focusing
    '''
    rootf = Tk()
    rootf.geometry("475x350+75+75")    
    appl_foc = SetFocWindow(rootf)  # all start setting in __init__        
    rootf.configure(background = appl_foc.main_bg)    
    appl_foc.mGrid_foc()



if __name__ == '__main__':

    sfoc = SettFOC() #'/home/pi/Desktop/pult_spreli_program/modules/settings_focus.conf')
    connect_mb = ModbusConnect()
    
    
    
    root = Tk()
    root.geometry("940x500+50+50")      # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    # root.attributes('-fullscreen', True)  #на весь экран
    appl = MainWindow(root)
    root.configure(background = appl.main_bg)
    appl.mGrid()
    root.mainloop()


