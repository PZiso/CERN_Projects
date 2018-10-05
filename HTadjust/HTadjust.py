# For some simple calculations
import numpy as np

#PyJAPC for getting & setting FESA parameters
import pyjapc
 
# Time module for sleeping
from time import sleep

#PyLogBook to push events to the eLogbook
import pylogbook

#Logging for keeping up with the flow...
import logging

# For logging with time-stamp
import datetime

#Sys.exit needed for killing the module
from sys import exit



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
                 no_elog_write=False,log_me=True,log_level='DEBUG',print_activity=False):
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

        self.print_activity=print_activity
        
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        
        self.__version__='v.1.4'
        
    
        
#                                              FUNCTION DEFINITIONS 
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #
        
        
        
    def initiate_JAPC(self,log=50):
        """Initialisation of the pyJAPC module. The class arguments are passed in the pyjapc module as:
        pyjapc.PyJapc(selector=ourceHT_selector,
                           incaAcceleratorName=INCA_ACCEL,noSet=simulate_SET) 
        """

        
        japc=pyjapc.PyJapc(selector=self.sourceHT_selector,
                           incaAcceleratorName=self.INCA_ACCEL,noSet=self.simulate_SET,logLevel=log) 
        return japc

    def initiate_elogbook(self):
        """
        Initialisation of the elogbook module. The class arguments are passed in the elogbook module as:
        pylogbook.eLogbook(which_ebook)
        
        """
        def elog_checker():
            
            elog_temp=pylogbook.eLogbook('TESTS')
            try:
                elog_temp.create_event('HTadjust test elogbook functionality.')
            except:
                self.no_elog_write=True
                msg=('Cannot push events to the OP logbook. ' + 
                    ' Problem with pylogbook module. Reverting to local logging only.')
                logger.info(msg)

        elog_checker()

        elog=pylogbook.eLogbook(self.which_ebook)
        return elog


    
    def initiate_logger(self):
        """
        Initialisation of the logging system. The Python logging module is used. The class argument of self.log_level,
        is passed  in the logging module and the default directory of the log files is in ../log. Each log file
        is unique, with a distinct time stamp.
        
        """
        if self.log_me:

            
            ttl='{:%Y-%m-%d_%H_%M_%S}'.format(datetime.datetime.now())
            dir_='../log/'
            file_name=dir_+'HTadjust_'+ttl+'.log'
            # Create logger
            logger = logging.getLogger('HTadjust')
            lvl=logging.getLevelName(self.log_level)
            logger.setLevel(lvl)

            handler_logfile=logging.FileHandler(file_name,mode='w')

            # Create formatter and add it to the handler
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            handler_logfile.setFormatter(formatter)

            logger.handlers = [handler_logfile]

            return logger
        
        else:

            return []



# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #
    
    def start_HTadjust(self):

        global logger, japc, elog


        logger=self.initiate_logger()   

        japc=self.initiate_JAPC()# Change pseudo_set to False to escape simulation mode for SET action
       
        elog=self.initiate_elogbook() # which_ebook: LINAC 3  


        if self.simulate_SET:

            msg='******Initiating HTadjust module in Simulation Mode. No SET operations will be performed******'

        else:

            msg='******Initiating HTadjust module.******'

        
        self.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')




# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

    
    def logger_or_printer(self,message,flag):
        """
        Function to switch between logging or print mode, according to the HTadjust module initialization parameter log_me.
        The input msg is the message (string) to be logged or printed. 
        The flag corresponds to the user defined severity (logging level) for the msg input.
        
        """
        
        lvl=self.log_level

        print_me=self.print_activity

        if not print_me:   

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

            print(message)


# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def write_L3_log(self,msg,where,logfile_lvl='info'):
        """
        Method to write predefined messages to the elogbook. The elogbook is defined from the user
        at the instantation of the HTadjust module. The action of writing to the elogbook can be 
        suppressed with the no_elog_write flag. The messages are also written in the local log file in case the 
        log_me flag=True in the class of HTadjust module.
        
        flag_unstable: If True, the function pushes a predefined event, written for the case of unstable measurement conditions to the elogbook and logbook.
                       If False, a predefined message for stablem easurement conditions is written in both logbooks.

        msg:           Default value of this string is empty. If not empty, the function will push this message to the logbooks. In other words, this variable overrides
                       the predefined messages explained in the previous parameter.
        
        """
        my_str=('Wrong input to log function. Choose where to log the message between' +
            '"logfile" for local logging,"logbook" for logging in the OP logbook or both with "both logs".')
            
        
        assert where in ['logfile','logbook','both logs'], my_str

        if where=='logfile':

            if self.log_me:
            
                self.logger_or_printer(message=msg,flag=logfile_lvl) 

        elif where=='logbook':

            if not self.no_elog_write: 

                elog.create_event(msg+'\n[GHOST:HTadjust]')

        else:

            if self.log_me:

                self.logger_or_printer(message=msg,flag=logfile_lvl)

            if not self.no_elog_write:

                elog.create_event(msg+'\n[GHOST:HTadjust]')



# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #
       
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

            msg=("There seems to be a problem communicating with the FEC." + 
                " No GET action is possible. Aborting.")
            
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
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
            msg='Setting %s#%s parameter to value %s.'%(my_field,param_full_name,val_to_set)
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        except:

            msg=("There seems to be a problem communicating with the FEC." + 
                " No SET action is possible. Aborting.")
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            raise ValueError(msg)    

    
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #
    
           
    def get_my_JAPC_parameter(self,device,field,parameter,my_selector=None,no_shots=10,subscribe_=1,basic_per=1.2,verbose=True):
        """
        Method to get the values of any FESA parameter via the GET method of pyjapc module.

        The inputs are:{

        device: The device name in FESA

        field:  The field name in FESA

        parameter: The parameter name in FESA

        my_selector: The PLS selector (Set None for non-ppm parameters)

        no_shots: The number of shots that the variable is measured.

        subscribe_: Logical flag for subscription (True) or not (False) to a parameter via PyJAPC

        basic_per: In case of subscribe_=False for a parameter, manual measurement is enabled, which is periodical with period basic_per.

        verbose: Flag to ctivate some additional information, while measuring a parameter.

        }

        The outputs are:{

        A dictionary with the keys 'Values'-> the vector of the measurements of length no_shots,
        'Mean'-> The average value of the 'Values' vector, 'Sigma'->The standard deviation of the 'Values' vector.

        }

        Normally the pyjapc module GET function is called to interact with 
        the parameter device/field#parameter (based on the JAPC rules)

        """
        
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
                    msg="({0}) Measured value for {1} is: {2}".format(ind_,parameterName, "%.3f"%newValue)
                    if verbose:
                        self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    ind_+=1

            japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

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
            # msg="Manual JAPC Measurement Mode: Waiting for "+str(basic_per)+" seconds for each measurement."
            # self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info',print_me=False)
            
            japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
            for k in range(no_shots):
                newValue=japc.getParam(my_constructor)
                param.append(newValue)
                msg="({0}) Measured value for {1} is: {2}".format(ind_,my_constructor, "%.3f"%newValue)
                if verbose:
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
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
        
        val_to_set: The new value to be set for the parameter device/field#parameter.
        
        lim_l, lim_r: The lower and upper limits of the value to be set. If the val_to_set value is outside this range, the SET action
        is aborted and the parameter retains its initial value.

        my_selector: The PLS selector (Set None for non-ppm parameters)
        
        }
        
        
        Normally the PyJAPC module SET function is called to interact with 
        the parameter device/field#parameter. (the name construction follows the JAPC rules)
        
        """
                
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
                msg='Setting '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            except:

                msg='Unable to set '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                raise ValueError(msg)
        
        else:

            msg=('Given value to SET is outside safe operating range (Limit->' +
                '[{0},{1}]. Aborting SET operation for {2}.').format(lim_l,lim_r,my_constructor+'#'+parameter)
            
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            

# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

        
    def wait_HTadjust_interval(self,time_knob=0):
        """
        Method to freeze the execution of the HTadjust module after the regulations on the
        HT source are performed. The freeze is performed with the sleep method of the time module.
        
        The duration of the freeze is user defined via the FESA parameter HTadjust_intervall (in minutes).
        After the pass of HTadjust_intervall minutes, the module looks for the new value of the HTadjust_kill
        parameter in the FESA class and restarts if it is allowed.

        During sleep time, the HTadjust_kill flag is checked via the method my_stopper(). 

        Inputs:

        time_knob:      If 0, the waiting time of the freeze is HTadjust_intervall minutes. If any positive integer other than 0,
                        the waiting time will be this number in seconds. E.g. if time_knob=10, the waiting interval is 10 seconds.
        
        """
        
        global HTadjust_interval

        HTadjust_interval=self.get_HTadjust('intervall') # This is in minutes !
        
        if not time_knob:

            msg='End of current iteration. Waiting for '+str(HTadjust_interval)+' minutes.'
            
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

             
            m=1
            while m<=HTadjust_interval*60:
                
                self.my_stopper(flag='',set_Vinit=True)
                sleep(1)# Input in seconds
                m+=1
            
        else:
            
            msg='End of current iteration. User defined sleep time. Waiting for {} seconds.'.format(time_knob)
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
         
            
            m=1
            while m<=time_knob:
                
                self.my_stopper(flag='',set_Vinit=True)
                sleep(1)# Input in seconds
                m+=1

        msg='Proceeding with next iteration. Acquiring new value for the HTadjust_kill flag.'
        self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

    
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

    def HT_Current_Measurements(self,shot_number):
        
        """
        *** inputs:
        {
        
        linac_current: The measurement of the linac current (dictionary)
        
        new_value_SRCVOLT: The new value to set the HT voltage.

        
        safe_volt_low___
                        |
                        -----: The low (safe_volt_low) and high (safe_volt_high) allowed values for the SET operations.
        safe_volt_high__|
        
        
        shot_number: The number of shots for the linac current measurement (see get_my_JAPC_parameter() method).
        
        
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

        status=1 

        for round_ in ['First','Second']:

            msg=round_+' round of BCT15 measurements'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            BCT15=self.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',
                                                         parameter='currentLinacSingle',
                                                         my_selector=self.BCT15_selector,
                                                         no_shots=shot_number)

            my_condition=BCT15['Sigma']>0.1*BCT15['Mean']

            if my_condition and round_=='First':

                msg='First round: Unstable conditions in the BCT15 measurements.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            elif my_condition and round_=='Second':
                msg='Second round: Unstable conditions in the BCT15 measurements.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                msg='Not possible to adjust the HT voltage. Setting the HT voltage to the initial value.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                status=0
           

            elif not my_condition:    

                
                break #EXIT the for loop

        return status,BCT15


# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def HT_Decider(self,BCT15_all,HT_start,HTadjust_vrange):


        if BCT15_all['Positive'] > BCT15_all['Start']:

            msg='Current p larger than current start.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            if BCT15_all['Positive'] > BCT15_all['Negative']:
                msg='Current p larger than current m.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start+HTadjust_vrange
                BCT15_new=BCT15_all['Positive']

            elif BCT15_all['Negative'] > BCT15_all['Start']:

                msg='Current m larger than current start.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start-HTadjust_vrange
                BCT15_new=BCT15_all['Negative']
            
            else:

                msg='Setting HT_new and BCT_new to their initial values.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start
                BCT15_new=BCT15_all['Start'] # This is not in the flowchart..should it be inside ?



        elif BCT15_all['Negative']> BCT15_all['Start']:
            msg='Current m larger than current start.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            HT_new=HT_start-HTadjust_vrange
            BCT15_new=BCT15_all['Negative']

        else:

            msg='Setting HT_new and BCT_new to their initial values.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            HT_new=HT_start
            BCT15_new=BCT15_all['Start'] # This is not in the flowchart..should it be inside ?

        return HT_new, BCT15_new

# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def my_stopper(self,flag='initial',set_Vinit=False):
        """ Function to terminate the HTadjust module by checking the HTadjust_kill flag.

            The termination of the HTadjust modulde is performed with the help of the sys.exit() function.

            When flag='initial' some useful info are printed out, for the begininning of the execution of the code.
            If flag='' there is not print out from the code and this mode is used when the function is called 
            in other places in the code. 

        """
        
        
        
        if flag=='initial':
            verbose=1
        else:
            verbose=0
        
        
        
        if verbose:
            msg='Checking HTadjust_kill flag.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        signum=self.get_HTadjust('kill')

        if signum:
            
            msg="""Terminating HTadjust module: Kill flag raised by the user."""
            self.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')

            if set_Vinit:

                msg='Setting the HT extraction voltage to the initial value. ({} V)'.format(HT_start)
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                self.set_my_JAPC_parameter(self,device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high)
            
            exit(msg)# Exit from the module
        
        else:
            
            if verbose:
                msg='HTadjust_kill checked. Running HTadjust module.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')                

            return



#                                                 MAIN FUNCTION
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #



   
    def run(self,dummy_wait_time,shot_number=10):
        """
        The main function of the HTadjust module. It executes the HTadjust module based on the user's input.
        
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
        
        global HT_start, safe_volt_low, safe_volt_high

   
        # Hard-coded values for HT voltage operation range
        safe_volt_low=19040
        safe_volt_high=19100
        

        self.start_HTadjust() # Initiate loggers, pyJAPC 

        #Infinite loop module !
        while True:


            HTadjust_interval=self.get_HTadjust('intervall') # Get HTadjust_interval

            msg='HTadjust_interval is {} minutes'.format(HTadjust_interval)
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


            self.my_stopper(flag='initial') # Check kill flag

            HTadjust_inhibit=self.get_HTadjust('inhibit')

            msg='HTadjust_inhbit is: '+str(HTadjust_inhibit)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
            HTadjust_test=self.get_HTadjust('test')

            msg='HTadjust_test is: '+str(HTadjust_inhibit)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            
            #Check inhbit flag !
            if not HTadjust_inhibit:

                #Check the status of the HT source before performing and adjustments ! 
                japc.setSelector(None)
                HT_status=japc.getParam('IP.NSRCGEN/Status#sourceHTStatus')

                if not HT_status[0]==2:
                    
                    msg=('The status of the source is {0}. ' + 
                        'Waiting for {1} minutes.').format(HT_status[1],HTadjust_interval)

                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    
                    self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                    
                    continue
                
                else:
                    msg=('The status of the source is {}. ' + 
                        'Proceeding with HTadjust operations.').format(HT_status[1])

                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    pass

                # Begin main sequence.
 

                HTadjust_vrange=self.get_HTadjust('Vrange')

                msg='The HT voltage will be adjusted within a +/- '+str(HTadjust_vrange)+' V range.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                msg='Acquiring source HT voltage.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                HT_start=self.get_my_JAPC_parameter(device="IP.NSRCGEN",
                    field="Setting",parameter='sourceHT',my_selector=None,subscribe_=0,no_shots=1)['Mean']

                msg='The source HT voltage is '+str(HT_start)+' V.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                #Do a first current measurement and examine if it is above or below the threshold

                Init_BCT=self.get_my_JAPC_parameter(device="ITF.BCT15",
                    field='Acquisition',parameter='currentLinacSingle',
                    my_selector=self.BCT15_selector,no_shots=1,subscribe_=1,verbose=False)['Mean']

                msg='Initial ion beam current measurement is {}'.format("%.3f"%Init_BCT)
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                # Is the current enough? Decide whether to proceed or not.
                if Init_BCT<0.01:
                    msg=('The measurement of the BCT15 current is below threshold (0.01 mA).' + 
                        ' Waiting for {} minutes and restarting.').format(HTadjust_interval)
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    
                    self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                    
                    continue

                else:
                    
                    msg=('The measurement of the BCT15 current is above threshold (0.01 mA). ' + 
                        'Proceeding with HTadjust operations.')
                     
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    pass


                # Start measurements

                my_keys=['Start','Positive','Negative']

                k=0 # index for my_keys array

                BCT15_all={} #initialize dictionary

                for dv in [0,HTadjust_vrange,-HTadjust_vrange]:

                    self.my_stopper(flag='',set_Vinit=True)

                    msg='Initiating BCT15 measurements for DV = {} V.'.format(dv)
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                    new_set_HTV=HT_start+dv

                    if not HTadjust_test:

                        msg='Setting the HT voltage to {} V.'.format(new_set_HTV)

                        self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        self.set_my_JAPC_parameter(device='IP.NSRCGEN',
                                                   field='Setting',parameter='sourceHT',
                                                   val_to_set=new_set_HTV,lim_l=safe_volt_low,
                                                   lim_r=safe_volt_high)
                    
                    else:

                        msg='This is a test. No SET operation on-going.'
                        self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')



                    status,BCT15=self.HT_Current_Measurements(shot_number=10)

                    msg=('Result of BCT15 measurements for adjustment DV = {0} V: ' + 
                        'Mean-> {1}, Sigma-> {2}').format(dv,"%.3f"%BCT15['Mean'],"%.3f"%BCT15['Sigma'])

                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    
                    if not status:

                        break


                    BCT15_all[my_keys[k]]=BCT15['Mean']

                    k+=1

                        

                if not status:

                    msg='Adjustments of the HT source are not possible due to unstable conditions.'
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    msg='Setting the HT source voltage to the initial value.'
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    self.set_my_JAPC_parameter(device='IP.NSRCGEN',
                           field='Setting',parameter='sourceHT',
                           val_to_set=HT_start,lim_l=safe_volt_low,
                           lim_r=safe_volt_high)



                    self.wait_HTadjust_interval(time_knob=dummy_wait_time) # GOTO the beginning of the while loop
                    
                    

                    continue


                

                #In this part we are looking for values in the pair (HT_new, BCT15_new)! :-)
                
                HT_new, BCT15_new=self.HT_Decider(BCT15_all,HT_start,HTadjust_vrange)
                
                self.my_stopper(flag='',set_Vinit=True)
                
                

                if not HTadjust_test:


                    self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',
                     parameter='sourceHT',val_to_set=HT_new,lim_l=safe_volt_low,lim_r=safe_volt_high)


                else:

                    msg=('New values for the HT adjustment acquired but ' + 
                    ' no SET operation is performed (HTadjust_test=True).')
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                msg="""HT extracting voltage [V]: {0}-->{1}, BCT15 I [mA]: {2}-->{3}""".format(HT_start,HT_new,
                    "%.3f"%BCT15_all['Start'],"%.3f"%BCT15_new)
                

                self.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')

                self.wait_HTadjust_interval(time_knob=dummy_wait_time)

                continue  #GOTO initial while loop

            else:

            # Wait for new input and restart
                msg=('Inhibition of module HTadjust: Inhibit flag raised by the user.' + 
                    'The module will resume after change of the HTadjust_inhibit flag.')

                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info') 

                self.wait_HTadjust_interval(time_knob=dummy_wait_time)
                # sleep(10) #wait 10 seconds before restarting.
                continue  #GOTO initial while loop
                


#                                                    RUN ME                                                
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

    
if __name__ == "__main__":
        
    HT_object=HTadjust(simulate_SET=True, sourceHT_selector=None,
                       BCT15_selector='LEI.USER.ALL',
                       which_ebook='LINAC 3',no_elog_write=False,log_me=True,log_level='INFO',
                       print_activity=False) 
                       #Roll back to Simulation mode with simulate_SET=True ; For L3 elog write : which_ebook='LINAC 3'  


    HT_object.run(dummy_wait_time=0,shot_number=10) # Run HTadjust module.