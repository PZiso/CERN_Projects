
import sys

sys.path.append('../../lib')

from cmn_methods import * # Some helper functions


class HTadjust(object):
    """
    The HTadjust module is used for maximizing the extracted ion current
    in Linac3 after regulation of the HighVoltage source. The observable is the
    ion beam current from BCT15 and the parameter under adjustment is the sourceHT voltage.
    The module is executed by calling the run() method of the HTadjust class. 

    """
        
    
    
    def __init__(self,FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='HTajust',
                 simulate_SET=False,INCA_ACCEL='LEIR',sourceHT_selector=None,
                 BCT15_selector='LEI.USER.ALL',which_ebook='TESTS',
                 no_elog_write=False,log_me=True,log_level='DEBUG',dir_logging=''):
        """
        Initialisation of the HTadjust module. The input parameters are:
        
        FESA_GHOST_Device: (default:GHOSTconfig): The device of the GHOST module in the appropriate FESA class.
        
        FESA_GHOST_Property: (default:HTajust): The property of the GHOST module in the appropriate FESA class.
        
        simulate_SET:(default:False): Option for executing the HTadjust module in simulation mode i.e. without actually adjusting any 
        of the parameters with JAPC.
        
        INCA_ACCEL:(default:LEIR): The accelerator in the INCA (INjection Control Architecture) database.
        
        sourceHT_selector:(default:None): The JAPC selector for interacting with the sourceHT parameter.
        
        BCT15_selector:(default:'LEI.USER.EARLY'): The selector for interacting with the currentLinacSingle parameter.
        
        which_ebook:(default:'LINAC 3'): The elogbook to push events from the elogbook module.
        
        no_elog_write:(default:False): Flag to suppress logging to the elogbook.
        
        log_me:(default:True): Flag to initiate the logger module for the local log system.
        
        log_level:(default:'DEBUG'): The level of logging for the local log system.
        
        dir_logging: (default:''): The directory of the local log files for logging.
        
        
        
        
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

        self.dir_logging=dir_logging
        
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        
        self.__version__='v.1.6'
        
    
        
#                                              FUNCTION DEFINITIONS 
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #
        


    def HT_Current_Measurements(self,shot_number):
        
        """
        Method of HTadjust class:

            Perform BCT15 current measurements for a maximum of two rounds.

            If the measurements are affected by noise, repeat for a second round. If second round is not successful exit the program.

                Input:

                shot_number: The number of shots for the BCT15 measurements.


                Output:

                BCT15: Dictionary with key values "Mean", "Sigma" and "Values" for the BCT15 measurements

                status: A logical flag to notify the main routine of the unstable conditions in the BCT15 measurements.
        """

        status=1 

        for round_ in ['First','Second']:

            msg=round_+' round of BCT15 measurements'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            BCT15=myGT.get_my_JAPC_parameter(device="ITF.BCT15",field='Acquisition',
                                                         parameter='currentLinacSingle',
                                                         my_selector=self.BCT15_selector,
                                                         no_shots=shot_number)

            my_condition=BCT15['Sigma']>0.1*BCT15['Mean']

            if my_condition and round_=='First':

                msg='First round: Unstable conditions in the BCT15 measurements.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            elif my_condition and round_=='Second':
                msg='Second round: Unstable conditions in the BCT15 measurements.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                msg='Not possible to adjust the HT voltage. Setting the HT voltage to the initial value.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                status=0
           

            elif not my_condition:    

                
                break #EXIT the for loop

        return status,BCT15


# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #


    def HT_Decider(self,BCT15_all,HT_start,HTadjust_vrange):

        """
        Method of HTadjust class:

            Decide which HTsource voltage configuration achieves the maximum current.


                Input:

                BCT15_all: The BCT15 current measurements for 0,+DV,-DV changes of the extraction voltage.

                HT_start: The initial BCT15 current measurement, before regulation the extraction voltage.

                HTadjust_vrange: The FESA parameter which defines the value of the HTadjust regulations.


                Output:

                HT_new: The extraction voltage value which achieves the maximum current.

                BCT15_new: The achieved current value from BCT15 instrument, when setting the HT_new extracting voltage.
        """


        if BCT15_all['Positive'] > BCT15_all['Start']:

            msg='Current p larger than current start.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            if BCT15_all['Positive'] > BCT15_all['Negative']:
                msg='Current p larger than current m.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start+HTadjust_vrange
                BCT15_new=BCT15_all['Positive']

            elif BCT15_all['Negative'] > BCT15_all['Start']:

                msg='Current m larger than current start.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start-HTadjust_vrange
                BCT15_new=BCT15_all['Negative']
            
            else:

                msg='Setting HT_new and BCT_new to their initial values.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

                HT_new=HT_start
                BCT15_new=BCT15_all['Start'] # This is not in the flowchart..should it be inside ?



        elif BCT15_all['Negative']> BCT15_all['Start']:
            msg='Current m larger than current start.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            HT_new=HT_start-HTadjust_vrange
            BCT15_new=BCT15_all['Negative']

        else:

            msg='Setting HT_new and BCT_new to their initial values.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='debug')

            HT_new=HT_start
            BCT15_new=BCT15_all['Start'] # This is not in the flowchart..should it be inside ?

        return HT_new, BCT15_new



# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

#                                                 MAIN FUNCTION

# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #



   
    def run(self,shot_number=10):
        """
        The main function of the HTadjust module. It executes the HTadjust module based on the user's input.
        
        Inputs:
        
            
        shot_number: (default 10): The number of shots in the cycle for which the BCT15 current is measured. 
        This variable is passed in get_my_JAPC_parameter(), HT_Current_Measurement() methods.
            
        
        
        *** Description :
        
        {
            Initially, the programm initiates pyjapc, elogbook and the local logger. 
            Then it looks for the variables HTadjust_kill, HTadjust_inhibit, HTadjust_Vrange, HTadjust_intervall.
            
            {
            
            In case HTadjust_kill=True, the program is not executed.
                
                {
                
                In case HTadjust_inhibit=True, the program is not executed until this flag is changed.
                
                    {
                        If the program is finally executed, it checks the source and current initial conditions. 

                        If the condition allow, it performs one measurement of the initial HT voltage (HTstart).
            
                        
                        The linac current is measured for a total of 3 times: one for zero jump (DV=0) of the extraction
                        voltage, one for a positive (+DV) jump of the voltage and one for a negative jump.(-DV)

                        The measurements are performed for each jump for a maximum of two rounds with the help of HT_Current_Measurement()

                        Then the optimum configuration is chosen with the help of HT_Decider()

                        If the measurement conditions are not ideal (i.e. there is noise in the measurements) the program will halt and restart.voltage

                        In addition, the program is externally controlled with the HTadjust_kill and HTadjust_inhibit variables in FESA.
                        
                    }
                
                }
            }
        
        
        
        
        }
        """




        
        global HT_start, safe_volt_low, safe_volt_high, myGT

        # Initialize my helper !

        myGT=GHOST(mod_name=self.__class__.__name__,FESA_GHOST_Device=self.FESA_GHOST_Device,
            FESA_GHOST_Property=self.FESA_GHOST_Property,simulate_SET=self.simulate_SET,
            INCA_ACCEL='LEIR',japc_selector=self.sourceHT_selector,
            which_ebook=self.which_ebook,no_elog_write=self.no_elog_write,
            log_me=self.log_me,log_level=self.log_level,dir_logging=self.dir_logging)



        # safe_volt_low=myGT.get_FESA_param('Vrange_min')
        safe_volt_low=19040


        # safe_volt_high=myGT.get_FESA_param('Vrange_max')
        safe_volt_high=19100
        

        myGT.start_module() # Initiate loggers, pyJAPC 

        #Infinite loop module !
        while True:


            HTadjust_interval=myGT.get_FESA_param('intervall') # Get HTadjust_interval

            msg='HTadjust_interval is {} minutes'.format(HTadjust_interval)
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


            myGT.my_stopper(flag='initial',set_init=False) # Check kill flag

            HTadjust_inhibit=myGT.get_FESA_param('inhibit')

            msg='HTadjust_inhbit is: '+str(HTadjust_inhibit)+'.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            
            HTadjust_test=myGT.get_FESA_param('test')

            msg='HTadjust_test is: '+str(HTadjust_test)+'.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            
            #Check inhbit flag !
            if not HTadjust_inhibit:

                #Check the status of the HT source before performing and adjustments ! 
                myGT.japc.setSelector(None)

                HT_status=myGT.japc.getParam('IP.NSRCGEN/Status#sourceHTStatus')

                if not HT_status[0]==2:
                    
                    msg=('The status of the source is {0}. ' + 
                        'Waiting for {1} minutes.').format(HT_status[1],HTadjust_interval)

                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    myGT.wait_time_interval(FESA_time=HTadjust_interval,set_init=False)
                    
                    continue
                
                else:
                    msg=('The status of the source is {}. ' + 
                        'Proceeding with HTadjust operations.').format(HT_status[1])

                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    pass

                # Begin main sequence.
 

                HTadjust_vrange=myGT.get_FESA_param('Vrange')

                msg='The HT voltage will be adjusted within a +/- '+str(HTadjust_vrange)+' V range.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                msg='Acquiring source HT voltage.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                HT_start=myGT.get_my_JAPC_parameter(device="IP.NSRCGEN",
                    field="Setting",parameter='sourceHT',my_selector=None,subscribe_=0,no_shots=1)['Mean']

                msg='The source HT voltage is '+str(HT_start)+' V.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                #Do a first current measurement and examine if it is above or below the threshold

                Init_BCT=myGT.get_my_JAPC_parameter(device="ITF.BCT15",
                    field='Acquisition',parameter='currentLinacSingle',
                    my_selector=self.BCT15_selector,no_shots=1,subscribe_=1,verbose=False)['Mean']

                msg='Initial ion beam current measurement is {}'.format("%.3f"%Init_BCT)
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                # Is the current enough? Decide whether to proceed or not.
                if Init_BCT<0.01:
                    msg=('The measurement of the BCT15 current is below threshold (0.01 mA).' + 
                        ' Waiting for {} minutes and restarting.').format(HTadjust_interval)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    
                    myGT.wait_time_interval(FESA_time=HTadjust_interval,set_init=False)
                    
                    continue

                else:
                    
                    msg=('The measurement of the BCT15 current is above threshold (0.01 mA). ' + 
                        'Proceeding with HTadjust operations.')
                     
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    pass


                # Start measurements

                my_keys=['Start','Positive','Negative']

                k=0 # index for my_keys array

                BCT15_all={} #initialize dictionary

                for dv in [0,HTadjust_vrange,-HTadjust_vrange]:

                    myGT.my_stopper(flag='',set_init=True,
                    device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                    val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high)

                    msg='Initiating BCT15 measurements for DV = {} V.'.format(dv)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                    new_set_HTV=HT_start+dv

                    if not HTadjust_test:

                        msg='Setting the HT voltage to {} V.'.format(new_set_HTV)

                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        myGT.set_my_JAPC_parameter(device='IP.NSRCGEN',
                                                   field='Setting',parameter='sourceHT',
                                                   my_selector=self.sourceHT_selector,
                                                   val_to_set=new_set_HTV,
                                                   lim_l=safe_volt_low,lim_r=safe_volt_high)
                    
                    else:

                        msg='This is a test. No SET operation on-going.'
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')



                    status,BCT15=self.HT_Current_Measurements(shot_number=10)

                    msg=('Result of BCT15 measurements for adjustment DV = {0} V: ' + 
                        'Mean-> {1}, Sigma-> {2}').format(dv,"%.3f"%BCT15['Mean'],"%.3f"%BCT15['Sigma'])

                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                    
                    if not status:

                        break


                    BCT15_all[my_keys[k]]=BCT15['Mean']

                    k+=1

                        

                if not status:

                    msg='Adjustments of the HT source are not possible due to unstable conditions.'
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    msg='Setting the HT source voltage to the initial value.'
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                    myGT.wait_time_interval(FESA_time=HTadjust_interval,set_init=True,
                        device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                        val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high,user_time=0) 

                    continue # GOTO the beginning of the while loop


                

                #In this part we are looking for values in the pair (HT_new, BCT15_new)! :-)
                
                HT_new, BCT15_new=self.HT_Decider(BCT15_all,HT_start,HTadjust_vrange)
                
                myGT.my_stopper(flag='',set_init=True,
                    device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                    val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high)
                
                

                if not HTadjust_test:


                    myGT.set_my_JAPC_parameter(device='IP.NSRCGEN',field='Setting',
                     my_selector=self.sourceHT_selector,parameter='sourceHT',
                     val_to_set=HT_new,lim_l=safe_volt_low,lim_r=safe_volt_high)


                else:

                    msg=('New values for the HT adjustment acquired but ' + 
                    ' no SET operation is performed (HTadjust_test=True).')
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                msg=('HT extracting voltage [V]: {0}-->{1}, '+
                    'BCT15 I [mA]: {2}-->{3}').format(HT_start,HT_new,
                    "%.3f"%BCT15_all['Start'],"%.3f"%BCT15_new)
                

                myGT.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')

                myGT.wait_time_interval(FESA_time=HTadjust_interval,set_init=True,
                        device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                        val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high,user_time=0)

                continue  #GOTO initial while loop

            else:

            # Wait for new input and restart
                msg=('Inhibition of module HTadjust: Inhibit flag raised by the user.' + 
                    'The module will resume after change of the HTadjust_inhibit flag.')

                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info') 

                self.wait_time_interval(FESA_time=HTadjust_interval,set_init=True,
                        device='IP.NSRCGEN',field='Setting',parameter='sourceHT',
                        val_to_set=HT_start,lim_l=safe_volt_low,lim_r=safe_volt_high,user_time=0)
                # sleep(10) #wait 10 seconds before restarting.
                continue  #GOTO initial while loop
                


#                                                    RUN ME                                                
# *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--* #

    
if __name__ == "__main__":

    my_log_dir='/afs/cern.ch/user/p/pzisopou/Linac3_Source/GHOST_Module/HTadjust/log/'
        
    HT_object=HTadjust(simulate_SET=True, sourceHT_selector=None,
                       BCT15_selector='LEI.USER.ALL',
                       which_ebook='TESTS',no_elog_write=False,log_me=True,log_level='INFO',
                       dir_logging=my_log_dir) 
                       #Roll back to Simulation mode with simulate_SET=True ; For L3 elog write : which_ebook='LINAC 3'  


    HT_object.run(shot_number=10) # Run HTadjust module.