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


class OvenRestart(object):
    """
    The OvenRestart module is a single-passage module which can be  used for restarting oven 1 and 2 of the Ion Source at Linac 3, separately or simultaneously.

    The implementation of the code is based on the OvenRestart flow-chart from D. Kuchler:https://edms.cern.ch/document/2000941.

    Interaction with code is performed via the GHOST FESA class. 

    
    """
        
    
    
    def __init__(self,FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='OvenRestart',
                 simulate_SET=True,INCA_ACCEL='LEIR',Oven_FESA_selector=None,
                 OvenResistance_selector='LEI.USER.ALL',OvenPower_wait=60,OvenIncrPower_wait=20,Pressure_wait=5,Pressure_limit=1e-6,which_ebook='LINAC 3',
                 no_elog_write=False,log_me=True,log_level='DEBUG'):
        """
        Initialisation of the OvenRestart module. The input parameters are:
        
        FESA_GHOST_Device: (default:GHOSTconfig): The device of the GHOST module in the appropriate FESA class.
        
        FESA_GHOST_Property: (default:OvenRestart): The property of the GHOST module in the appropriate FESA class.
        
        simulate_SET:(default:True): Run the OvenRestart module in simulation mode i.e. without actually adjusting any 
        of the parameters.
        
        INCA_ACCEL:(default:LEIR): The INCA accelerator.
        
        Oven_FESA_selector:(default:None): The selector for interacting with the oven power parameter.
        
        OvenResistance_selector:(default:'LEI.USER.ALL'):The selector for interacting with the resistance parameter, which is a PPM parameter.

        OvenPower_wait: (default:60): The waiting time after setting the power at the oven, in minutes.

        OvenIncrPower_wait: (default:20): The waiting time after increasing in small steps the power at the oven, in minutes.

        Pressure_wait: (default:5): The waiting time before rechecking the pressure at the ovens.the

        Pressure_limit:(default:1e-6): The limit of the pressure value. If the pressure is smaller than this value, it means that the outgassing has been completed.
        
        which_ebook:(default:'LINAC 3'): The elogbook to push events from the elogbook module.
        
        no_elog_write:(default:False): Flag to suppress pushing events to the elogbook
        
        log_me:(default:True): Flag to initiate the logger module for the local log system.
        
        log_level:(default:'DEBUG'): The level of logging for the local log system.
        
        
        
        
        
        """
        
        self.FESA_GHOST_Device=FESA_GHOST_Device

        self.FESA_GHOST_Property=FESA_GHOST_Property 
        
        self.simulate_SET=simulate_SET

        self.Oven_FESA_selector=Oven_FESA_selector
        
        self.OvenResistance_selector=OvenResistance_selector

        self.OvenPower_wait=OvenPower_wait

        self.OvenIncrPower_wait=OvenIncrPower_wait

        self.Pressure_wait=Pressure_wait

        self.Pressure_limit=Pressure_limit
        
        self.INCA_ACCEL=INCA_ACCEL
        
        self.which_ebook=which_ebook
        
        self.log_level=log_level
        
        self.no_elog_write=no_elog_write
        
        self.log_me=log_me
        
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        
        self.__version__='v.0.1'
        
    
        
    def my_stopper(self,flag='initial'):
        """ Function to terminate the OvenRestart module by checking the OvenRestart_kill flag.

            The termination of the OvenRestart modulde is performed with the help of the sys.exit() function.

            When flag='initial' some useful info are printed out, for the begininning of the execution of the code.
            If flag='' there is not print out from the code and this mode is used when the function is called 
            in other places in the code. 

        """
        
        
        
        if flag=='initial':
            verbose=1
        else:
            verbose=0
        
        
        
        if verbose:
            msg='Checking OvenRestart_kill flag.\n'
            self.logger_or_printer(message=msg,flag='info')

        signum=self.get_OvenRestart('kill')

        if signum:
            
            msg='Terminating OvenRestart module: Kill flag raised by the user.\n'
            self.logger_or_printer(message=msg,flag='info')
            self.write_L3_logbook(msg=msg)
            
            exit(msg)
        
        else:
            
            if verbose:
                msg='OvenRestart_kill checked. Running OvenRestart module.\n'
                self.logger_or_printer(message=msg,flag='info')
                self.write_L3_logbook(msg=msg)
                

            return
        
        
        
    def initiate_JAPC(self,log=50):
        """Initialisation of the pyJAPC module. The class arguments are passed in the pyjapc module as:
        pyjapc.PyJapc(selector=ourceHT_selector,
                           incaAcceleratorName=INCA_ACCEL,noSet=simulate_SET) 
        """

        global japc
        japc=pyjapc.PyJapc(selector=self.Oven_FESA_selector,
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
        Initialisation of the logging system. The Python logging module is used. The class argument of self.log_level,
        is passed  in the logging module and the default directory of the log files is in ../log. Each log file
        is unique, with a distinct time stamp.
        
        """
        if self.log_me:

            global logger
            ttl='{:%Y-%m-%d_%H_%M_%S}'.format(datetime.datetime.now())
            dir_='../log/'
            file_name=dir_+'OvenRestart_'+ttl+'.log'
            # Create logger
            logger = logging.getLogger('OvenRestart')
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
        Function to switch between logging or print mode, according to the OvenRestart module initialization parameter log_me.
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
            print('Log of OvenRestart activity suppressed by the user. Message: '+message)

                
    def get_OvenRestart(self,OvenRestart_input):
        
        """
        Method to get the values of the OvenRestart parameters in the GHOST FESA class via the GET method of pyjapc module.
        The input OvenRestart_input (string) can be only the keywords kill, inhibit, test, Vrange, intervall
        which correspond to the OvenRestart_kill and OvenRestart_inhibit parameters.
        
        """

        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        valid_params=japc.getParamInfo(my_field)
        param_full_name='OvenRestart_'+OvenRestart_input

        try:

            OvenRestart_param=japc.getParam(my_field+'#'+param_full_name)
            return OvenRestart_param

        except:

            msg='There seems to be a problem communicating with the FEC. No GET action is possible. Aborting.\n'
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
            #msg="Manual JAPC Measurement Mode: Waiting for "+str(basic_per)+" seconds for each measurement.\n"
            msg="Manual JAPC Measuremet.\n"
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
        
        val_to_set: The new value to be set for the parameter device/field#parameter.
        
        lim_l, lim_r: The lower and upper limits of the value to be set. If the val_to_set value is outside this range, the SET action
        is aborted and the parameter retains its initial value.

        my_selector: The PLS selector (Set None for non-ppm parameters)
        
        }
        
        
        Normally the PyJAPC module SET function is called to interact with 
        the parameter device/field#parameter. (the name construction follows the JAPC rules)
        
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
            
            
                

                    
         
        
    
    def write_L3_logbook(self,msg):
        """
        Method to write predefined messages to the elogbook. The elogbook is defined from the user
        at the instantation of the OvenRestart module. The action of writing to the elogbook can be 
        suppressed with the no_elog_write flag. The messages are also written in the local log file in case the 
        log_me flag=True in the class of OvenRestart module.
        


        msg:           The message to be passed in pylogbook and issued on the selected elogbook
        

        """


        
        if not self.no_elog_write: 
        
            elog.create_event(msg+'\n[GHOST:OvenRestart]')
            
            if self.log_me:
                msg2='New entry in eLogBook: '+msg+'.\n'
            
                self.logger_or_printer(message=msg2,flag='info')

        else:

            if self.log_me:
                m1='E-log activity suppressed :\n'
                self.logger_or_printer(m1, flag='info')
                self.logger_or_printer(msg, flag='info')



        
    def wait_OvenRestart_interval(self,time_knob):
        """
        Method to freeze the execution of the OvenRestart module. The freeze is performed with the sleep method of the time module.
        
        The duration of the freeze is user defined and should be registered at the creation of the OvenRestart object.


        During sleep time, the OvenRestart_kill flag is checked via the method my_stopper(). 

        Inputs:

        time_knob:      If any positive integer other than 0,the waiting time will be this number in minutes. E.g. if time_knob=10, the waiting interval is 10 minutes.
        
        """
        

        assert time_knob>0,"Please give a positive and finite waiting time."
        
        m=1
        while m<=time_knob*60:
            
            self.my_stopper(flag='')
            sleep(1)# Input in seconds
            m+=1
        
    
    
    def pressure_checker(self):
        """
        Method to check the pressure at LINAC3.
        """

        time_wait=self.Pressure_wait

        assert time_wait>0,"Please give a positive and finite waiting time."

        P=japc.getParam('IP.VGP2/PR')

        msg='The pressure is {} mbar.\n'.format("%.2E"%P)
        self.logger_or_printer(message=msg,flag='info')

        while P >= self.Pressure_limit:

            msg='Pressure is larger than {0} mbar. Cannot proceed. Waiting for {1} minutes before next measurement.\n'.format(self.Pressure_limit,time_wait)
            self.logger_or_printer(message=msg,flag='info')
            self.write_L3_logbook(msg=msg+'[GHOST:OvenRestart]')

            # Wait for 5 minutes
            self.wait_OvenRestart_interval(time_knob=time_wait)
            # Re-check pressure
            P=japc.getParam('IP.VGP2/PR')
    
    def which_combo(self):
        """
        A method which produces indexes and a list with the oven numbers, which correspond to the oven that is selected.
       
        """

        if Oven_choice==1 or Oven_choice==2:
            left=Oven_choice-1
            right=Oven_choice
            which_oven=[Oven_choice]
        elif Oven_choice==3:
            left=0
            right=2
            which_oven=[1,2]
        else:
            raise ValueError('Wrong input for Oven_choice. Choose 1,2 or 3.')

        return left,right,which_oven
   
    def read_power(self):
        """
        Method to read the Power of the ovens.
        """

        left,right,which_oven=self.which_combo()

        japc.setSelector(None)

        oven_power=japc.getParam(['IP.NSRCGEN/Setting#oven1Power','IP.NSRCGEN/Setting#oven2Power'])[left:right]
        m=0
        for powpow in oven_power:
            msg='The power of oven {0} is measured to be {1} W.\n '.format(which_oven[m],"%.2f"%powpow)
            self.logger_or_printer(message=msg,flag='info')
            m+=1

        return oven_power

    def read_resistance(self):
        """
        Method to read the resistance of the ovens.
        
        """

        if Oven_choice==1 or Oven_choice==2:

            res=[self.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven'+str(Oven_choice)+'AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean']]
            which_oven=[Oven_choice]

        elif Oven_choice==3:

            res=[self.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven1AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean'],
            self.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven2AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean']]
            which_oven=[1,2]

        m=0
        for r in res:
            msg='The resistance of oven {0} is measured to be {1} Ohms.\n '.format(which_oven[m],"%.2f"%r)
            self.logger_or_printer(message=msg,flag='info')
            m+=1

        return res

        


    def run(self):
        """
        The main function of the OvenRestart module. It executes the OvenRestart module based on the user's input.
        
        
        *** Description (N.B.: All operations are recorded in the elogbook and the local log) :
        
        {
            Initially, the programm initiates pyjapc, elogbook and the local logger. 
            Then it looks for the variables OvenRestart_kill, OvenRestart_inhibit.
            
            {
            
            In case OvenRestart_kill=True, the program is not executed.
                
                {
                
                In case OvenRestart_inhibit=True, the program is not executed.
                
                    {
                        If the program is finally executed, it performs a check of the oven selection parameter.
                        If this patameter is 1, then oven 1 is selected, if 2 then oven 2 is selected, if 3 both
                        ovens are selected. Note that in this scenario, both of the ovens should be in parallel (similar)
                        states (e.g. both powered on or off, both having a resistance which is in the operational range.)
            
                        
                        The Oven_status  is checked then and if the status is ON the code continues.  
                        
                        The Oven_power parameter is then measured and the code proceeds if the power is not finite, i.e. only if the oven is not powered on.

                        In the next step, the pressure at LINAC 3 is checked. If it is smaller than a predefined value (usually 1e-6) the code continues.

                        If the outgassing is completed, the Oven power is set to 2 Watts. Then the code freezes for 60 minutes in order for the system
                        to reach an equilibrium. 

                        Next, the pressure is remeasured and if the code is allowed to continue, it will measure also the resistance value at the oven.

                        If the resistance value is between the operational range, usually (0.5,5 Ohms) the code will continue with the oven restart procedure.

                        As a next step, the code will increase the oven by 0.5 Watts. It will wait for 20 minutes and then it will continue with the pressure and 
                        resistance measurements. The increase of the oven power in 0.5 W steps, allong with the checks of pressure and resistance,
                         will continue until the oven power reaches a value which is larger than 5 Watts.
                        
                        
                    }
                
                }
            }
        
        
        
        
        }
        """
        
        
        

        self.initiate_logger()   
        self.initiate_JAPC()# Change pseudo_set to False to escape simulation mode for SET action
        self.initiate_elogbook() # Currently issuing on LINAC3 logbook
        

        if self.simulate_SET:

            msg='******Initiating OvenRestart module in Simulation Mode. No SET operations will be performed******\n'
            self.logger_or_printer(message=msg,flag='info')
            self.write_L3_logbook(msg=msg)

        else:

            msg='******Initiating OvenRestart module.******\n'
            self.logger_or_printer(message=msg,flag='info')
            self.write_L3_logbook(msg=msg)



        msg='Initiating JAPC, E-Logbook and OvenRestart logger.\n'
        self.logger_or_printer(message=msg,flag='debug')
   
        self.my_stopper(flag='initial') # Check OvenRestart_kill flag


        

        #Single-passage module !


        msg='Acquiring OvenRestart_inhibit.\n'
        self.logger_or_printer(msg,flag='debug')

        OvenRestart_inhibit=self.get_OvenRestart('inhibit')

        msg='The inhibit flag is: '+str(OvenRestart_inhibit)+'.\n'
        self.logger_or_printer(message=msg,flag='info')
        Oven_choice=self.get_OvenRestart('oven')
    
        
        #Check inhbit flag !
        if not OvenRestart_inhibit:

            Oven_choice=get_OvenRestart('oven')

            #Check the status of the Oven ! 

            if Oven_choice==1 or Oven_choice==2:

                Oven_status=japc.getParam('IP.NSRCGEN/Status#oven'+str(Oven_choice)+'Status')[1]
                which_oven=[Oven_choice]
                msg='Oven {} is selected for restart.\n'.format(Oven_choice)
                self.logger_or_printer(message=msg,flag='info')
                self.write_L3_logbook(msg=msg)

            elif Oven_choice==3:

                Oven_both_status=[item[0] for item in japc.getParam(['IP.NSRCGEN/Status#oven1Status','IP.NSRCGEN/Status#oven2Status'])]
                which_oven=[1,2]
                msg='Ovens 1 and 2 are selected for restart.\n'
                self.logger_or_printer(message=msg,flag='info')
                self.write_L3_logbook(msg=msg)

                if sum(Oven_both_status)==4:
                    Oven_status='ON'
                else:
                    Oven_status='OFF' #if one of the ovens is OFF in the oven selector 3 case, then do not proceed with operations.
            else:
                raise ValueError('Wrong choice of oven. Please select 1,2,3 in the OvenRestart_oven parameter in the FESA class.')


            if Oven_status=='ON':

                msg="The status of the oven {0} is {1}. Proceeding with the reading of the oven power.\n".format(which_oven,Oven_status)
                self.logger_or_printer(message=msg,flag='info')


                #Get oven power
                Oven_power=self.read_power()
                
                #Make sure it is not larger than 0 
                if not all(Oven_power):

                    msg='Oven does not appear to be powered on. Proceeding with OvenRestart module operations.\n'
                    self.logger_or_printer(message=msg,flag='info')

                    #Get the pressure. Wait 5 minutes for each measurement of the pressure, until it is above threshold.

                    self.pressure_checker()

                    msg='Pressure is larger than 1e-6 mbar. Proceeding with resistance reading from oven {}.\n'.format(which_oven)
                    self.logger_or_printer(message=msg,flag='info')
                        

                    msg='Setting power of oven {0} to 2 W.\n'.format(which_oven)
                    self.logger_or_printer(message=msg,flag='info')

                    set_oven_power=2.0 #in Watts

                    for ov in which_oven:
                        self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='oven'+str(ov)+'Power',
                            val_to_set=set_oven_power,lim_l=0.0,lim_r=10.0,my_selector=None)

                    msg='The power of the oven {} is set. Waiting for 60 minutes.\n'.format(which_oven)
                    self.logger_or_printer(message=msg,flag='info')

                    #wait for 60 minutes
                    time_wait=self.OvenPower_wait
                    self.wait_OvenRestart_interval(time_knob=time_wait)

                    msg='{} minutes have passed. Continuing with pressure measurement.\n'.format(time_wait)
                    self.logger_or_printer(message=msg,flag='info')

                    #check pressure for second time. Wait 5 minutes for each measurement of the pressure, until it is above threshold.

                    self.pressure_checker()

                    msg='Pressure is smaller than {0} mbar. Proceeding with resistance reading from oven {1}.\n'.format(self.Pressure_limit,which_oven)
                    self.logger_or_printer(message=msg,flag='info')

                    R=self.read_resistance()

                    msg='The resistance of oven {0} is measured to be {1} Ohms.\n'.format(Oven_choice,R)

                    self.logger_or_printer(message=msg,flag='info')


                    if all(np.asarray(R)>0.5) and all(np.asarray(R)<5.0):

                        go_up=0.5



                        while True:

                            
                            msg='Power of oven {0} is {1} W. Increasing power by {2} W.\n'.format(which_oven,set_oven_power,go_up)
                            self.logger_or_printer(message=msg,flag='info')


                            #increase the oven power

                            set_oven_power+=go_up

                            for ov in which_oven:

                                self.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',parameter='oven'+str(ov)+'Power',val_to_set=set_oven_power,lim_l=0.0,lim_r=10.0,my_selector=None)



                            #wait for 20 minutes

                            time_wait=self.OvenIncrPower_wait
                            msg='Oven {0} power increased by {1} W. Waiting for {2} minutes.\n'.format(which_oven,go_up,time_wait)
                            self.logger_or_printer(message=msg,flag='info')

                            self.wait_OvenRestart_interval(time_knob=time_wait)

                            msg='{0} minutes have passed. Proceeding with pressure measurement.\n'.format(time_wait)

                            self.pressure_checker()

                            msg='Pressure is smaller than {0} mbar. Proceeding with resistance reading from oven {1}.\n'.format(self.Pressure_limit,which_oven)
                            self.logger_or_printer(message=msg,flag='info')

                            

                            R=self.read_resistance()


                            if all(np.asarray(R)>0.5) and all(np.asarray(R)<5.0):

                                msg='Checking if oven {0} is larger than 5.0 W.\n'.format(which_oven)

                                Oven_power=self.read_power()

                                if all(np.array(Oven_power)>=5.0):
                                    m=0
                                    for it in which_oven:

                                        msg='Final power measurement of oven {0} is {1} W.\n'.format(it,"%.2f"%Oven_power[m])
                                        self.logger_or_printer(message=msg,flag='info')
                                        self.write_L3_logbook(msg=msg)
                                        m+=1

                                    msg="OvenRestart module finished with success. Goodbye! :-)"
                                    self.write_L3_logbook(msg)
                                    self.logger_or_printer(message=msg,flag='info')

                                    break #exit from the while loop

                                else:

                                    m=0

                                    for it in which_oven:
                                        msg='Final power measurement of oven {0} is {1} W.\n'.format(it,"%.2f"%Oven_power[m])
                                        self.logger_or_printer(message=msg,flag='info')
       
                                    continue #continue in the while loop.


                            else:

                                msg='Cannot proceed with OvenRestart operations due to resistance value outside operation range (0.5,5) Ohms. Exiting.\n'
                                self.logger_or_printer(message=msg,flag='info')
                                break # exit while loop

                    else:

                        msg='Resistance value outside operation range (0.5,5) Ohms. Aborting OvenRestart module operations. Exiting.\n'
                        self.logger_or_printer(message=msg,flag='info')
                        self.write_L3_logbook(msg=msg)                            

                else:

                    msg='Oven {} appears to be already powered on. Aborting OvenRestart module operations. Exiting.\n'.format(Oven_choice)
                    self.logger_or_printer(message=msg,flag='info')
                    self.write_L3_logbook(msg=msg)



            else:

                msg="The status of the oven {0} is {1}. Aborting OvenRestart module operations. Exiting.\n".format(Oven_choice,Oven_status)
                self.logger_or_printer(message=msg,flag='info')
                self.write_L3_logbook(msg=msg) 

        else:


            # Wait for new input and restart
            msg='Inhibition of module OvenRestart: Inhibit flag raised by the user. Exiting.\n'
            self.logger_or_printer(message=msg,flag='info')
            self.write_L3_logbook(msg=msg) 


            
                
    
if __name__ == "__main__":
        
    OR_object=OvenRestart(simulate_SET=False,INCA_ACCEL='LEIR',Oven_FESA_selector=None,
                 OvenResistance_selector='LEI.USER.ALL',OvenPower_wait=60,
                 OvenIncrPower_wait=20,Pressure_limit=1e-6,Pressure_wait=5,which_ebook='LINAC 3',
                 no_elog_write=False,log_me=True,log_level='INFO') # # Roll back to SET mode with simulat_SET=True    
    OR_object.run() # Run OvenRestart module.



