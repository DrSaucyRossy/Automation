# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 17:42:15 2019

@author: RossAnthony 
Used To Run a Keithley2400
"""

import visa
import time
import numpy as np
import pandas as pd
from datetime import datetime
VStart = 2
VStep = -0.5
VFinish = -2 + VStep
V = np.arange(VStart,VFinish,VStep)
rm = visa.ResourceManager()
K_2400 = rm.open_resource('GPIB0::10::INSTR')
K_2400.write("*rst; status:preset; *cls") #reset and clear instrument
K_2400.write(':SOUR:FUNC VOLT') # use voltage as source
K_2400.write(':SOUR:VOLT:RANG 200')# % votlage source range is set up to 20V.
K_2400.write(':SENS:FUNC "CURR"')  # measure current 
K_2400.write(':SENS:CURR:PROT 0.5') #  Set compliance current
K_2400.write(':SENS:CURR:RANG:AUTO ON') #Turn on Autorange
K_2400.write(':OUTP ON') #Turn on Voltage

Current = []
Voltage = []
n = len(V)
for i in range(n):
    K_2400.write(':SOUR:VOLT:LEV ', str(V[i])) #Set Voltage
    values = np.array(K_2400.query_ascii_values(':READ?')) #Read Current
    Current.append(values[1]) #Record Current
    Voltage.append(V[i]) #Record Voltage
    time.sleep(0.01) #From Zhao's Code: pause time is necessary. if not defined, reading might be unavailable
K_2400.write('OUTP OFF') #Turn Off Voltage
K_2400.clear() 
K_2400.close() 
#Save data to CSV
data = np.transpose([Voltage,Current])
x =  'Dark Current '
timing = datetime.now()
y = timing.strftime("%d-%m-%Y %H--%M--%S")
z = '.csv'
pd.DataFrame(data).to_csv(x+y+z , header = ['Voltage (V)','Current (A)'], index = None) #can alter the string to include a file path. Otherwise it will save in the same folder as your script