import sys

sys.path.append('../../lib')

from cmn_methods import *


class OvenRestart(object):
    """
    The OvenRestart module is a single-passage module which can be  used for restarting oven 1 and 2 of the Ion Source at Linac 3, separately or simultaneously.

    The implementation of the code is based on the OvenRestart flow-chart from D. Kuchler:https://edms.cern.ch/document/2000941.

    Interaction with code is performed via the GHOST FESA class. 

    
    """
        
    
    
    def __init__(self,FESA_GHOST_Device='GHOSTconfig',FESA_GHOST_Property='OvenRestart',
                 simulate_SET=True,INCA_ACCEL='LEIR',Oven_FESA_selector=None,
                 OvenResistance_selector='LEI.USER.ALL',OvenPower_wait=60,OvenIncrPower_wait=20,
                 Pressure_wait=5,Pressure_limit=1e-6,which_ebook='LINAC 3',
                 no_elog_write=False,log_me=True,log_level='DEBUG',dir_logging=''):
        """
        Initialisation of the OvenRestart module. The input parameters are:
        
        FESA_GHOST_Device: (default:GHOSTconfig): The device of the 
                                                  GHOST module in the appropriate FESA class.
        
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

        dir_logging:(default:''): The directory for the saving of the local log files.
        
        
        
        
        
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
        
        self.dir_logging=dir_logging
        
        self.__author__='P. Zisopoulos (pzisopou@cern.ch)'
        
        self.__version__='v.1.0'
        
    
    
        
    
    
    def pressure_checker(self):
        """
        Method to check the pressure at LINAC3.
        """

        time_wait=self.Pressure_wait

        assert time_wait>0,"Please give a positive and finite waiting time."

        P=myGT.japc.getParam('IP.VGP2/PR')

        msg='The pressure is {} mbar.'.format("%.2E"%P)
        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        while P >= self.Pressure_limit:

            msg=('Pressure is larger than {0} mbar. '+
                'Waiting for {1} minutes before '+
                'next measurement.').format(self.Pressure_limit,time_wait)

            myGT.write_L3_log(msg=msg+'[GHOST:OvenRestart]',where='both logs',logfile_lvl='info')

            # Wait for 5 minutes
            myGT.wait_time_interval(FESA_time=time_wait,set_init=False)
            # Re-check pressure
            P=myGT.japc.getParam('IP.VGP2/PR')
    
    def which_combo(self):
        """
        A method which produces indexes and a list with the oven numbers, 
        in accordance to the oven that is selected.
       
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

        myGT.japc.setSelector(None)

        oven_power=myGT.japc.getParam(['IP.NSRCGEN/Setting#oven1Power',
            'IP.NSRCGEN/Setting#oven2Power'])[left:right]
        m=0
        for powpow in oven_power:
            msg='The power of oven {0} is measured to be {1} W.'.format(which_oven[m],"%.2f"%powpow)
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
            m+=1

        return oven_power

    def read_resistance(self):
        """
        Method to read the resistance of the ovens.
        Note the selector cannot be None otherwide JAPC complains for multiplexed parameter.
        Selector LEI.USER.ALL is mandatory so we need to subscribe.
        
        """

        if Oven_choice==1 or Oven_choice==2:

            res=[myGT.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven'+str(Oven_choice)+'AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean']]
            which_oven=[Oven_choice]

        elif Oven_choice==3:

            res=[myGT.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven1AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean'],
            myGT.get_my_JAPC_parameter(device='IP.NSRCGEN',field='Acquisition',
                parameter='oven2AqnR',my_selector='LEI.USER.ALL',no_shots=1,subscribe_=1,verbose=False)['Mean']]
            which_oven=[1,2]

        m=0
        for r in res:
            msg='The resistance of oven {0} is measured to be {1} Ohms.'.format(which_oven[m],"%.2f"%r)
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
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
        
        global Oven_choice, myGT
        
        # Initialize my helper !

        myGT=GHOST(mod_name=self.__class__.__name__,FESA_GHOST_Device=self.FESA_GHOST_Device,
            FESA_GHOST_Property=self.FESA_GHOST_Property,simulate_SET=self.simulate_SET,
            INCA_ACCEL='LEIR',japc_selector=self.Oven_FESA_selector,
            which_ebook=self.which_ebook,no_elog_write=self.no_elog_write,
            log_me=self.log_me,log_level=self.log_level,dir_logging=self.dir_logging)


        myGT.start_module()# Initialize logging systems and JAPC

        myGT.my_stopper(flag='initial',set_init=False) # Check OvenRestart_kill flag 
                                                       #without setting any initial value :-)

        

        #Single-passage module !


        msg='Acquiring OvenRestart_inhibit.'
        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        OvenRestart_inhibit=myGT.get_FESA_param('inhibit')

        msg='The inhibit flag is: '+str(OvenRestart_inhibit)
        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

    
        
        #Check inhbit flag !
        if  not OvenRestart_inhibit:

            # Get the choice of oven
            Oven_choice=myGT.get_FESA_param('oven')

            #Check the status of the Oven ! 

            if Oven_choice==1 or Oven_choice==2:
                
                myGT.japc.setSelector(None)

                Oven_status=myGT.japc.getParam('IP.NSRCGEN/Status#oven'+str(Oven_choice)+'Status')[1]
                which_oven=[Oven_choice]
                msg='Oven {} is selected for restart.'.format(Oven_choice)

                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            elif Oven_choice==3:

                Oven_both_status=[item[0] for item \
                in myGT.japc.getParam(['IP.NSRCGEN/Status#oven1Status',
                    'IP.NSRCGEN/Status#oven2Status'])]
                
                which_oven=[1,2]
                msg='Ovens 1 and 2 are selected for restart.'
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                if sum(Oven_both_status)==4:
                    Oven_status='ON'
                else:
                    Oven_status='OFF' #if one of the ovens is OFF 
                                      #in the oven selector 3 case, then do not proceed with operations.
            else:
                raise ValueError(('Wrong choice of oven. Please select 1,2,3 in '+
                    ' the OvenRestart_oven parameter in the FESA class.'))


            if Oven_status=='ON':

                msg=("The status of the oven {0} is {1}. " +
                    "Proceeding with the reading of the oven power.").format(which_oven,Oven_status)
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                #Get oven power
                Oven_power=self.read_power()
                
                #Make sure it is not larger than 0 
                if not all(Oven_power):

                    msg=('Oven does not appear to be powered on.'+
                        ' Proceeding with OvenRestart module operations.')

                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    #Get the pressure. 
                    #Wait 5 minutes for each measurement of the pressure, until it is above threshold.

                    self.pressure_checker()

                    msg=('Pressure is larger than 1e-6 mbar. '+
                        'Proceeding with resistance reading from oven {}.').format(which_oven)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                        

                    msg='Setting power of oven {0} to 2 W.'.format(which_oven)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    set_oven_power=2.0 #in Watts

                    for ov in which_oven:
                        is_safe_to_set=myGT.set_my_JAPC_parameter(device='IP.NSRCGEN',
                            field='Setting',parameter='oven'+str(ov)+'Power',
                            my_selector=None,val_to_set=set_oven_power,lim_l=0.0,lim_r=10.0)

                    msg='The power of the oven {} is set. Waiting for 60 minutes.'.format(which_oven)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    #wait for 60 minutes
                    time_wait=self.OvenPower_wait
                    
                    myGT.wait_time_interval(FESA_time=time_wait,set_init=False)

                    msg='{} minutes have passed. Continuing with pressure measurement.'.format(time_wait)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    #check pressure for second time. 
                    #Wait 5 minutes for each measurement of the pressure, until it is above threshold.

                    self.pressure_checker()

                    msg=('Pressure is smaller than {0} mbar. '+
                        'Proceeding with resistance reading from '+
                        'oven {1}.').format(self.Pressure_limit,which_oven)

                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    R=self.read_resistance()

                    msg='The resistance of oven {0} is measured to be {1} Ohms.'.format(Oven_choice,R)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                    go_up=0.5 # Increase Oven Power by 0.5 W

                    while all(np.asarray(R)>0.5) and all(np.asarray(R)<5.0):

                        
                        msg=('Power of oven {0} is {1} W. '+
                            'Increasing power by {2} W.').format(which_oven,set_oven_power,go_up)
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')


                        #increase the oven power

                        set_oven_power+=go_up

                        for ov in which_oven:

                            is_safe_to_set=myGT.set_my_JAPC_parameter(device='IP.NSRCGEN',
                                field='Setting',parameter='oven'+str(ov)+'Power',
                                val_to_set=set_oven_power,lim_l=0.0,lim_r=10.0,my_selector=None)



                        #wait for 20 minutes

                        time_wait=self.OvenIncrPower_wait
                        msg=('Oven {0} power increased by {1} W. '+
                            'Waiting for {2} minutes.').format(which_oven,go_up,time_wait)
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        myGT.wait_time_interval(FESA_time=time_wait,set_init=False)

                        msg=('{0} minutes have passed. '+
                            'Proceeding with pressure measurement.').format(time_wait)
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        self.pressure_checker()

                        msg=('Pressure is smaller than {0} mbar. '+
                            'Proceeding with resistance '+
                            'reading from oven {1}.').format(self.Pressure_limit,which_oven)

                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        

                        
                        msg='Checking if oven {0} is larger than 5.0 W.'.format(which_oven)
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

                        Oven_power=self.read_power()

                        if all(np.array(Oven_power)>=5.0):
                            m=0

                            for it in which_oven:

                                msg=('Power measurement of '+
                                    ' oven {0} is {1} W.').format(it,"%.2f"%Oven_power[m])
                                
                                myGT.write_L3_log(msg=msg,where='both logs',logfile_lvl='info')
                                
                                m+=1

                            msg="OvenRestart module finished with success. Goodbye! :-)"
                            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                            

                            break #exit from the while loop

                        else:

                            m=0

                            for it in which_oven:
                                msg=('Power measurement of '+
                                    'oven {0} is {1} W. ').format(it,"%.2f"%Oven_power[m])
                                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                            

                            # Read resistance to determine if the module should go on
                            R=self.read_resistance() 

                            msg=('The resistance of oven {0} is measured '+
                            'to be {1} Ohms.').format(Oven_choice,R)
                            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                            
                            continue #continue in the while loop.


                    else:

                        msg=('Resistance value outside operation range (0.5,5) Ohms. '+
                            'Aborting OvenRestart module operations. Exiting.')
                        myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')
                                                    

                else:

                    msg=('Oven {} appears to be already powered on. '+
                        'Aborting OvenRestart module operations. Exiting.').format(Oven_choice)
                    myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')



            else:

                msg=('The status of the oven {0} is {1}. '+
                    'Aborting OvenRestart module operations. Exiting.').format(Oven_choice,Oven_status)
                myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

        else:


            # Wait for new input and restart
            msg='Inhibition of module OvenRestart: Inhibit flag raised by the user. Exiting.'
            myGT.write_L3_log(msg=msg,where='logfile',logfile_lvl='info')

            
                
    
if __name__ == "__main__":
    
    #my_log_dir='/afs/cern.ch/user/p/pzisopou/Linac3_Source/GHOST_Module/OvenRestart/log/'
    
    my_log_dir='/user/ln3op/GHOST/OvenRestart/log/'
        
    OR_object=OvenRestart(simulate_SET=False,INCA_ACCEL='LEIR',Oven_FESA_selector=None,
                 OvenResistance_selector='LEI.USER.ALL',OvenPower_wait=60,
                 OvenIncrPower_wait=20,Pressure_limit=1e-6,Pressure_wait=5,which_ebook='LINAC 3',
                 no_elog_write=False,log_me=True,log_level='INFO',dir_logging=my_log_dir)
                  # # Roll back to SET mode with simulat_SET=True    
    OR_object.run() # Run OvenRestart module.




