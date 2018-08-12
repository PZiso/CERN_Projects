
# coding: utf-8

# In[1]:

from GHOST import HTadjust 


# # Main Code

# In[2]:

HT_object=HTadjust(simulate_SET=False,no_elog_write=False,log_me=True,log_level='INFO') # Initiate object


# In[3]:

#knobs for input parameters--> To be set in the Control Room
HT_object.initiate_JAPC()
HT_object.initiate_logger()#--> This is needed for the set_HTadjust method but it seems a bit dull :P
HT_object.set_HTadjust('kill',False)
HT_object.set_HTadjust('inhibit',False)
HT_object.set_HTadjust('test',False)


# In[4]:

HT_object=HTadjust(simulate_SET=True,no_elog_write=False,log_me=True,log_level='DEBUG') # # Roll back to simulation mode


# In[6]:

HT_object.run()


# In[ ]:

# from IPython.display import IFrame
# IFrame("HTadjust_v2.pdf", width=600, height=500)


# In[ ]:

#!jupyter nbconvert --to script HT_adjust_v2.ipynb  #For conversion to Python script.

