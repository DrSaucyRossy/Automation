# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 13:11:06 2019

@author: RossAnthony
"""

import visa
import time
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from datetime import datetime

scan_speed = 5  # nm/s only 0.5 5 40 allowed
avg_time=1E-4 # photodiode average time
wavelength_start = 1550
wavelength_step = 0.1
wavelength_finish = 1560 + wavelength_step
wavelength = np.arange(wavelength_start,wavelength_finish,wavelength_step) # nm

rm = visa.ResourceManager()
Agilent_8164A = rm.open_resource('GPIB0::20::INSTR')
Agilent_8164A.write('*cls'); # instrument setting reset
points = len (wavelength);
Agilent_8164A.write('trig:conf LOOP') # an output trigger is autometically works as input trigger
Agilent_8164A.write('TRIG1:OUTP DIS') # PD output trigger is disabled
Agilent_8164A.write('TRIG1:INP SME') # PD will finish a function when input trigger is abled
Agilent_8164A.write('TRIG0:OUTP STF')# TLS will send a output trigger when sweep starts (input trigger generated)
Agilent_8164A.write('TRIG0:INP IGN') # (TLS input trigger is ignored)

# sensor setting
Agilent_8164A.write('init1:cont 1')# continuous detection mode
Agilent_8164A.write('sens1:pow:atim 1MS')# set the averagetime to 1ms for sensor 2
Agilent_8164A.write('sens1:pow:rang:auto 0')#set auto ranging off
Agilent_8164A.write('sens1:pow:rang -10DBM')#sense range (maximum power that can be detected)
Agilent_8164A.write('sens1:pow:unit 1')# set the unit of power: 0[dBm],1[W]
Agilent_8164A.write('sens1:pow:wav 1550nm'); # set senser wavelength centered at 1550 nm

# tunalbe laser setting
Agilent_8164A.write('outp0:path high');# choose which path of tuable laser. output1 [low power high sens] output2 [high power]
Agilent_8164A.write('sour0:pow:unit 0');# set source power unit
Agilent_8164A.write('sour0:pow 0');#sset laser power {unit will be according to the power unit set before}
Agilent_8164A.write('sour0:AM:stat OFF');
#continuous sweep setting
Agilent_8164A.write('wav:swe:mode CONT');
scan_speed_command = 'wav:swe:spe ' + str(scan_speed) + 'nm/s'
Agilent_8164A.write(scan_speed_command); # only 0.5 5 40 allowed
wavelength_start_command = 'wav:swe:star ' + str(wavelength_start) + 'nm'
wavelength_step_command = 'wav:swe:step ' + str(wavelength_step) + 'nm'
wavelength_stop_command = 'wav:swe:stop ' + str(wavelength_finish) + 'nm'
Agilent_8164A.write(wavelength_start_command);
Agilent_8164A.write(wavelength_step_command);
Agilent_8164A.write(wavelength_stop_command);
Agilent_8164A.write('wav:swe:cycl 1'); #Set the number of cycles
log_data_command = 'sens1:func:par:logg ' + str(points) + ',' + str(avg_time)
Agilent_8164A.write(log_data_command); # Sets the number of data points and the averaging time for the logging data acquisition function
Agilent_8164A.write('sens1:func:stat stab,star'); #Enables Stability data acquistion and starts data acquistion
Agilent_8164A.write('wav:swe STAR'); # Start wavelength sweep

Agilent_8164A.write('sour0:wav:swe:llog 1'); #Logging the wavelength during the sweep
time.sleep(10);
values = Agilent_8164A.query_binary_values('sour0:read:data? llog', datatype='d', is_big_endian=True)# get wavelength data from logging operation
power = Agilent_8164A.query_binary_values('sens1:func:res?'); #get power data
P = savgol_filter(power,11,3) # Smooths data
Agilent_8164A.write('sens1:pow:rang:auto 1') #set auto ranging on
Agilent_8164A.write('TRIG1:INP IGN'); # PD will finish a function when input trigger is abled
Agilent_8164A.write('sour0:wav 1550nm'); # set the input wavelength back to 1550 nm for the next measurment
data = [values, P]
x =  'Sweep '
timing = datetime.now()
y = timing.strftime("%d-%m-%Y %H--%M--%S")
z = '.csv'
pd.DataFrame(data).to_csv(x+y+z , header = ['Wavelength (m)','Power (dBm)'], index = None)
