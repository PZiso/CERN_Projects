# For some simple calculations
import numpy as np

#PyJAPC for getting & setting FESA parameters
import pyjapc
 
#Timber logs
import pytimber

# Time module for sleeping
from time import sleep

#PyLogBook to push events to the eLogbook
import pylogbook

#Logging for keeping up with the flow...
import logging.handlers

#Data manipulation
import pandas as pd

# For logging with time-stamp
import datetime

#Sys.exit needed for killing the module
from sys import exit

# For string search
import re


#Plotting

import matplotlib.pylab as plt

#Send emails

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class GHOST():


    def __init__(self,mod_name,FESA_GHOST_Property,
             simulate_SET,INCA_ACCEL='LEIR',FESA_GHOST_Device='GHOSTconfig',japc_selector=None,
             which_ebook='TESTS',no_elog_write=False,log_me=True,log_level='DEBUG',dir_logging=''):

        self.mod_name=mod_name
        self.FESA_GHOST_Device=FESA_GHOST_Device
        self.FESA_GHOST_Property=FESA_GHOST_Property
        self.simulate_SET=simulate_SET
        self.INCA_ACCEL=INCA_ACCEL
        self.japc_selector=japc_selector
        self.which_ebook=which_ebook
        self.no_elog_write=no_elog_write
        self.log_me=log_me
        self.log_level=log_level
        self.dir_logging=dir_logging




    #                                              FUNCTION DEFINITIONS 
    # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* 

    def initiate_JAPC(self,log=50):
            """

            Initialisation of the pyJAPC module. 

            Input:

            log : (default 50): The log level of the pyjapc module.


            """

            
            japc=pyjapc.PyJapc(selector=self.japc_selector,
                               incaAcceleratorName=self.INCA_ACCEL,noSet=self.simulate_SET,logLevel=log) 
        
            self.japc=japc

    # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* 

    def initiate_elogbook(self):
        """
        Initialisation of the elogbook module. 

        Note that due to a bug of elogbook, each time a check of its functionality is performed via logging to logbook "TESTS".
        
        """

        assert self.which_ebook in ['LINAC 3','TESTS'], 'Wrong choice of logbook. Choose between "LINAC 3" and "TESTS"'

        def elog_checker():
            
            elog_temp=pylogbook.eLogbook('TESTS')

            try:

                elog_temp.create_event('Testing elogbook functionality.')

            except:

                self.no_elog_write=True

                msg=('Cannot push events to '+self.which_ebook+' logbook. ' + 
                    ' Failed to initiate PyLogbook module. Reverting to local logging only.')
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


        elog_checker()

        elog=pylogbook.eLogbook(self.which_ebook)

        self.elog=elog

    # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* 

    def initiate_logger(self):
        """
        Initialisation of the local logging system. 

        The Python logger is used and the handler automatically opens a new log file at midnight. The logger's name is defined 
        by the name of the class of the corresponding module.

        The directory of the log files must be set in the initialization of the object. (self.dir_logging)

        If the object parameter "log_me" is False, then the logger is not constructed.
        
        """
        if self.log_me:


            # Set Logger and create its handler


            lvl=logging.getLevelName(self.log_level)

            
            ttl='{:%Y-%m-%d_%H_%M_%S}'.format(datetime.datetime.now())
            dir_=self.dir_logging
            file_name=dir_+self.mod_name+'_'+ttl+'.log'
            print(file_name)
            # Create logger
            logger = logging.getLogger(self.mod_name)
            
            logger.setLevel(lvl)

            #handler_logfile=logging.FileHandler(file_name,mode='w')

            # Create formatter and add it to the handler
            
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            #handler_logfile.setFormatter(formatter)

            #Create funky Midnight roller

            handler_rot = logging.handlers.TimedRotatingFileHandler(file_name,
                                     when="midnight",
                                     interval=1,
                                     backupCount=0)# At midnight the Dracula comes out and at the same time,
                                     # our bud here will change the log file name by appending the new date.
            
            handler_rot.setFormatter(formatter)
            
            logger.handlers = [handler_rot]

            self.logger=logger
        
        else:

            self.logger=[]

        # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* 


        
    def logger_or_printer(self,message,flag):

        """
        Function to switch between local logging or shell printing mode, according to the object initialization parameter log_me.
        
        Input:

        message: The message (string) to be passed to the logger.

        flag: Parameter (string) which corresponds to the user defined severity (logging level) for the msg input.



        Note that this method is designed to log only messages which correspond to the oblect parameted "log_level" and the flag input.

        For example, if flag='debug' and theu ser has initialised the module with log_level='info', the logger will not log anything.log

        But if flag='info', the message will be logged.
        
        """
        
        lvl=self.log_level

        if self.log_me:   

            if (lvl=='INFO') and (flag=='info'):
                self.logger.info(message)
            elif (lvl=='DEBUG') and (flag=='debug'):
                self.logger.debug(message)
            elif (lvl=='WARNING') and (flag=='warning'):
                self.logger.warning(message)
            elif (lvl=='ERROR') and (flag=='error'):
                self.logger.error(message)
            elif (lvl=='CRITICAL') and (flag=='critical'):
                self.logger.critical(message)

        else:

            print('Attention:Local logging is suppresed: '+message)



    # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def write_L3_log(self,msg,where,logfile_lvl='info'):
        """
        
        Log messages to local logfile, logbook or both.

        Input:

        msg: (string): Them essage to be logged.logfile_lvl

        where: (string): The location for the logging ('logbook', 'logfile' or 'both logs')

        logfile_lvl : (string): The level for the logging. (see logger_or_printer() for more info)

        Note that logging operations are controlled form the iniatialisation of the object with the parameters

        no_elog_write (for the logbook) and log_me (for the local logging).


        """
        my_str=('Wrong input to log function. Choose where to log the message between' +
            '"logfile" for local logging,"logbook" for logging in the OP logbook or both with "both logs".')
            
        
        assert where in ['logfile','logbook','both logs'], my_str

        if where=='logfile':
            
            self.logger_or_printer(message=msg,flag=logfile_lvl) 

        elif where=='logbook':

            if not self.no_elog_write: 
                msg=(msg+' [GHOST: {}]').format(self.mod_name)
                self.elog.create_event(msg)

        else:

            self.logger_or_printer(message=msg,flag=logfile_lvl)

            if not self.no_elog_write:
                msg=(msg+' [GHOST: {}]').format(self.mod_name)
                self.elog.create_event(msg)

    # *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def start_module(self):


        """
        Method to initialize PyJAPC and the loggers.

        """

        global logger,japc,elog


        self.initiate_logger()   

        self.initiate_JAPC()# Change pseudo_set to False to escape simulation mode for SET action
       
        self.initiate_elogbook() # which_ebook: LINAC 3  


        if self.simulate_SET:

            msg=('******Initiating {} module in Simulation Mode.' +
            'No SET operations will be performed******').format(self.mod_name)

        else:

            msg='******Initiating {} module.******'.format(self.mod_name)

        
        self.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')

     
       
    def string_found(self,string1, string2):
        
       if re.search(r"\b" + re.escape(string1) + r"\b", string2):
          return True
       return False 


    def get_FESA_param(self,param_request):
        
        """
        Method to get the values of the dedicated FESA parameters that control each module, via the GET method of pyjapc module.

        Input:

        param_request:(string): The parameter to be fetched from FESA. Only the description part of each parameter is accepted in this parameter. 

                                Each FESA parameter is named with the naming rule $Module_name+'_'+$parameter.

                                For example, the kill flag of HTadjust is HTadjust_kill. In order to fetch the value of this parameter, param_request should be

                                'kill' 
        
        """
        
        

        my_field=self.FESA_GHOST_Device+'/'+self.FESA_GHOST_Property
        
        my_list=self.japc.getParamInfo(my_field)
        
        my_inquiry=my_field+'#'+self.mod_name+'_'+param_request
        
        assert self.string_found(my_inquiry,my_list),'Wrong name of FESA parameter: {}'.format(param_request)
        
        my_param=[]

        while len(my_param)==0:
            

            try:

                my_param=[self.japc.getParam(my_inquiry)]

                

            except:

                msg=("There seems to be a problem communicating with the FEC." + 
                    " No GET action is possible. Rechecking in 5 minutes.").format(self.mod_name)
                
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                
                sleep(5*60)

                


        return my_param[0]





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

            self.japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            self.japc.subscribeParam(my_constructor, newValueCallback, getHeader=True)
            self.japc.startSubscriptions()

            while True:

                if ind_<=no_shots:
                    continue
                else:
                    self.japc.stopSubscriptions()
                    self.japc.clearSubscriptions()
                    break
            param=param[:no_shots]


            
        else:
            
            param=[]
            ind_=1
            # msg="Manual JAPC Measurement Mode: Waiting for "+str(basic_per)+" seconds for each measurement."
            # cmn.write_L3_log(msg=msg,where='logfile',logfile_lvl='info',print_me=False)
            
            self.japc.setSelector(my_selector)
            msg=my_constructor+' measurement: Assigning selector-> '+str(my_selector)+'.'
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
            for k in range(no_shots):
                newValue=self.japc.getParam(my_constructor)
                param.append(newValue)
                msg="({0}) Measured value for {1} is: {2}".format(ind_,my_constructor, "%.3f"%newValue)
                if verbose:
                    self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                sleep(basic_per)
                ind_+=1
                self.japc.stopSubscriptions()
                self.japc.clearSubscriptions()
        
        
        return {'Values':param,'Mean':np.mean(param),'Sigma':np.std(param)}






# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* # 
    

    def set_my_JAPC_parameter(self,device,field,parameter,my_selector,val_to_set,lim_l,lim_r):
        
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
        self.japc.setSelector(my_selector)
        dic_FESA=self.japc.getParam(my_constructor)
        temp={}

        for key,item in dic_FESA.items():

            if not (('_min' in key ) or ('_max' in key)):
                temp[key]=item
        
        dic_FESA=temp
        
        if float(val_to_set)>=float(lim_l) and float(val_to_set)<=float(lim_r):
              
            dic_FESA[parameter]=float(val_to_set)
            
            try:
            
                self.japc.setParam(my_constructor,dic_FESA)
                msg='Setting '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                
                return True

            except:

                msg='Unable to set '+my_constructor+'#'+parameter+' parameter to value '+str(val_to_set)+'.'
                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                
                raise ValueError(msg)
        
        else:

            msg=('Given value to SET is outside safe operating range (Limit->' +
                '[{0},{1}]. Aborting SET operation for {2}.').format(lim_l,lim_r,my_constructor+'#'+parameter)
            
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
            return False
            

# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

        
    def wait_time_interval(self,FESA_time,set_init,device='',field='',parameter='',
    val_to_set=0,lim_l=-1,lim_r=1,user_time=0):#time_interval in minutes!
        """
        Method to freeze the execution of the a module for a user defined time interval. 

        The freeze is performed with the sleep method of the time module.
        

        During sleep time, the module kill flag is checked via my_stopper(). 

        Inputs:

        FESA_time: (int): The FESA parameter for the control of the sleeping time. (usually in minutes) 

        set_init: (boolean): Flag to impose roll-back to the initial configuration of any FESA parameter, if the
                             kill flag is executed from the user

        
        The following inputs are needed for my_stopper() method:

            device: (string): The device name in FESA
            
            field: (string): The field name in FESA
            
            parameter: (string): The parameter name in FESA
            
            val_to_set: (float): The new value to be set for the parameter device/field#parameter.
            
            lim_l, lim_r: (float): The lower and upper limits of the value to be set. If the val_to_set value is outside this range, the SET action
            is aborted and the parameter retains its initial value.

        user_time: (float) : If other than zero, the FESA_time is overriden and the module freezes for a time interval of user_time seconds.


        
        """
        

               
        if not user_time:

            msg='End of current iteration. Waiting for '+str(FESA_time)+' minutes.'
            
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

             
            m=1

            while m<=FESA_time*60:
                
                self.my_stopper(flag='',set_init=set_init,
                    device=device,field=field,parameter=parameter,val_to_set=val_to_set,lim_l=lim_l,lim_r=lim_r)
                sleep(1)# Input in seconds
                m+=1
            
        else:
            
            msg='End of current iteration. User defined sleep time. Waiting for {} seconds.'\
                                                                                .format(user_time)
            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
         
            
            m=1
            while m<=user_time:
                
                self.my_stopper(flag='',set_init=set_init,
                    device=device,field=field,parameter=parameter,val_to_set=val_to_set,lim_l=lim_l,lim_r=lim_r)
                sleep(1)# Input in seconds
                m+=1

        msg='Proceeding with next iteration of the module.'

        self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')





# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def my_stopper(self,flag,set_init,device='',field='',parameter='',val_to_set=0,lim_l=-1,lim_r=1):
        """ Function to terminate the  module by checking the kill flag.

            The termination of the module is performed with the help of the sys.exit() function.
            
            Input:

            flag:(string): When flag='initial' some useful info are logged. If flag='' there is not print out from the code.

            device: (string): The device name in FESA
            
            field: (string): The field name in FESA
            
            parameter: (string): The parameter name in FESA
            
            val_to_set: (float): The new value to be set for the parameter device/field#parameter.
            
            lim_l, lim_r: (float): The lower and upper limits of the value to be set. If the val_to_set value is outside this range, the SET action
            is aborted and the parameter retains its initial value.



        """
        
        if set_init:
            assert val_to_set,"Wrong input in my_stopper(). Set_init parameter is True but val_to_set is 0."
        
        
        mod_name=self.mod_name
        
        
        if flag=='initial':

            msg='Checking {}_kill flag.'.format(mod_name)

            self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        
        signum=self.get_FESA_param('kill')

        if signum:
            
            msg="""Terminating {} module: Kill flag raised by the user.""".format(mod_name)
            self.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')

            if set_init:

                self.set_my_JAPC_parameter(device=device,field=field,parameter=parameter,
                val_to_set=val_to_set,lim_l=lim_l,lim_r=lim_r)
            
            exit(msg)# Exit from the module
        
        else:
            
            if flag=='initial':

                msg='{}_kill checked. Running {} module.'.format(mod_name,mod_name)

                self.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')                

            return
        
    def read_timber(self,scale,offset,observable=['IP.NSRCGEN:SOURCEHTAQNI'],plot_me=True,pickle_me=False,ax_obj=None):
                
         if scale=='hours':
                delta=datetime.timedelta(hours=offset)
         elif scale=='minutes':
                delta=datetime.timedelta(minutes=offset)
         elif scale=='days':
                delta=datetime.timedelta(days=offset)
         else:
                raise NameError('Wrong input for datetime conversion. Choose between "days","hours","minutes"')
            
            
            
         assert offset>=0,"Please provide a finite positive offset."
        
         t1 = datetime.datetime.now() - delta
        
         t2 = datetime.datetime.now()
        
         
         
         db=pytimber.LoggingDB()
        
         data=db.get(observable,t1,t2)[observable[0]]
         
         
         calendar=[pytimber.dumpdate(ts) for ts in data[0]]
         
         df=pd.DataFrame(index=calendar,columns=observable)
         
         for obs in observable:
             
             data=db.get(obs,t1,t2)[obs]
             numeric=data[1]
             df[obs]=numeric
             
        
         
        
         if pickle_me:
             df.to_pickle(calendar[-1]+'.pickle')
             
         if plot_me:
             
             df.plot(ax=ax_obj, marker='')
             plt.show()
             
         return df


    def send_email(self,sender='pzisopou@cern.ch',recipient='pzisopou@cern.ch',password='*************'):
        
        # create message object instance
        msg = MIMEMultipart()
         
         
        message = "Hello Detlef,\n\nThe module has finished with success :-).\n\nBest regards,\n\nGHOST"
         
        # setup the parameters of the message
        
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = "[GHOST:{}]".format(self.mod_name)
         
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
         
        #create server
        server = smtplib.SMTP('smtp.cern.ch: 587')
         
        server.starttls()
         
        # Login Credentials for sending the mail
        server.login(msg['From'], password)
         
         
        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())
         
        server.quit()
         
        print("Successfully sent email to {}".format(msg['To']))

        
        
if __name__=='__main__':
    
   my_log_dir='/user/ln3op/GHOST/HTadjust/log/' 
   myGT=GHOST(mod_name='HTadjust',FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='HTadjust',
               simulate_SET=True,INCA_ACCEL='LEIR',japc_selector=None,
               which_ebook='TESTS',no_elog_write=False,log_me=True,log_level='INFO',dir_logging=my_log_dir)
