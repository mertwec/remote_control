#!/usr/bin/python3.7

import time

from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
#from threading import Thread

from configparser import ConfigParser

from modbus485_mm import ModbusConnect
from focusing_config import SettFOC
from i2c_bus import DACModule, ExtSwitcher
from in_out_buttons import PinIO
from mask_logging import *

sfoc = SettFOC('/home/pi/spreli/remote_control/settings_focus_t.conf')

class MainWindow(ModbusConnect, DACModule, ExtSwitcher, SettFOC):
    def __init__(self, master):
        #ModbusConnect.__init__(self)

        # const
        self.master = master                          # root       
        
        self.main_bg = '#9edcff'                      # задний фон поля
        self.master.configure(background = self.main_bg)
        
        self.font_labels = ("FreeSans", 13)           # шрифт подписей
        self.font_displ = ('DS-Digital', 33)          # шрифт на дисплейчике
        self.font_displ_set = ('DS-Digital', 26)
        self.width_displ = 8                          # ширина диспелйчика
        self.width_displ_set = 8
        self.displ_fg = 'lime'                        # цвет цифер на диспл
        self.time_total_update = 500                  # ,ms - частота запроса параметров системы
        
        self.initUI()                                 # виджеты
        
    def initUI(self):
        self.initUI_button()
        self.initUI_label_displ()
        self.initUI_inform_statisic()
        self.initUI_progress_bar()
        self.initUI_indicator()
        self.initUI_label_sett_displ()
        
    def initUI_label_displ(self):
        self.master.title("-=SPRELI PARAMETERS=-") # основное окно
        self.label_title = Label(self.master, text=('-SPRELI PARAMETERS- status read'),
                                font=self.font_labels,bg=self.main_bg)
            # labels and display
        self.label_text_U_ACC = Label(self.master,text=('UACC,kV'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_displ_U_ACC = Label(self.master,text=('----'),anchor=E, height=1,
                                font=self.font_displ, width=self.width_displ, justify=LEFT,
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

        self.label_text_U_LOCK = Label(self.master,text=('Bias Volt,V'),
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
    
    def initUI_label_sett_displ(self):
        self.label_text_set = Label(self.master,text=('-SETLINGS-'),
                                font=self.font_labels, bg=self.main_bg )
        self.label_text_setUACC = Label(self.master,text=('SET UACC,kV'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_setUACC = Label(self.master,text=('--'),anchor=E,
                                 font=self.font_displ_set,width=self.width_displ_set, 
                                 fg='black', bg=self.main_bg)
        
        self.label_text_setIBOMB = Label(self.master,text=('SET I_BOMB,mA'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_setIBOMB = Label(self.master,text=('--'),anchor=E,
                                 font=self.font_displ_set,width=self.width_displ_set,
                                 fg='black', bg=self.main_bg)
        
        self.label_text_setIWELD = Label(self.master,text=('SET I_WELD,mA'),
                                 font=self.font_labels, bg=self.main_bg )
        self.label_displ_setIWELD = Label(self.master,text=('--'),anchor=E,
                                 font=self.font_displ_set,width=self.width_displ_set, 
                                 fg='black', bg=self.main_bg)
        self.label_splitter = Label(self.master, text=('_'*76),anchor=N,
                                 font=self.font_labels, bg=self.main_bg)    
 
    def initUI_progress_bar(self):
            # progress bar
        st = ttk.Style()
        st.configure('Vertical.TProgressbar', troughcolor='white', 
                                    background='green',
                                    bordercolor='black',
                                    thickness=55,)
        
        self.label_text_pb = Label(self.master,text=('Welding Curent,mA'),
                                font=self.font_labels, bg=self.main_bg )
        
        self.progress_bar = ttk.Progressbar(self.master, maximum = 250,
                                orient="vertical", mode="determinate", length=230,
                                style='Vertical.TProgressbar')
    
    def initUI_inform_statisic(self):
            # inform statistic
        self.label_text_inform = Label(self.master,text=('Information'),
                                font=self.font_labels, bg=self.main_bg )
        self.text_inform = Label(self.master,
                                text= (f''' Torsion Plus '''),
                                font=('Inconsolata',14), bg='black',fg='white',
                                height= 3, width=63,
                                anchor=W)
    
    def initUI_indicator(self):              
            # indcators
        self.label_indicator_AW = Label(self.master, text=('Acceleration Voltage'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_AW = Canvas(bg=self.main_bg, width=70, height=50,)
        self.indicator_AW = self.fild_indicator_AW.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")

        self.label_indicator_CH = Label(self.master, text=('Cathode Heating'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_CH = Canvas(bg=self.main_bg, width=70, height=50)
        self.indicator_CH = self.fild_indicator_CH.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")

        self.label_indicator_WC = Label(self.master, text=('Welding Current'),
                            font=self.font_labels, bg=self.main_bg)
        self.fild_indicator_WC = Canvas(bg=self.main_bg, width=70, height=50)
        self.indicator_WC = self.fild_indicator_WC.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")
        
                #indicator  error
        self.label_error = Label(self.master, text=('Error'),
                            font=self.font_labels, bg=self.main_bg)

        # self.fild_indcator_error = Canvas(bg='white', width=120, height=50)
        # self.indicator_error = self.fild_indcator_error.create_text(20,10,text='Err: 00', font=self.font_labels)

        self.indicator_error =  Label(self.master, text=('ERR: 00'),height=1, width=8,
                            font='LED 18', bg='green')
    
    def initUI_button(self):
            #button
        self.button_quit = Button(self.master,text='quit',width=10,height=1,
                            command=lambda:self.disconnect(self.master))
        self.button_focus = Button(self.master,text='settings',width=10,height=1,
                            command=lambda:open_setFocWindows())

    # widget layout
    def mGrid(self):
        self.label_title.grid(row=0,column=0,columnspan=2,sticky=W,padx=25, pady=7)
        # button
        self.button_quit.grid(row=0,column=2, sticky=S)
        self.button_focus.grid(row=0, column=3, sticky=S)
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

        # display set labels
        #self.label_text_set.grid(row=7, column=0, sticky=W, padx=27, pady=3)
        
        self.label_text_setUACC.grid(row=7, column=0, sticky='SE', padx=7, pady=2)
        self.label_displ_setUACC.grid(row=8, column=0, sticky='SE', padx=7, pady=1)
        
        self.label_text_setIBOMB.grid(row=7, column=1, sticky='SE', padx=7, pady=2)
        self.label_displ_setIBOMB.grid(row=8, column=1, sticky='SE', padx=7, pady=1)
        
        self.label_text_setIWELD.grid(row=7, column=2, sticky='SE', padx=7, pady=2)
        self.label_displ_setIWELD.grid(row=8, column=2, sticky='SE', padx=7, pady=1)

        # progress bar
        self.label_text_pb.grid(row=1, column=3, sticky=S, padx=7, pady=2)
        self.progress_bar.grid(row=3,column=3, rowspan=6, pady=3)
        
        
           # inform statistic
        #self.label_text_inform.grid(row=7, column=0, sticky=W, padx=7, pady=3)
        #self.text_inform.grid(row=8, column=0 ,columnspan=3, sticky=W,
        #                    padx=7, pady=3)
        
        # indicator
        self.label_splitter.grid(row=9, column=0,columnspan=4,)
        self.label_error.grid(row=11, column=0, sticky=S, padx=7, pady=3)
        self.indicator_error.grid(row=10, column=0,padx=7, pady=3)

        self.label_indicator_AW.grid(row=11, column=1,sticky=S,padx=7,pady=3)
        self.fild_indicator_AW.grid(row=10,column=1,padx=7,pady=1)

        self.label_indicator_CH.grid(row=11, column=2,sticky=S, padx=7, pady=3)
        self.fild_indicator_CH.grid(row=10, column=2,padx=7, pady=1)

        self.label_indicator_WC.grid(row=11, column=3,sticky=S, padx=7, pady=3)
        self.fild_indicator_WC.grid(row=10, column=3, padx=7, pady=1)

    def show_message(self, mess):
        messagebox.showerror("error", mess,)# parent=Toplevel())
    
    def set_parameters(self, system_parameters):
        self.label_displ_setUACC.config(text=system_parameters['sets_UACC'])
        self.label_displ_setIWELD.config(text=system_parameters['sets_IWELD'])
        self.label_displ_setIBOMB.config(text=system_parameters['sets_IBOMB'])
        
        system_parameters = ModbusConnect().transform_parameters_to_str(system_parameters)
        
        self.label_title.config(text='-SPRELI PARAMETERS- status: connected')
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

    def set_indicator(self,stat_system):        
        if stat_system['stat_failure']==1:
            valueparam = ModbusConnect().read_one_register(register_= 1, functioncode_=4) # read code of error
            if valueparam == 0:
                self.indicator_error.config(text=f'ERR: {valueparam}',bg = 'green')
            else:
                self.indicator_error.config(text=f'ERR: {valueparam}',bg = 'red')
        else:
            self.indicator_error.config(text=f'ERR: 00',bg = 'green')
        
        if stat_system['stat_UACC']:
            self.fild_indicator_AW.create_oval(15,5,55,45,outline="black",        # 20,10,50,40,
                                width=1, fill="red")
        else:
            self.fild_indicator_AW.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")
        
        if stat_system['stat_IBOMB']:
            self.fild_indicator_CH.create_oval(15,5,55,45,outline="black",
                                width=1, fill="red")
        else:
            self.fild_indicator_CH.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")
        
        if stat_system['stat_IWELD']:
            self.fild_indicator_WC.create_oval(15,5,55,45,outline="black",
                                width=1, fill="red")
        else:
            self.fild_indicator_WC.create_oval(15,5,55,45,outline="black",
                                width=1, fill="white")
    
    def change_all_display(self, gpio, startiweld, system_parameters):
        # read current parameters
        system_parameters = ModbusConnect().read_all_parameters()

        if isinstance(system_parameters, dict):            
            status_system = ModbusConnect().parsing_status_system(system_parameters['status_system'])
            
            self.set_parameters(system_parameters) 
            self.set_indicator(status_system)
            
            #self.set_progressbar(startiweld)
            iweld=ExtSwitcher().value_iweld()
            if iweld!=startiweld:
                self.progress_bar['value'] = iweld
                startiweld = iweld
                ModbusConnect().write_one_register(
                                    register_=ModbusConnect().set_points['set_iweld'][0],
                                    value_=iweld,
                                    degree_=ModbusConnect().set_points['set_iweld'][1])
            else:
                pass

            gpio.set_outside_knob(status_system)                
            gpio.set_output_VD(status_system, 
                                value_ibomb=system_parameters['I_BOMB'],
                                setted_ibomb=system_parameters['sets_IBOMB']) #register
                               
        else:
            print('____________________________________________')
            #self.label_title.config(text='-SPRELI PARAMETERS- status: disconnect')
            #self.indicator_error['bg'] = 'red'
            self.indicator_error['text']='ERR: NC'
            self.master.update()
            print('error in change_all_parameter', system_parameters)
            error_log(f'error in change_all_display:{system_parameters}')
                   
        self.master.update_idletasks()
        self.master.after(self.time_total_update, 
                        self.change_all_display, 
                        gpio, startiweld, system_parameters)

    def disconnect(self, master):
        ModbusConnect().close_connect()
        print('disconnect')
        master.destroy()
        print('closed window')
        #time.sleep(0.5)

class SetFocWindow(MainWindow):   # SettFOC, ModbusConnect):
    def __init__(self, master):
       
        MainWindow.__init__(self, master)
        SettFOC.__init__(self)  #,path='spreli\remote_control\settings_focus.conf')
        #ModbusConnect.__init__(self)
        DACModule.__init__(self)
        
        self.I_FOC=self.readConfig()['I_FOC']
        self.I_BOMB_setting = ModbusConnect().read_one_register(123, functioncode_=3, degree_=1,)
        self.U_ACC_setting = ModbusConnect().read_one_register(117, functioncode_=3, degree_=2,)
        
        self.font_set_labels = ("FreeSans", 15) 
        self.font_displ_set = ('DS-Digital', 17)
        
        self.initUI_set_menu()        
        self.set_entry_values(self.readConfig())
        
    def initUI_set_menu(self):
        #main title
        self.master.title("-=SETTINGS=-") #  отображение в шапке окна основное окно
        
        # entry settings
        self.label_uacc_current = Label(self.master, text=('setpoint U ACC,kV:'),
                                font=self.font_set_labels,bg=self.main_bg,)
        self.entry_set_U_ACC = Entry(self.master, width=10, font=self.font_displ_set)                       
        
        self.label_ibomb_current = Label(self.master, text=('setpoint I BOMB,mA:'),      # {self.I_BOMB_setting}
                                font=self.font_set_labels,bg=self.main_bg,)
        self.entry_set_I_BOMB = Entry(self.master, width=10, font=self.font_displ_set)                        
        
        self.label_ifoc_current = Label(self.master, text=('setpoint I FOCUS,mA:'),     # {self.I_FOC}
                                font=self.font_set_labels,bg=self.main_bg,)
        self.entry_set_I_FOC = Entry(self.master, width=10, font=self.font_displ_set)
        
        self.label_start_iweld = Label(self.master, text=('start I WELDING,mA:'),
                                font=self.font_set_labels, bg=self.main_bg,)
        self.entry_start_iweld = Entry(self.master, width=10, font=self.font_displ_set)
        
        # entry parameters set ifoc 
        
        self.label_set_I_FOC_MIN = Label(self.master, text=(f'I FOC MIN,mA: '),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_I_FOC_MIN = Entry(self.master, width=10, font=self.font_displ_set)

        self.label_set_I_FOC_MAX = Label(self.master, text=(f'I FOC MAX,mA: '),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_I_FOC_MAX = Entry(self.master, width=10, font=self.font_displ_set)

        self.label_set_DAC_MIN = Label(self.master, text=(f'DAC MIN: '),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_DAC_MIN = Entry(self.master, width=10, font=self.font_displ_set)

        self.label_set_DAC_MAX = Label(self.master, text=(f'DAC_MAX: '),
                                font=self.font_labels,bg=self.main_bg)
        self.entry_set_DAC_MAX = Entry(self.master, width=10, font=self.font_displ_set)


        #buttons
        self.button_add_uacc = Button(self.master,text='+1kV',width=3,height=2,
                            command=lambda:self.change_ibomb_uacc('+',step=1))
        self.button_sub_uacc = Button(self.master,text='-1kV',width=3,height=2,
                            command=lambda:self.change_ibomb_uacc('-',step=1))
                            
        self.button_add_ibomb = Button(self.master,text='+2mA',width=3,height=2,
                            command=lambda:self.change_ibomb_uacc('+',step=2))
        self.button_sub_ibomb = Button(self.master,text='-2mA',width=3,height=2,
                            command=lambda:self.change_ibomb_uacc('-',step=2))
        
        self.button_add_ifoc = Button(self.master,text='+4mA',width=3,height=2,
                            command=lambda:self.change_i_focus('+')) 
        self.button_sub_ifoc = Button(self.master,text='-4mA',width=3,height=2,
                            command=lambda:self.change_i_focus('-'))

        self.button_write = Button(self.master,text='write',width=12,height=1,
                            command=self.write_from_entry_fields)
        self.button_quit = Button(self.master,text='quit',width=12,height=1,
                            command=lambda:self.disconnect(self.master))

    def mGrid_set_menu(self):

        #label entry
        
        self.label_uacc_current.grid(row=0, column=0, sticky=W, padx=15, pady=7)
        self.entry_set_U_ACC.grid(row=0, column=1, sticky=W, padx=15, pady=7)
        
        self.label_ibomb_current.grid(row=1, column=0, sticky=W, padx=15, pady=7)
        self.entry_set_I_BOMB.grid(row=1, column=1, sticky=W, padx=15, pady=7)
        
        self.label_ifoc_current.grid(row=2, column=0, sticky=W, padx=15, pady=7)
        self.entry_set_I_FOC.grid(row=2, column=1, sticky=W, padx=15, pady=7)
        
        self.label_start_iweld.grid(row=3, column=0, sticky=W, padx=15, pady=7)
        self.entry_start_iweld.grid(row=3,column=1,sticky=W, padx=15, pady=7)

        self.label_set_I_FOC_MIN.grid(row=4,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_I_FOC_MIN.grid(row=4,column=1,sticky=W,padx=15, pady=7)

        self.label_set_I_FOC_MAX.grid(row=5,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_I_FOC_MAX.grid(row=5,column=1,sticky=W,padx=15, pady=7)

        self.label_set_DAC_MIN.grid(row=6,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_DAC_MIN.grid(row=6,column=1,sticky=W,padx=15, pady=7)

        self.label_set_DAC_MAX.grid(row=7,column=0,sticky=W,padx=25, pady=7)
        self.entry_set_DAC_MAX.grid(row=7,column=1,sticky=W,padx=15, pady=7)

        # buttons
        self.button_add_uacc.grid(row=0,column=3,sticky=W,padx=7, pady=7)
        self.button_sub_uacc.grid(row=0,column=2,sticky=W,padx=7, pady=7)
        
        self.button_add_ibomb.grid(row=1,column=3,sticky=W,padx=7, pady=7)
        self.button_sub_ibomb.grid(row=1,column=2,sticky=W,padx=7, pady=7)
        
        self.button_add_ifoc.grid(row=2,column=3,sticky=W,padx=7, pady=7)
        self.button_sub_ifoc.grid(row=2,column=2,sticky=W,padx=7, pady=7)
        
        self.button_write.grid(row=6,column=2,columnspan=2,sticky=W,padx=7, pady=7)
        self.button_quit.grid(row=7,column=2,columnspan=2,sticky=W,padx=7, pady=7)

    def set_entry_values(self, param:dict): # param -- read from config file ,path='modules\settings_focus.conf')
        self.entry_set_U_ACC.insert(0, self.U_ACC_setting)
        self.entry_set_I_BOMB.insert(0, self.I_BOMB_setting)  
        self.entry_start_iweld.insert(0, param['start_I_WELD'])   
        self.entry_set_I_FOC.insert(0, param['I_FOC'])
        self.entry_set_I_FOC_MIN.insert(0, param['I_FOC_MIN'])
        self.entry_set_I_FOC_MAX.insert(0, param['I_FOC_MAX'])
        self.entry_set_DAC_MIN.insert(0, param['DAC_MIN'])
        self.entry_set_DAC_MAX.insert(0, param['DAC_MAX'])

    def read_entry_fields(self)-> dict:
        u_acc = self.entry_set_U_ACC.get()
        i_bomb = self.entry_set_I_BOMB.get()
        i_foc = self.entry_set_I_FOC.get()
        start_iweld = self.entry_start_iweld.get()
        i_foc_min = self.entry_set_I_FOC_MIN.get()
        i_foc_max = self.entry_set_I_FOC_MAX.get()
        dac_min = self.entry_set_DAC_MIN.get()
        dac_max = self.entry_set_DAC_MAX.get()
        return {'U_ACC':float(u_acc),
                'I_BOMB':float(i_bomb),
                'I_FOC':int(i_foc),
                'start_I_WELD':int(start_iweld),
                'I_FOC_MIN':int(i_foc_min),
                'I_FOC_MAX':int(i_foc_max),
                'DAC_MIN':int(dac_min),
                'DAC_MAX':int(dac_max),}

    def write_from_entry_fields(self):
        # read from entry -- dict
        r_dict = self.read_entry_fields()
        U = r_dict['U_ACC']
        IB = r_dict['I_BOMB']
        IF = (r_dict['I_FOC'], r_dict['I_FOC_MIN'], r_dict['I_FOC_MAX'])
        D = (r_dict['DAC_MIN'],r_dict['DAC_MAX'])

        if U>25 or U<0:
            self.show_message(f'uncorrect value {U}!')
            return None        
        if IB>120 or IB<0:
            self.show_message(f'uncorrect value {IB}!')
            return None        
        for i in IF:
            if i>1000 or i<0:
                self.show_message(f'uncorrect value {i}!')
                return None
        for d in D:
            if d>255 or d<0:
                self.show_message(f'uncorrect value dac {d}!')
                return None
                
        # запись в config file
        self.createConfig(r_dict)
        print('writing to conf')
                
        # calculate and and set DAC output
        dac_out = self.calculateDAC(r_dict)            
        self.write_byte_dac(byte=dac_out)

        self.I_FOC = self.read_entry_fields()['I_FOC']
        self.I_BOMB = self.read_entry_fields()['I_BOMB']
        self.U_ACC = self.read_entry_fields()['U_ACC']
        
        ModbusConnect().write_one_register(register_=ModbusConnect().set_points['set_ibomb'][0], 
                                    value_=self.I_BOMB, 
                                    degree_=ModbusConnect().set_points['set_ibomb'][1])
        ModbusConnect().write_one_register(register_=ModbusConnect().set_points['set_uacc'][0],
                                    value_=self.U_ACC, 
                                    degree_=ModbusConnect().set_points['set_uacc'][1])
    
    def change_ibomb_uacc(self, sign, step):
        '''
        1=uass, kV
        2=ibomb,mA
        '''
        r_dict = self.read_entry_fields()
        if step == 1: # uacc kV
            if sign == '+' and r_dict['U_ACC']<25:
                r_dict['U_ACC']+=1
                self.entry_set_U_ACC.delete(0,END)
                self.entry_set_U_ACC.insert(0,r_dict['U_ACC'])                
            elif sign =='-' and r_dict['U_ACC']>0:
                r_dict['U_ACC']-=1
                self.entry_set_U_ACC.delete(0,END)
                self.entry_set_U_ACC.insert(0,r_dict['U_ACC'])
                
        elif step ==2: # ibomb mA
            if sign == '+' and r_dict['I_BOMB']<120:
                r_dict['I_BOMB']+=2
                self.entry_set_I_BOMB.delete(0,END)
                self.entry_set_I_BOMB.insert(0,r_dict['I_BOMB'])                
            elif sign =='-' and r_dict['I_BOMB']>0:
                r_dict['I_BOMB']-=2
                self.entry_set_I_BOMB.delete(0,END)
                self.entry_set_I_BOMB.insert(0,r_dict['I_BOMB'])
                
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
        elif sign== '-':
            if r_dict['I_FOC'] > 0:
                r_dict['I_FOC']-= 4
                print(r_dict)
                self.entry_set_I_FOC.delete(0,END)
                self.entry_set_I_FOC.insert(0,r_dict['I_FOC'])
                self.createConfig(r_dict)                        
                self.write_byte_dac(self.calculateDAC(r_dict))
               
               
def open_setFocWindows():
    '''open windows setting focusing
    '''
    rootf = Tk()
    rootf.geometry("550x410+25+25")   # поместить окно в точку с координатам 25,25 и установить размер в 810x370 
    appl_foc = SetFocWindow(rootf)  # all start setting in __init__ 
    appl_foc.mGrid_set_menu()
    
    rootf.mainloop()
    
def open_mainWindow():
    root = Tk()
    root.geometry("800x500+25+25")      # поместить окно в точку с координатам 100,100 и установить размер в 810x450
    #root.attributes('-fullscreen', True)  #на весь экран
    appl = MainWindow(root)
    appl.mGrid()
    
    root.mainloop()
   


if __name__ == '__main__':

    connect_mb = ModbusConnect()
    
    #root = Tk()
    #root.geometry("800x500+25+25")      
    #root.attributes('-fullscreen', True)  #на весь экран
    #root.config(cursor='none')
    
    #appl = MainWindow(root)
    #appl.mGrid()

    #root.mainloop()
    
    
    open_mainWindow()
    #open_setFocWindows()
    


