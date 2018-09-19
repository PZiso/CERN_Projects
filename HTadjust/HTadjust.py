# For some simple calculations
import numpy as np

#PyJAPC for getting & setting FESA parameters
import pyjapc
 
# Time module for sleeping
from time import sleep, strftime

#PyLogBook to push events to the eLogbook
import pylogbook

#Logging for keeping up with the flow...
import logging

# For logging with time-stamp
import datetime

#Sys needed for logging in Jupyter with StreamHandler..It can be removed for non-Jupyter platform
from sys import stderr,exit


class HTadjust(object):
    """
    The HTadjust module is used for monitoring and maximizing the ion current
    in Linac3 after regulation of the HighVoltage source. The observable is the
    ion beam current from the BCT15 device and the parameter under adjustment is the sourceHT voltage.
    The module is executed by calling the run() method of the HTadjust class. 
    See more information in the docstrings of all the class methods.
    
    """
        
    
    
    def __init__(self,FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='HTajust',
                 simulate_SET=True,INCA_ACCEL='LEIR',sourceHT_selector=None,
                 BCT15_selector='LEI.USER.ALL',which_ebook='TESTS',
                 no_elog_write=False,log_me=True,log_level='DEBUG'):
        """
        Initialisation of the HTadjust module. The input parameters are:
        
        FESA_GHOST_Device: (default:GHOSTconfig): The device of the GHOST module in the appropriate FESA class.
        
        FESA_GHOST_Property: (default:HTajust): The property of the GHOST module in the appropriate FESA class.
        
        simulate_SET:(default:True): Run the HTadjust module in simulation mode i.e. without actually adjusting any 
        of the parameters on the FESA class.
        
        INCA_ACCEL:(default:LEIR): The INCA accelerator.
        
        sourceHT_selector:(default:None): The selector for interacting with the sourceHT parameter.
        
        BCT15_selector:(default:'LEI.USER.EARLY'):The selector for interacting with the currentLinacSingle parameter.
        
        which_ebook:(default:'TESTS'): The elogbook to push events from the elogbook module.
        
        no_elog_write:(default:False): Flag to suppress pushing events to the elogbook
        
        log_me:(default:True): Flag to initiate the logger module for the local log system.
        
        log_level:(default:'DEBUG'): The level of logging for the local log system.
        
        
        
        
        
        """
        
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
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        self.__version__='v.1.1'
        
    
        
    def my_stopper(self,flag='initial'):
        
        
        
        if flag=='initial':
            verbose=1
        else:
            verbose=0
        
        
        
        if verbose:
            msg='Checking HTadjust_kill flag.\n'
            self.logger_or_printer(message=msg,flag='info')

        signum=self.get_HTadjust('kill')

        if signum:
            
            msg='Terminating HTadjust module: Kill flag raised by the user.\n'
            self.logger_or_printer(message=msg,flag='info')
            
            if not self.no_elog_write:
                
                elog.create_event(msg+'[GHOST:HTadjust]')

            exit(msg)
        
        else:
            
            if verbose:
                msg='HTadjust_kill checked. Running HTadjust module.\n'
                self.logger_or_printer(message=msg,flag='info')
                
                if not self.no_elog_write:
                    
                    elog.create_event(msg+'[GHOST:HTadjust]')

            return
        
        
        
    def initiate_JAPC(self,log=50):
        """Initialisation of the pyJAPC module. The class arguments are passed in the pyjapc module as:
        pyjapc.PyJapc(selector=ourceHT_selector,
                           incaAcceleratorName=INCA_ACCEL,noSet=simulate_SET) 
        """

        global japc
        japc=pyjapc.PyJapc(selector=self.sourceHT_selector,
                           incaAcceleratorName=self.INCA_ACCEL,noSet=self.simulate_SET,logLevel=log) 

    def initiate_elogbook(self):
        """
        Initialisation of the elogbook module. The class arguments are passed in the elogbook module as:
        pylogbook.eLogbook(which_ebook)
        
        """
        global elog
        elog=pylogbook.eLogbook(self.which_ebook)
    
    def initiate_logger(self):
        """
        Initialisation of the logging system. The Python logging module is used. The class argument of log_level,
        is passed  in the logging module and the default directory and name of the log files is 
        LogFiles/HT_adjust.log.
        
        """
        if self.log_me:

            global logger
            ttl='{:%Y-%m-%d_%H_%M_%S}'.format(datetime.datetime.now())
            dir_='../log/'
            file_name=dir_+'HTadjust_'+ttl+'.log'
            # Create logger
            logger = logging.getLogger('HTadjust')
            lvl=logging.getLevelName(self.log_level)
            logger.setLevel(lvl)
             # Create STDERR handler
            handler_stream = logging.StreamHandler(stderr)
            handler_logfile=logging.FileHandler(file_name,mode='w')

            # ch.setLevel(logging.DEBUG)

            # Create formatter and add it to the handler
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            handler_logfile.setFormatter(formatter)

            # Set STDERR handler as the only handler 
            logger.handlers = [handler_stream,handler_logfile]
        else:

            pass

     
    
    def logger_or_printer(self,message,flag):
        """
        Function to switch between logging or print mode, according to the HTadjust module initialization parameter log_me.
        The input msg is the message (string) to be logged or printed. 
        The flag corresponds to the user defined severity (logging level) for the msg input.
        
        """
        
    
        if self.log_me:
            
            lvl=self.log_level
            
            if (lvl=='INFO') and (flag=='info'):
                logger.info(message)
            elif (lvl=='DEBUG') and (flag=='debug'):
                logger.debug(message)
            elif (lvl=='WARNING') and (flag=='warning'):
                logger.warning(message)
            elif (lvl=='ERROR') and (flag=='error'):
                logger.error(message)
            elif (lvl=='CRITICAL') and (flag=='critical'):
                logger.critical(message)

        else:
            
#             logger.info('Logging suppressed by the user.\n')
            print('Log of HTadjust activity suppressed by the user. Message: '+message)

                
    def get_HTadjust(self,HTadjust_input):
        
        """
        Method to get the values of the HTadjust parameters in the GHOST FESA class via the GET method of pyjapc module.
        The input HTadjust_input (string) can be only the keywords kill, inhibit, test, Vrange, intervall
        which correspond to the HTadjust_kill, HTadjust_inhibit, HTadjust_test, HTadjust_Vrange, HTadjust_intervall
        parameters.
        
        """

        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        valid_params=japc.getParamInfo(my_field)
        param_full_name='HTadjust_'+HTadjust_input

        try:

            HTadjust_param=japc.getParam(my_field+'#'+param_full_name)
            return HTadjust_param

        except:
            msg='There seems to be a problem communicating with the FEC. No GET action is possible. Aborting.\n'
            self.logger_or_printer(msg,flag='error')
            raise ValueError(msg)


        
            
    def set_HTadjust(self,HTadjust_input,val_to_set):
        """
        Method to set the values of the HTadjust parameters in the GHOST FESA class via the SET method of pyjapc module.
        The input HTadjust_input (string) can be only the keywords kill, inhibit, test, Vrange, intervall
        which correspond to the HTadjust_kill, HTadjust_inhibit, HTadjust_test, HTadjust_Vrange, HTadjust_intervall
        parameters. The val_to_set input is the new value. Note that actual SET happens if and only if the HTadjust module
        has not been initialised in simulation mode via the 'simulate_SET' flag.
        
        """
       
        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        valid_params=japc.getParamInfo(my_field)
        param_full_name='HTadjust_'+HTadjust_input

        try:

            map_params=japc.getParam(my_field)
            map_params[param_full_name]=val_to_set
            japc.setParam(my_field,map_params)
            msg='Setting %s#%s parameter to value %s.\n'%(my_field,param_full_name,val_to_set)
            self.logger_or_printer(message=msg,flag='info')

        except:

            msg='There seems to be a problem communicating with the FEC. Aborting SET action.\n'
            self.logger_or_printer(msg,flag='error')
            raise ValueError(msg)    

    
    
           
    def get_my_JAPC_parameter(self,device,field,parameter,my_selector=None,no_shots=10,subscribe_=1,basic_per=1.2,verbose=True):
        """
        Method to get the values of any FESA parameter via the GET method of pyjapc module.

        The inputs are:{

        device: The device name in FESA

        field:  The field name in FESA

        parameter: The parameter name in FESA

        my_selector: The PLS selector (Set None for non-ppm parameters)

        no_shots: The number of shots that the variable is measured.

        }

        The outputs are:{

        A dictionary with the keys 'Values'-> the vector of the measurements of length no_shots,
        'Mean'-> The average value of the 'Values' vector, 'Sigma'->The standard deviation of the 'Values' vector.

        }

        Normally the pyjapc module GET function is called to interact with 
        the parameter device/field#parameter (based on the JAPC rules)

        """
        
        self.my_stopper(flag='')

        my_constructor=device+'/'+field+'#'+parameter
        global ind_
        
        
        if subscribe_:
        
            param=[]
            ind_=1
            
            def newValueCallback(parameterName, newValue, headerInfo):

                """
                Call-back function to subscribe to the parameter parameterName. 
                The output is the newValue value of the parameter. This function
                is called through pyjapc for the number of shots that the user
                has defined (no_shots)

                """
                
                
                global ind_

            #     param.append(newValue)
                if not headerInfo['isFirstUpdate']:
                    param.append(newValue)
                    msg="({0}) Measured value for {1} is: {2}\n".format(ind_,parameterName, "%.3f"%newValue)
                    if verbose:
                        self.logger_or_printer(message=msg,flag='info')
                    ind_+=1

            japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.\n'
            self.logger_or_printer(message=msg,flag='info')

            japc.subscribeParam(my_constructor, newValueCallback, getHeader=True)
            japc.startSubscriptions()

            while True:

                if ind_<=no_shots:
                    continue
                else:
                    japc.stopSubscriptions()
                    japc.clearSubscriptions()
                    break
            param=param[:no_shots]


            
        else:
            
            param=[]
            ind_=1
            msg="Manual JAPC Measurement Mode: Waiting for "+str(basic_per)+" seconds for each measurement.\n"
            self.logger_or_printer(message=msg,flag='info')
            
            japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.\n'
            self.logger_or_printer(message=msg,flag='info')
            
            for k in range(no_shots):
                newValue=japc.getParam(my_constructor)
                param.append(newValue)
                msg="("+str(ind_)+") Measured value for {0} is: {1}\n".format(my_constructor, "%.3f"%newValue)
                if verbose:
                    self.logger_or_printer(message=msg,flag='info')
                sleep(basic_per)
                ind_+=1
                japc.stopSubscriptions()
                japc.clearSubscriptions()
        
        
        return {'Values':param,'Mean':np.mean(param),'Sigma':np.std(param)}
    
    

    def set_my_JAPC_parameter(self,device,field,parameter,val_to_set,lim_l,lim_r,my_selector=None):
        
        """
        Method to set the values of any FESA parameter via the SET method of pyjapc module.
        
        The inputs are:
        
        {
        
        device: The device name in FESA
        
        field:  The field name in FESA
        
        parameter: The parameter name in FESA
        
        val_to_set: The new value to be set.
        
        my_selector: The PLS selector (Set None for non-ppm parameters)
        
        lim_l, lim_r: The lower and upper limits of the value to be set. If the val_to_set value is outside this range, the SET action
        is aborted and the parameter retains its initial value.
        
        }
        
        
        Normally the pyjapc module SET function is called to interact with 
        the parameter device/field#parameter (based on the JAPC rules)
        
        """
        
        self.my_stopper(flag='')
        
        my_constructor=device+'/'+field
        japc.setSelector(my_selector)
        dic_FESA=japc.getParam(my_constructor)
        temp={}
        for key,item in dic_FESA.items():
            if not (('_min' in key ) or ('_max' in key)):
                temp[key]=item
        
        dic_FESA=temp
        
        if float(val_to_set)>=float(lim_l) and float(val_to_set)<=float(lim_r):
              
            dic_FESA[parameter]=float(val_to_set)
            
            try:
            
                japc.setParam(my_constructor,dic_FESA)
                msg='Setting '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.\n'
                self.logger_or_printer(message=msg,flag='info')
            except:
                msg='Unable to set '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)
                self.logger_or_printer(msg,flag='error')
                raise ValueError('Unable to set '+my_constructor+'#'+parameter+' parameter to value '+
                                 str(val_to_set))
        
        else:
            msg=('Given value to SET is outside safe operating range (Limit->['+str(lim_l)+' '+str(lim_r)+']) . Aborting SET for parameter '
            +my_constructor+'#'+parameter+'.\n')
            
            self.logger_or_printer(msg,flag='info')
            
            
                

                    
         
        
    
    def write_L3_logbook(self,flag_unstable):
        """
        Method to write predefined messages to the elogbook. The elogbook is defined from the user
        at the instantation of the HTadjust module. The action of writing to the elogbook can be 
        suppressed with the no_elog_write flag. The messages are also written in the local log file in case the 
        log_me flag=True in the class of HTadjust module.
        
        """
        if flag_unstable:
            my_message=('After '+str(HTadjust_interval)+
            ' minutes, ITF.BCT15 was measured but too unstable for adjustment.\n [GHOST:HTadjust]')
        else:
            my_message=('After '+str(HTadjust_interval)+
            ' minutes, ITF.BCT15 was measured, change of HT from '+str("%d"%HT_start)+
            ' to '+str("%d"%HT_new)+'. \nChanged ITF.BCT from '+str("%.3f"%linac_current_start['Mean'])+
            ' to '+str("%.3f"%BCT15_new)+'\n[GHOST:HTadjust]')

        
        if not self.no_elog_write: 
        
            elog.create_event(my_message)
            
            if self.log_me:
                msg='New entry in eLogBook: '+my_message+'.\n'
            
                self.logger_or_printer(message=msg,flag='info')

        else:

            if self.log_me:
                msg='Operation of logging to elogbook suppresed:\n'
                self.logger_or_printer(msg, flag='info')
                self.logger_or_printer(my_message, flag='info')

        
    def wait_HTadjust_interval(self,time_knob=0):
        """
        Method to freeze the execution of the HTadjust module after the regulations on the
        HT source are performed. The freeze is performed with the sleep method of the time module.
        
        The duration of the freeze is user defined via the FESA parameter HTadjust_intervall (in minutes).
        After the pass of HTadjust_intervall minutes, the module looks for the new value of the HTadjust_kill
        parameter in the FESA class and restarts if it is allowed.
        
        """
        
        global HTadjust_interval, HTadjust_kill

        HTadjust_interval=self.get_HTadjust('intervall') # This is in minutes !
        
        if not time_knob:
            msg='End of module. Waiting for '+str(HTadjust_interval)+' minutes.\n'
            if self.log_me:
                self.logger_or_printer(message=msg,flag='info')
            if not self.no_elog_write:
                 elog.create_event(msg+'[GHOST:HTadjust]')

             
            m=1
            while m<=HTadjust_interval*60:
                
                self.my_stopper(flag='')
                sleep(1)# Input in seconds
                m+=1
            
        else:
            
            msg='End of module. User defined sleep time. Waiting for '+str(time_knob)+' seconds.\n'

            if self.log_me:
                self.logger_or_printer(message=msg,flag='info')
            if not self.no_elog_write:
                 elog.create_event(msg+'[GHOST:HTadjust]')            
            
            m=1
            while m<=time_knob:
                
                self.my_stopper(flag='')
                sleep(1)# Input in seconds
                m+=1
        msg='Restarting HTadjust Module. Acquiring new value for the HTadjust_kill flag.\n'

        if self.log_me:
            self.logger_or_printer(message=msg,flag='info')
        if not self.no_elog_write:
             elog.create_event(msg+'[GHOST:HTadjust]')  

        HTadjust_kill=self.get_HTadjust('kill')
    
    
    
    def HT_Linac_Current_Decider(self,linac_current,new_value_SRCVOLT,safe_volt_low,safe_volt_high,shot_number=10):
        
        """
        *** inputs:
        {
        
        linac_current: The measurement of the linac current (dictionary)
        
        new_value_SRCVOLT: The new value to set the HT voltage.
        
        dummy_wait_time: A user defined flag to suppress the waiting time for HTadjust_intervall minutes. 
        For example, if HTadjust_intervall=60 (in minutes) and dummy_wait_time=1 (in seconds), the program will be frozen for 1 second
        instead of 60 minutes. If dummy_wait_time=0 (in seconds), then the HTadjust_intervall time is not overridden
        and the waiting time is 60 minutes in this case.
        
        shot_number: The number of shots for the linac current measurement (see get_my_JAPC_parameter() method.
        
        
        }
        
        *** Description:
        
        A block of code for decisions and actions based on the observable of the Linac3 current.
       {
        { First, a check on the stability of the measurement of the current is made. If the conditions are unstable, a second
        round of measurements is performed. 
            { 
                If the second round is also unstable, the adjustments of the HT voltage are aborted.
            }
                
                { 
                    If the HTadjust_test parameter from the FESA class is False, the HT source voltage is not changed and if 
                    HTadjust_test is True, no SET operations are performed.
                }
    
        }
        
        { 
          Second, if the conditions are stable, and if the module is executed in not a test mode (via HTadjust_test),
          the HT source voltage is set to a new value, according to the specifications of the HTadjust module.
        }
        

        }
        
        """
        global second_round
        self.my_stopper(flag='')
        status=1
        while linac_current['Sigma']>0.1*linac_current['Mean']:
            msg='Unstable conditions of linac current measurement. Checking if this is the first round.\n'
            self.logger_or_printer(message=msg,flag='info')
            
            if second_round:
                msg='This is the second round. The current measurement from BCT15 is too unstable. Writing to eLogbook.\n'
                
                self.logger_or_printer(message=msg,flag='info')
                
                self.write_L3_logbook(flag_unstable=True)

                if not HTadjust_test:
                    msg='This is not a test! Forwarding SET request and setting the HT voltage to the initial value.\n'
                    self.logger_or_printer(message=msg,flag='info')
                    self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',
                                               parameter='sourceHT',val_to_set=HT_start,
                                               lim_l=safe_volt_low,lim_r=safe_volt_high,my_selector=None) 
                else:
                    msg='This is a test. No SET operation on-going.\n'
                    self.logger_or_printer(message=msg,flag='info')

                #msg='End of module. Waiting for new time interval for HT adjust.\n'
                #self.logger_or_printer(message=msg,flag='info')
                status=0
                break
#                 self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                

            else:

                msg='This is the first round of measurement.\n'
                self.logger_or_printer(message=msg,flag='info')
                
                second_round=True
                
                msg='Measuring the current in the Linac for a second round.\n'
                self.logger_or_printer(message=msg,flag='info')

                linac_current=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',
                                                         parameter='currentLinacSingle',
                                                         my_selector=self.BCT15_selector,no_shots=shot_number)
                
                msg='Selector for BCT15 measurement-> '+self.BCT15_selector+'.\n'
                
                self.logger_or_printer(message=msg,flag='info')
                


        else:    

            if not HTadjust_test:
                msg='Stable conditions. This is not a test! Forwarding SET request and adjusting the HT voltage within Vrange.\n'
                self.logger_or_printer(message=msg,flag='info')
                self.set_my_JAPC_parameter(device='IP.NSRCGEN',
                                           field='Setting',parameter='sourceHT',
                                           val_to_set=new_value_SRCVOLT,lim_l=safe_volt_low,lim_r=safe_volt_high)
                
            else:
                msg='This is a test. No SET operation on-going.\n'
                self.logger_or_printer(message=msg,flag='info')
         
        # print('My status from HT_Linac_Current_Decider is '+str(status))        
        return status

    def run(self,dummy_wait_time=10,shot_number=10):
        """
        The main function of the HTadjust module. It executes the HTadjust module based on the current specifications.
        
        *** inputs:
        {
            dummy_wait_time: Overrides the HTadjust_intervall waiting time. Note that this value (dummy_wait_time)
            is given in seconds. This variable is passed in HT_Linac_Current_Decider() method as well. 
            See the description of that method for more information.
            
            shot_number: The number of shots in the cycle for which the BCT15 current is measured. 
            This variable is passed in get_my_JAPC_parameter(), HT_Linac_Current_Decider() methods.
            
            

            
        
        }
        
        *** Description (N.B.: All operations are recorded in the elogbook and the local log) :
        
        {
            Initially, the programm initiates pyjapc, elogbook and the local logger. 
            Then it looks for the variables HTadjust_kill, HTadjust_inhibit, HTadjust_Vrange, HTadjust_intervall.
            
            {
            
            In case HTadjust_kill=True, the program is not executed.
                
                {
                
                In case HTadjust_inhibit=True, the program is not executed until this flag is changed.
                
                    {
                        If the program is finally executed, it performs one measurement of the initial HT voltage (HTstart).
            
                        
                        The linac current is measured for the first time (for no_shots consecutive times).
                        The new value of the HT source to be set is HTstart+HTadjust_Vrange
                        The HT_Linac_Current_Decider() method is called with the initial current measurement and
                        the new value of the HT source as inputs.
                        
                        
                        The linac current is measured for the second time (for no_shots consecutive times).
                        The new value of the HT source to be set is HTstart-HTadjust_Vrange
                        The HT_Linac_Current_Decider() method is called with the second current measurement and
                        the new value of the HT source as inputs.
                        
                        
                        The linac current is measured for the third time (for no_shots consecutive times).
                        
                        If the conditions of the measurements are unstable after two rounds of measuremets, 
                        no SET operations are performed and the module enters in frozen mode with the 
                        wait_HTadjust_interval() method.
                        
                        If the conditions are not unstable, then the following actions are performed:
                        
                            {
                                
                                The second current measurement is compared to the initial one. 
                                
                                If the second measurement is larger, then :
                                
                                    {
                                    
                                        A comparison is made with the third current measurement.
                                        If it is larger, then maximization of the current is fulfilled
                                        and the settings for the source HT and the beam current value
                                        are retained and set at the source

                                    }
                                    
                                If it is smaller, then:
                                
                                    {         
                                        The third current measurement is compared to the initial current measurement.
                                        If it is larger, then maximization of the current is fulfilled
                                        and the settings for the source HT and the beam current value
                                        are retained and set at the source

                                    }
                                    
                                If the comparisons show that the initial current measurement is 
                                larger than the next two, it means that the maximisation of the current is not needed.
                                The initial settings for the source HT and the beam current value 
                                are retained and set at the source.
                                
                            }
                        
                        
                        After all the operations have taken place, the program enters in a frozen mode
                        with the wait_HTadjust_interval() method. The new value of HTadjust_kill is recorded
                        from the program, and it restarts if allowed.
                        
                        
                    }
                
                }
            }
        
        
        
        
        }
        """
        
        
        #this line here should change at some point.
        global BCT15_new, linac_current_start, HT_new, HT_start
        global second_round, HTadjust_kill, HTadjust_interval,HTadjust_inhibit
        global HTadjust_vrange,HTadjust_test
        

        self.initiate_logger()   
        self.initiate_JAPC()# Change pseudo_set to False to escape simulation mode for SET action
        self.initiate_elogbook() # Current issuing on TESTS logbook
        
        # Hard-coded values for HT voltage operation range
        safe_volt_low=19040
        safe_volt_high=19100


        if self.log_me and self.simulate_SET:
            msg='******Initiating HTadjust module in Simulation Mode. No SET operations will be performed******\n'
            self.logger_or_printer(message=msg,flag='info')
            
        elif not self.no_elog_write and self.simulate_SET:
            msg='******Initiating HTadjust module in Simulation Mode. No SET operations will be performed******\n[GHOST:HTadjust]'
            elog.create_event(msg)

        
        msg='******Initiating HTadjust module.******\n'
        self.logger_or_printer(message=msg,flag='info')
            
        if not self.no_elog_write:
            msg='******Initiating HTadjust module.******\n[GHOST:HTadjust]'
            elog.create_event(msg)

        msg='Dummy wait time is: '+str(dummy_wait_time)+'.\n'
        self.logger_or_printer(message=msg,flag='debug')

        msg='Initiating JAPC, E-Logbook and HTadjust logger.\n'
        self.logger_or_printer(message=msg,flag='debug')
   
        self.my_stopper(flag='initial')

        msg='Acquiring HTadjust_inhibit.\n'
        self.logger_or_printer(msg,flag='debug')

        HTadjust_inhibit=self.get_HTadjust('inhibit')

        msg='The inhibit flag is: '+str(HTadjust_inhibit)+'.\n'
        self.logger_or_printer(message=msg,flag='info')

        msg='Acquiring HTadjust_interval.\n'
        self.logger_or_printer(msg,flag='debug')

        HTadjust_interval=self.get_HTadjust('intervall')

        msg='Elapsed time from last HT adjustment is '+str(HTadjust_interval)+' minutes.\n'
        self.logger_or_printer(message=msg,flag='info')

        while True:
            
            while not HTadjust_inhibit:
                japc.setSelector(None)
                HT_status=japc.getParam('IP.NSRCGEN/Status#sourceHTStatus')

                if not HT_status[0]==2:
                    msg="The status of the source is {}. Waiting 1 minute for the status to become ON.\n".format(HT_status[1])
                    self.logger_or_printer(message=msg,flag='info')
                    sleep(60)
                    continue
                else:
                    msg="The status of the source is {}. Proceeding with HTadjust operations.\n".format(HT_status[1])
                    self.logger_or_printer(message=msg,flag='info')
                    pass

                msg='Acquiring HTadjust_test.\n'
                self.logger_or_printer(msg,flag='debug')

                HTadjust_test=self.get_HTadjust('test')

                msg='HTadjust_test checked. The test flag is: '+str(HTadjust_test)+'.\n'
                self.logger_or_printer(msg,flag='debug')

                msg='Acquiring HTadjust_Vrange.\n'
                self.logger_or_printer(message=msg,flag='info')

                HTadjust_vrange=self.get_HTadjust('Vrange')

                msg='The HT voltage will be adjusted within a +/- '+str(HTadjust_vrange)+' V range.\n'
                self.logger_or_printer(message=msg,flag='info')

                msg='Acquiring source HT voltage.\n'
                self.logger_or_printer(message=msg,flag='info')

                HT_start=self.get_my_JAPC_parameter(device="IP.NSRCGEN",field="Setting",
                                                    parameter='sourceHT',my_selector=None,subscribe_=0,no_shots=1)['Mean']

                msg='The current HT voltage is '+str(HT_start)+' Volts.\n'

                self.logger_or_printer(message=msg,flag='info')

                second_round=False #1

                #Do a first current measurement and examine if it is above \ below the threshold


                Init_BCT=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=2,subscribe_=1,verbose=False)['Mean']
                msg='Initial ion beam current measurement is {}\n'.format("%.3f"%Init_BCT)
                self.logger_or_printer(message=msg,flag='info')
                if Init_BCT<0.01:
                    msg="The measurement of the BCT15 currentLinacSingle is below threshold (0.01 mA). Waiting for 1 minute and restarting.\n"
                    self.logger_or_printer(message=msg,flag='info')
                    sleep(60)
                    continue
                else:
                    msg="The measurement of the BCT15 currentLinacSingle is above threshold (0.01 mA). Proceeding with HTadjust measurements.\n"
                    self.logger_or_printer(message=msg,flag='info')
                    pass

                msg=('Measuring the current for '+str(shot_number)+' shots at the Linac from BCT15 for the first time'+'.\n')
                self.logger_or_printer(message=msg,flag='info')

                linac_current_start=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',my_selector=self.BCT15_selector,no_shots=shot_number)

                new_set_HTV=HT_start+HTadjust_vrange

                msg=('First linac current measurement (DV=0): Mean-> '+str("%.3f"%linac_current_start['Mean'])+', Sigma-> '+str("%.3f"%linac_current_start['Sigma'])+'.\n')

                self.logger_or_printer(message=msg,flag='info')

                status=self.HT_Linac_Current_Decider(linac_current_start,new_set_HTV,safe_volt_low,safe_volt_high,shot_number=shot_number)

                if not status:
                    self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                    msg='I am in the first not status loop!'
                    self.logger_or_printer(message=msg,flag='debug')
                    continue


                second_round=False #2

                msg=('Measuring the current for '+str(shot_number)+
                ' shots at the Linac from BCT15 for HT DV= + '+str(HTadjust_vrange)+' V.\n')

                self.logger_or_printer(message=msg,flag='info')

                linac_current_p=self.get_my_JAPC_parameter(
                    device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',
                 my_selector=self.BCT15_selector,no_shots=shot_number)

                new_set_HTV=HT_start-HTadjust_vrange

                msg=('Second linac current measurement (+ DV): Mean-> '+
                str("%.3f"%linac_current_p['Mean'])+', Sigma-> '+str("%.3f"%linac_current_p['Sigma'])+'.\n')

                self.logger_or_printer(message=msg,flag='info')

                status=self.HT_Linac_Current_Decider(linac_current_p,new_set_HTV,safe_volt_low,safe_volt_high,shot_number=shot_number)
                # print('#2 Run(): My status is '+str(status))
                if not status:
                    self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                    msg='I am in the second not status loop!'
                    self.logger_or_printer(message=msg,flag='debug')
                    continue

                second_round=False #3

                msg=('Measuring the current for '+str(shot_number)+
                ' shots at the Linac from BCT15 for HT DV= - '+str(HTadjust_vrange)+' V.\n')

                self.logger_or_printer(message=msg,flag='info')

                linac_current_m=self.get_my_JAPC_parameter(
                    device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',
                my_selector=self.BCT15_selector,no_shots=shot_number)

                msg=('Third linac current measurement (- DV): Mean-> '+
                str("%.3f"%linac_current_m['Mean'])+', Sigma-> '+str("%.3f"%linac_current_m['Sigma'])+'.\n')

                self.logger_or_printer(message=msg,flag='info')

                status=1

                while status:


                    while linac_current_m['Sigma'] > 0.1*linac_current_m['Mean']:


                        if second_round:

                            msg='This is the second round in m measurement.\n'
                            self.logger_or_printer(msg,flag='debug')

                            msg='The current measurement from BCT15 is too unstable. Writing to eLogbook.\n'
                            self.logger_or_printer(message=msg,flag='info')

                            self.write_L3_logbook(flag_unstable=True)

                            if not HTadjust_test:
                                self.set_my_JAPC_parameter(
                                    device='IP.NSRCGEN',field='Setting',parameter='source',val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high)


                            status=0
                            continue

                        else:

                            msg='This is the first round in m measurement.\n'
                            self.logger_or_printer(msg,flag='debug')

                            second_round=True

                            linac_current_m=self.get_my_JAPC_parameter(
                                device="ITF.BCT15",field='Acquisition',parameter='currentLinacSingle',
                             my_selector=self.BCT15_selector,no_shots=shot_number)

                    else:

                        if linac_current_p['Mean']>linac_current_start['Mean']:
                            msg='Current p larger than current start.\n'
                            self.logger_or_printer(msg,flag='debug')

                            if linac_current_p['Mean']>linac_current_m['Mean']:
                                msg='Current p larger than current m.\n'
                                self.logger_or_printer(msg,flag='debug')

                                HT_new=HT_start+HTadjust_vrange
                                BCT15_new=linac_current_p['Mean']

                            else:

                                msg='Current m larger than current start.\n'
                                self.logger_or_printer(msg,flag='debug')

                                HT_new=HT_start-HTadjust_vrange
                                BCT15_new=linac_current_m['Mean']



                        elif linac_current_m['Mean']>linac_current_start['Mean']:
                            msg='Current m larger than current start.\n'
                            self.logger_or_printer(msg,flag='debug')

                            HT_new=HT_start-HTadjust_vrange
                            BCT15_new=linac_current_m['Mean']

                        else:
                            msg='Setting HT_new and BCT_new to their current values.\n'
                            self.logger_or_printer(message=msg,flag='info')

                            HT_new=HT_start
                            BCT15_new=linac_current_start['Mean'] # This is not in the flowchart..should it be inside ?

                        if not HTadjust_test:

                            self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',\
                                                       parameter='sourceHT',val_to_set=HT_new,lim_l=safe_volt_low,lim_r=safe_volt_high)                        

                        self.write_L3_logbook(flag_unstable=False)


                        status=0


                else:

                    self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                    msg='I am in the last else loop !'
                    self.logger_or_printer(message=msg,flag='debug')
                    continue

            else:



            # Wait for new input and restart
                msg='Inhibition of module HTadjust: Inhibit flag raised by the user. The module will restart after change of flag.\n'
                self.logger_or_printer(message=msg,flag='info') 

                # self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                sleep(60)
                continue
                


    
    # A small snippet for string comparison
#     @staticmethod
#     def contains_word(s, w):
#         return f'{w}' in f' {s} '
    
if __name__ == "__main__":
        
    HT_object=HTadjust(simulate_SET=False, sourceHT_selector=None,
                       BCT15_selector='LEI.USER.ALL',
                       which_ebook='LINAC 3',no_elog_write=True,log_me=True,log_level='INFO') # # Roll back to simulation mode    
    HT_object.run(dummy_wait_time=0,shot_number=10) # Run HTadjust module.



