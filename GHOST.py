
# coding: utf-8

# In[1]:

import numpy as np

#Fancy printing with pprint
from pprint import pprint

#PyJAPC for getting & setting FESA parameters
import pyjapc
 
# Time module for sleeping
from time import sleep, strftime

#PyLogBook to push events to the eLogbook
import pylogbook

#Logging for keeping up with the flow...
import logging

#Sys needed for logging in Jupyter with StreamHandler..It can be removed for non-Jupyter platform
from sys import stderr


# In[18]:

class HTadjust(object):
    
    def __init__(self,FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='HTajust',simulate_SET=True,INCA_ACCEL='LEIR',sourceHT_selector=None,BCT15_selector='LEI.USER.EARLY',which_ebook='TESTS',no_elog_write=False,log_me=True,log_level='DEBUG'):
        
        self.FESA_GHOST_Device=FESA_GHOST_Device
        self.FESA_GHOST_Property=FESA_GHOST_Property 
        self.simulate_SET=simulate_SET
        self.sourceHT_selector=sourceHT_selector
        self.BCT15_selector=BCT15_selector
        self.INCA_ACCEL=INCA_ACCEL
        self.which_ebook=which_ebook
        self.log_level=log_level
        self.no_elog_write=no_elog_write
        self.log_me=log_me
        self.__name__='HTadjust'
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        self.__version__='v.1.0.0'
        
    
    def initiate_JAPC(self):
        global japc
        japc=pyjapc.PyJapc(selector=self.sourceHT_selector,
                           incaAcceleratorName=self.INCA_ACCEL,noSet=self.simulate_SET,logLevel=50) 

    def initiate_elogbook(self):
        global elog
        elog=pylogbook.eLogbook(self.which_ebook)
    
    def initiate_logger(self):
        global logger
        # Create logger
        logger = logging.getLogger(self.__name__)
        lvl=logging.getLevelName(self.log_level)
        logger.setLevel(lvl)
         # Create STDERR handler
        handler_stream = logging.StreamHandler(stderr)
        handler_logfile=logging.FileHandler('LogFiles/HT_adjust.log',mode='w')

        # ch.setLevel(logging.DEBUG)

        # Create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        handler_logfile.setFormatter(formatter)

        # Set STDERR handler as the only handler 
        logger.handlers = [handler_stream,handler_logfile] 
     
    
    def logger_or_printer(self,msg,flag):
        if self.log_me:
            lvl=self.log_level
            
            if (lvl=='INFO') and (flag=='info'):
                logger.info(msg)
            elif (lvl=='DEBUG') and (flag=='debug'):
                logger.debug(msg)
            elif (lvl=='WARNING') and (flag=='warning'):
                logger.warning(msg)
            elif (lvl=='ERROR') and (flag=='error'):
                logger.error(msg)
            elif (lvl=='CRITICAL') and (flag=='critical'):
                logger.critical(msg)
               
        else:
            
            print('No logger mode: '+msg)

                
    def get_HTadjust(self,HTadjust_input):
        
        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        valid_params=japc.getParamInfo(my_field)
        param_full_name='HTadjust_'+HTadjust_input

        if self.contains_word(valid_params,param_full_name):
            try:

                HTadjust_param=japc.getParam(my_field+'#'+param_full_name)
                return HTadjust_param

            except:
                msg='There seems to be a problem communicating with the FEC. No GET action is possible. Aborting.\n'
                self.logger_or_printer(msg,flag='error')
                raise ValueError('msg')

        else:
            msg='Wrong name of the parameter.\nPlease check again the available parameter space with japc.getParamInfo().\n'
            self.logger_or_printer(msg,flag='error')
            raise NameError(msg)    
            
    def set_HTadjust(self,HTadjust_input,val_to_set):

        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        valid_params=japc.getParamInfo(my_field)
        param_full_name='HTadjust_'+HTadjust_input

        if self.contains_word(valid_params,param_full_name):

            try:

                map_params=japc.getParam(my_field)
                map_params[param_full_name]=val_to_set
                japc.setParam(my_field,map_params)
                msg='Setting %s#%s parameter to value %s.\n'%(my_field,param_full_name,val_to_set)
                self.logger_or_printer(msg,flag='info')

            except:
        
                msg='There seems to be a problem communicating with the FEC. Aborting SET action.\n'
                self.logger_or_printer(msg,flag='error')
                raise ValueError(msg)

        else:
            
            msg='Wrong name of the parameter.\nPlease check again the available parameter space with japc.getParamInfo().\n'
            self.logger_or_printer(msg,flag='error')
            raise NameError(msg)    

    
    
           
    def get_my_JAPC_parameter(self,device,field,parameter,my_selector=None,no_shots=10,offset=1):
        
        param=[]

        def myCallback(parameterName, newValue):
                
            msg="New value for {0} is: {1}\n".format(parameterName, newValue)
            self.logger_or_printer(msg,flag='info')
            param.append(newValue)

        japc.setSelector(my_selector)
        
        msg=parameter+' measurement: Assigning selector-> '+str(my_selector)+'.\n'
        self.logger_or_printer(msg,flag='info')
        my_constructor=device+'/'+field+'#'+parameter
        japc.subscribeParam( my_constructor, myCallback )
        japc.startSubscriptions()

        while len(param)<no_shots+offset:
            pass
        else:
            japc.stopSubscriptions()
            japc.clearSubscriptions()

        param=param[offset:]

        japc.stopSubscriptions()##
                                ## Without these 2 it seems that the subscriptions persist...    
        japc.clearSubscriptions()##
        return {'Values':param,'Mean':np.mean(param),'Sigma':np.std(param)}
    
    

    def set_my_JAPC_parameter(self,device,field,parameter,val_to_set,my_selector=None,lim=200000):
        

        my_constructor=device+'/'+field
        japc.setSelector(my_selector)
        dic_FESA=japc.getParam(my_constructor)
        temp={}
        for key,item in dic_FESA.items():
            if not (('_min' in key ) or ('_max' in key)):
                temp[key]=item
        
        dic_FESA=temp
        
        if float(val_to_set)<float(lim):
              
            dic_FESA[parameter]=float(val_to_set)
            
            try:
            
                japc.setParam(my_constructor,dic_FESA)
                msg='Setting '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.\n'
                self.logger_or_printer(msg,flag='info')
            except:
                msg='Unable to set '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)
                self.logger_or_printer(msg,flag='error')
                raise ValueError('Unable to set '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set))
        
        else:
            msg='Given value above safe operating threshold(Limit->'+str(lim)+') . Aborting operation and keeping the same value of parameter '+my_constructor+'#'+parameter+'.\n'
            self.logger_or_printer(msg,flag='warning')
            
            
                

                    
         
        
    
    def write_L3_logbook(self,flag_unstable):

        if not self.no_elog_write: 
            if flag_unstable:
                my_message='After '+str(HTadjust_interval)+' minutes, ITF.BCT15 was measured but too unstable for adjustment.\n [GHOST:HTadjust]'
            else:
                my_message='After '+str(HTadjust_interval)+' minutes, ITF.BCT15 was measured, change of HT from '+str(HT_start)+' to '+str(HT_new)+'. \nChanged ITF.BCT from '+str(linac_current_start['Mean'])+' to '+str(BCT15_new)+'\n[GHOST:HTadjust]'

            elog.create_event(my_message)
            
            msg='New entry in eLogBook: '+my_message+'.\n'
            
            self.logger_or_printer(msg,flag='info')

        else:
            msg='Operation of logging to elogbook suppresed by the user.\n'
            self.logger_or_printer(msg, flag='info')

        
    def wait_HTadjust_interval(self,time_knob=0):
    
        global HTadjust_interval, HTadjust_kill

        HTadjust_interval=self.get_HTadjust('intervall') # This is in minutes !
        
        if not time_knob:
            msg='Waiting for '+str(HTadjust_interval)+' minutes.\n'
            self.logger_or_printer(msg,flag='info')
            sleep(HTadjust_interval*60)# Input in seconds     
        else:
            msg='User defined sleep time. Waiting for '+str(time_knob)+' seconds.\n'
            self.logger_or_printer(msg,flag='info')
            sleep(time_knob)# Input in seconds
        
        msg='Restarting HTadjust Module. Acquiring new value for the HTadjust_kill flag.\n'
        self.logger_or_printer(msg,flag='info')

        HTadjust_kill=self.get_HTadjust('kill')
    
    
    
    def HT_Linac_Current_Decider(self,linac_current,new_value_SRCVOLT,dummy_wait_time,shot_number=10,cycle_offset=1):
        
        global second_round
        
        while linac_current['Sigma']>0.1*linac_current['Mean']:
            msg='Unstable conditions of linac current measurement. Checking if this is the first round.\n'
            self.logger_or_printer(msg,flag='info')
            
            if second_round:
                msg='This is the second round. The current measurement from BCT15 is too unstable. Writing to eLogbook.\n'
                self.logger_or_printer(msg,flag='info')
                self.write_L3_logbook(flag_unstable=True)

                if not HTadjust_test:
                    msg='This is not a test! Forwarding SET request and setting the HT voltage to the initial value.\n'
                    self.logger_or_printer(msg,flag='info')
                    self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='sourceHT',val_to_set=HT_start,my_selector=None) 
                else:
                    msg='This is a test. No SET operation on-going.\n'
                    self.logger_or_printer(msg,flag='info')

                msg='End of module. Waiting for new time interval for HT adjust.\n'
                self.logger_or_printer(msg,flag='info')                
                self.wait_HTadjust_interval(time_knob=dummy_wait_time)

            else:
                msg='This is the first round of measurement.\n'
                self.logger_or_printer(msg,flag='info')
                
                second_round=True
                
                msg='Starting measuring the current in the Linac for a second time.\n'
                self.logger_or_printer(msg,flag='info')

                linac_current=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number,offset=cycle_offset)
                
                msg='Selector for BCT15 measurement-> '+self.BCT15_selector+'.\n'
                self.logger_or_printer(msg,flag='info')


        else:    

            if not HTadjust_test:
                msg='Stable conditions. This is not a test! Forwarding SET request and adjusting the HT voltage within Vrange.\n'
                self.logger_or_printer(msg,flag='info')
                self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='sourceHT',val_to_set=new_value_SRCVOLT)
            else:
                msg='This is a test. No SET operation on-going.\n'
                self.logger_or_printer(msg,flag='info')

    def run(self,dummy_wait_time=10,shot_number=2,cycle_offset=0):
        
        global linac_current_start,HTadjust_kill, HTadjust_interval,HTadjust_inhibit,HTadjust_vrange,HTadjust_test,HT_start,second_round,BCT15_new,HT_new
        
        self.initiate_logger()   
        self.initiate_JAPC()# Change pseudo_set to False to escape simulation mode for SET action
        self.initiate_elogbook() # Current issuing on TESTS logbook
        
        msg='Dummy wait time is: '+str(dummy_wait_time)+'.\n'
        self.logger_or_printer(msg,flag='debug')
        
        msg='Initiating JAPC, E-Logbook and HTadjust logger.\n'
        self.logger_or_printer(msg,flag='debug')
        
        msg='Checking HTadjust_kill flag.\n'
        self.logger_or_printer(msg,flag='info')

        HTadjust_kill=self.get_HTadjust('kill')

        while not HTadjust_kill:
            
            msg='Running HTadjust module.\n'
            self.logger_or_printer(msg,flag='info')
            
            msg='Acquiring HTadjust_inhibit.\n'
            self.logger_or_printer(msg,flag='debug')

            HTadjust_inhibit=self.get_HTadjust('inhibit')
            
            msg='The inhibit flag is: '+str(HTadjust_inhibit)+'.\n'
            self.logger_or_printer(msg,flag='info')

            msg='Acquiring HTadjust_interval.\n'
            self.logger_or_printer(msg,flag='debug')

            HTadjust_interval=self.get_HTadjust('intervall')

            msg='Elapsed time from last HT adjustment is '+str(HTadjust_interval)+' minutes.\n'
            self.logger_or_printer(msg,flag='info')

            if not HTadjust_inhibit:

                msg='Acquiring HTadjust_test.\n'
                self.logger_or_printer(msg,flag='debug')

                HTadjust_test=self.get_HTadjust('test')

                msg='The test flag is: '+str(HTadjust_test)+'.\n'
                self.logger_or_printer(msg,flag='debug')

                msg='Acquiring HTadjust_Vrange.\n'
                self.logger_or_printer(msg,flag='info')

                HTadjust_vrange=self.get_HTadjust('Vrange')

                msg='The HT voltage will be adjusted within a +/- '+str(HTadjust_vrange)+' V range.\n'
                self.logger_or_printer(msg,flag='info')

                msg='Acquiring source HT voltage.\n'
                self.logger_or_printer(msg,flag='info')

                HT_start=self.get_my_JAPC_parameter(device="IP.NSRCGEN",field="Setting",parameter='sourceHT',my_selector=None,no_shots=1,offset=0)['Mean']

                msg='The current HT voltage is '+str(HT_start)+' Volts.\n'
                self.logger_or_printer(msg,flag='info')

                second_round=False #1

                msg='Measuring the current for '+str(shot_number)+' shots at the Linac from BCT15 for the first time'+'.\n'
                self.logger_or_printer(msg,flag='info')

                linac_current_start=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number,offset=cycle_offset)

                new_set_HTV=HT_start+HTadjust_vrange

                msg='First linac current measurement: Mean-> '+str(linac_current_start['Mean'])+', Sigma-> '+str(linac_current_start['Sigma'])+'.\n'
                self.logger_or_printer(msg,flag='info')

                self.HT_Linac_Current_Decider(linac_current_start,new_set_HTV,dummy_wait_time,shot_number=shot_number,cycle_offset=0)

                second_round=False #2

                msg='Measuring the current for '+str(shot_number)+' shots at the Linac from BCT15 for the second time.\n'
                self.logger_or_printer(msg,flag='info')

                linac_current_p=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number,offset=cycle_offset)

                new_set_HTV=HT_start-HTadjust_vrange

                msg='Second linac current measurement: Mean-> '+str(linac_current_p['Mean'])+', Sigma-> '+str(linac_current_p['Sigma'])+'.\n'
                self.logger_or_printer(msg,flag='info')

                self.HT_Linac_Current_Decider(linac_current_p,new_set_HTV,dummy_wait_time,shot_number=shot_number,cycle_offset=0)

                second_round=False #3

                msg='Measuring the current for '+str(shot_number)+' shots at the Linac from BCT15 for the third time.\n'
                self.logger_or_printer(msg,flag='info')

                linac_current_m=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number)

                msg='Third linac current measurement: Mean-> '+str(linac_current_m['Mean'])+', Sigma-> '+str(linac_current_m['Sigma'])+'.\n'
                self.logger_or_printer(msg,flag='info')
        #         logger.info('\n')



                while linac_current_m['Sigma'] > 0.1*linac_current_m['Mean']:


                    if second_round:

                        msg='This is the second round in m measurement.\n'
                        self.logger_or_printer(msg,flag='debug')

                        msg='The current measurement from BCT15 is too unstable. Writing to eLogbook.\n'
                        self.logger_or_printer(msg,flag='info')

                        self.write_L3_logbook(flag_unstable=True)

                        if not HTadjust_test:
                            self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='source',val_to_set=HT_start)
                        self.wait_HTadjust_interval(time_knob=dummy_wait_time)

                    else:

                        msg='This is the first round in m measurement.\n'
                        self.logger_or_printer(msgflag='debug')

                        second_round=True
                        
                        linac_current_m=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number)

                else:

                    if linac_current_p['Mean']>linac_current_start['Mean']:
                        msg='Current p larger than current start.\n'
                        self.logger_or_printer(msg,flag='debug')

                        if linac_current_p['Mean']>linac_current_m['Mean']:
                            msg='Current p larger than current m.\n'
                            self.logger_or_printer(msg,flag='debug')

                            HT_new=HT_start+HTadjust_vrange
                            BCT15_new=linac_current_p['Mean']

                    elif linac_current_m['Mean']>linac_current_start['Mean']:
                        msg='Current m larger than current start.\n'
                        self.logger_or_printer(msg,flag='debug')

                        HT_new=HT_start-HTadjust_vrange
                        BCT15_new=linac_current_m['Mean']

                    else:
                        msg='Setting HT_new and BCT_new to their current values.\n'
                        self.logger_or_printer(msg,flag='info')

                        HT_new=HT_start
                        BCT15_new=linac_current_start['Mean'] # This is not in the flowchart..should it be inside ?

                    if not HTadjust_test:

                        self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='sourceHT',val_to_set=HT_new)                        
                        self.write_L3_logbook(flag_unstable=False)
                            
#                         except:   
#                             msg='Unable to write to elogbook.\n'
#                             self.logger_or_printer(msg)

                        self.wait_HTadjust_interval(time_knob=dummy_wait_time)

            else:
                # Wait for new input and restart
                self.wait_HTadjust_interval(time_knob=dummy_wait_time)

        else:
            msg='End of module HTadjust: Kill flag raised by the user.\n'
            self.logger_or_printer(msg,flag='info') 
            logger.info()
    
    
    # A small snippet for string comparison
    @staticmethod
    def contains_word(s, w):
        return f'{w}' in f' {s} '
        
        

 


