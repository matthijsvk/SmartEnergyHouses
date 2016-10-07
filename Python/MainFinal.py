# -*- coding: cp1252 -*-

#libraries en modules
import sys
import datetime
import time
import gobject
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    print('GTK not available')
    sys.exit(1)

import time
import MySQLdb

#eigen files
import QuerySmarthouse
import PlotValues
import communicatie

import Python_Gams_DagNacht_GeenLocal_functie
import Python_Gams_DagNacht_Local_gn_Curt_functie
import Python_Gams_DagNacht_Local_functie
import Python_Gams_Variabel_GeenLocal_functie
import Python_Gams_Variabel_local_geen_curtail_functie
import Python_Gams_Variabel_inclusief_local_functie


##########################################################################################################################################################################################

DagNacht_GeenLocal=1
DagNacht_Local_gn_Curt=3
DagNacht_Local=2

Variabel_GeenLocal=4
Variabel_Local_gn_Curt=6
Variabel_Local=5

##############################################################
                                                             #
huidige_programma= DagNacht_GeenLocal ## Choose your program     #
piper_poort= 'COM8'               ## Choose your port        #
                                                             #
##############################################################


arduino1= 1 #we werken enkel arduino met nr 1

day_start=6.00
day_end= 5.45
time_scheme= []
program_time_scheme= []
pheatinglst= []
pricelst= []

#### Pins ####

#input pins
tv_switch= 14 #analog pin A0
light_upstairs_switch=15 #analog pin A1

light_sensor_pin=int(QuerySmarthouse.query1("SELECT Pinnbr FROM sensor WHERE Sensor_name = 'licht'")[0][0])
temp_sensor_pin=int(QuerySmarthouse.query1("SELECT Pinnbr FROM sensor WHERE Sensor_name = 'temperatuur'")[0][0])

#output pins
tv_pin=int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'tv' AND p.Device_ID = d.Device_ID")[0][0])
heating_pin= int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'verwarming' AND p.Device_ID = d.Device_ID")[0][0])
light_upstairs_pin= int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'licht boven' AND p.Device_ID = d.Device_ID")[0][0])
light_downstairs_pin= int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'licht beneden' AND p.Device_ID = d.Device_ID")[0][0])
fornuis_pin=int(QuerySmarthouse.query1("SELECT Pinbr FROM Device_pin as p, device as d WHERE Device_name = 'fornuis' AND p.Device_ID = d.Device_ID")[0][0])
fridge_pin=int(QuerySmarthouse.query1("SELECT Pinbr FROM Device_pin as p, device as d WHERE Device_name = 'diepvriezer' AND p.Device_ID = d.Device_ID")[0][0])
wash_mach_pin=int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'wasmachine' AND p.Device_ID = d.Device_ID")[0][0])
#voor de demo doen we alsof de auto een vaatwas is; de auto wordt aangesloten op pin 8
#auto_pin=int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'auto' AND p.Device_ID = d.Device_ID")[0][0])
dish_wash_pin= 8 #int(QuerySmarthouse.query1("SELECT Pinbr FROM device_pin as p, device as d WHERE Device_name = 'vaatwasser' AND p.Device_ID = d.Device_ID")[0][0])


#### Programs ####

light_upstairs_program=int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'licht boven'")[0][0])
light_downstairs_program=int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'licht beneden'")[0][0])
wash_mach_program= int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'wasmachine'")[0][0])
dish_wash_program= int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'vaatwasser'")[0][0])
fridge_program= int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'diepvriezer'")[0][0])
tv_program=int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'tv'")[0][0])
heating_program=int(QuerySmarthouse.query1("SELECT Program_ID FROM program as p, device as d WHERE p.Device_ID = d.Device_ID AND d.Device_name = 'verwarming'")[0][0])

digital_programs= [dish_wash_program, wash_mach_program, fridge_program, tv_program,light_upstairs_program,light_downstairs_program]  
switch_programs_list= {tv_switch:tv_program,light_upstairs_switch:light_upstairs_program}

#global variables needed for main()
counter = 0 
prev_counter= 10


#####   Init  #####

#@effect starts GAMS program, gets list of programs at all quarters, list of prices at all quarters
#        and initializes communication

def init():
    global progam_time_scheme, time_scheme
    print 'initializing, please wait a sec'

    if huidige_programma==DagNacht_GeenLocal:
        Python_Gams_DagNacht_GeenLocal_functie.init()
    elif huidige_programma== DagNacht_Local_gn_Curt:
        Python_Gams_DagNacht_Local_gn_Curt_functie.init()
    elif huidige_programma== DagNacht_Local:
        Python_Gams_DagNacht_Local_functie.init()
        
    elif huidige_programma==Variabel_GeenLocal:
        Python_Gams_Variabel_GeenLocal_functie.init()
    elif huidige_programma== Variabel_Local_gn_Curt:
        Python_Gams_Variabel_local_geen_curtail_functie.init()
    elif huidige_programma==Variabel_Local:
        Python_Gams_Variabel_inclusief_local_functie.init()
    else:print 'ERROR. Geen programma"s gevonden'
        
    progam_time_scheme= get_progam_time_scheme() #lijst met program_ID's van ieder kwartier (het kwartierNr= de positie in deze lijst)
    print program_time_scheme
    communicatie.init(piper_poort)
    
    #zet alle pins uit
    arduinoNr=arduino1
    communicatie.pin_control(arduinoNr,[2,3,4,5,6,7,8,9,10,11],0)
    
    print 'done \n'


#### Functions used in main() ####

#@param the smart programs that are currently on
#@param category1 the states of all the switches
#@ effect return the analog and the digital programs
def sort_programs(programs_on, category1): #subfunctions: r275
    global digital_programs

    #get new programs to be turned on and previous programs to be turned off. The other programs are the same as before.
    category1_programs_on= get_category1_programs(category1)                 
    
    #splitsen in analoge/digitale programma's: aan/uit of met tussenstadia (bv licht vs verwarming)            
    programs_on_digital=[]
    programs_on_analog=[]
                
    for program in programs_on:  #new programs to be turned on
        if program in digital_programs:
            programs_on_digital.append(program)
             
        else:
            programs_on_analog.append(program)
    
    for category1_program in category1_programs_on: #all switch-programs are digital programs        programs_on_digital.append(category1_program)
          programs_on_digital.append(category1_program)                         
    return programs_on_digital,programs_on_analog

#@effect all the commands to the SEH
def control_arduino(arduinoNr,programs_on_digital,programs_on_analog): #subfunctions: r234
    
    #turn programs on/off
    arduino_turn_digital_programs_off(arduinoNr)

    if len(programs_on_digital)>0:
        arduino_turn_digital_programs_on(arduinoNr,programs_on_digital) 
        
    if len(programs_on_analog) > 0:
        arduino_turn_analog_programs_on(arduinoNr,programs_on_analog)
    
#@effect return all the smart programs that are currently on
def get_program_IDs_now(counter):
    return progam_time_scheme[counter]

#@effect return all the programs that are currently on
def get_all_programs_on(programs_on,category1):
    all_programs_on=[]
    
    for program in programs_on:
        all_programs_on.append(program)
        
    for switch in category1:
        switch_programs= get_programs_switch(switch)
        for switch_program in switch_programs:
            if switch[1]==1:
                all_programs_on.append(switch_program)
    switch_light = getLightSwitch() #software switch
    if(switch_light == True):
        all_programs_on.append(light_downstairs_program)
            
    return all_programs_on
        

#### Subfunctions of control_arduino ####

#@ effect send commands to turn pins on to SEH 
def arduino_turn_digital_programs_on(arduinoNr,programs_on_digital):
    'turn all the pins from these programs on'
    on_pins = [] #pins for each device
    for program in programs_on_digital:
        device_pins= get_device_pins(program)
        for pin in device_pins:
            on_pins.append(pin)

    communicatie.pin_control(arduinoNr,on_pins,1) 

#@ effect send commands to turn all pins off to SEH
def arduino_turn_digital_programs_off(arduinoNr):
    'turn all the pins from these programs off'
    off_pins = [2,3,4,5,6,7,8,9,10,11]
            
    communicatie.pin_control(arduinoNr,off_pins,0) 

#@ effect send commands for PWM to SEH
def arduino_turn_analog_programs_on(arduinoNr,programs_on_analog):
    'turn all the pins from these programs on with the right value'
    on_pins = [] #pins for each device
    values= []
    
    for program in programs_on_analog:
        on_pins.append(get_device_pins(program))
        values.append([get_analog_value(program)])
   
    for i in range(len(programs_on_analog)):
        communicatie.analog_pin_control(arduinoNr,on_pins[i],values[i])

#return value for PWM that belongs to the program (only for heating_program)
def get_analog_value(program):
    'return analoge waarde die hoort bij dit programma (bv verwarming op "hoog" programma -> 900)'
    if program not in digital_programs:
        return communicatie.mapp(program,0,2000,0,253) #heating
    return 255

#@param the program of which to return the pins
#@effect the pins that belong to the program
def get_device_pins(program): 
    'return alle pinnen die bij een bepaald programma horen (in een lijst)'

    #gebruikt in demo
    if program==light_upstairs_program:
        return [light_upstairs_pin,light_downstairs_pin]
    elif program==light_downstairs_program:
        return [light_downstairs_pin]
    
    elif program==dish_wash_program:
        return [dish_wash_pin]
    elif program==wash_mach_program:
        return [wash_mach_pin]
    elif program==fridge_program:
        return [fridge_pin]
    elif program== tv_program: 
        return [tv_pin]
    
    else :return [heating_pin]
    #####return QueryDatabase.query1("SELECT Device_pin FROM Program WHERE Program_id= '(%d)'",program) #####  NIET GETEST


#### Subfunctions of sort_programs ####
                                   
#@param the states of all the switches
#@effect return the programs that belong to the switches that are turned on
def get_category1_programs(category1):
    category1_programs_on=[]
    for switch in category1: #New states: get programs that belongs to each switch and add them to category1_programs_on/off
        switch_programs= get_programs_switch(switch)

        if switch[1]==1:
            for switch_program in switch_programs:
                category1_programs_on.append(switch_program)

        switch_light = getLightSwitch()
        if(switch_light == True):
            category1_programs_on.append(light_downstairs_program)

    return category1_programs_on

#@effect return the program that belongs to the switch
def get_programs_switch(switch):
    global switch_programs_list
    'return programma"s die bij een switch horen '
    if switch[0] in switch_programs_list.keys():
        return [switch_programs_list[switch[0]]]
    else: return [0]


##### Gui update functions #####

def get_current_sensor_data():
    while len(sensor_data_interpreted)<2:
        sensor_data_interpreted.append(20)
    return [sensor_data_interpreted[:2]] #enkel licht en temperatuur

#Return the current relative daytime in minutes
def get_current_time_minutes(counter):
    current_time= get_current_time(counter)    
    return [(current_time)*60]

def get_current_electricity_price(counter):
    if len(pricelst)>counter:
        return [pricelst[counter]*0.001] #huidige prijs
    else: return [0]

#@param counter: the current quarter number
#@param category1 the states of all the switches
#@effect returns all the programs that are turned on currently  for gui
def get_current_programs(counter,category1):
    
    programmas_on= program_time_scheme[counter]
    all_programs_on= get_all_programs_on(programmas_on,category1)
    all_programs_on[0]= heating_program
    return [all_programs_on]

#@effect returns the current boiler consumption in 
def get_current_boiler_consumption(counter):
    current_programs_on= get_program_IDs_now(counter)
    if len(current_programs_on)>0:
        return [current_programs_on[0]*0.001] #boiler is always the first of the current programs on
    else: return [0]

    

#### Time & GAMS functions ####

def GAMS_init():
    # 1. Setup Gams Workspace
    # ws = gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.ShowLog)
    ws = gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.Off)
    # 2. Initialize Job
    job = ws.add_job_from_file('optimalisatie_energie.gms')
    return job

def time_to_quarters(time): #time is a float between 0.0 and 24.0
    return int(time/0.25 - day_start/.25)                                       

#@effect return the time at the current quarternumber
def get_current_time(counter):
    if time_scheme[counter]>24.0:
        return time_scheme[counter]-24.0
    return time_scheme[counter]%24.0

#@effect compile a list of programs at each quarternumber, a list of the time at each quarternumber, a list of the price at each quarternumber
def get_progam_time_scheme():
    global program_time_scheme, pricelst, time_scheme

    #fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_DagNacht_GeenLocal_functie.run_dagnacht_nolocal()
    if huidige_programma==DagNacht_GeenLocal:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_DagNacht_GeenLocal_functie.run()
    elif huidige_programma== DagNacht_Local_gn_Curt:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_DagNacht_Local_gn_Curt_functie.run()
    elif huidige_programma== DagNacht_Local:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_DagNacht_Local_functie.run()
        
    elif huidige_programma==Variabel_GeenLocal:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_Variabel_GeenLocal_functie.run()
    elif huidige_programma== Variabel_Local_gn_Curt:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_Variabel_local_geen_curtail_functie.run()
    elif huidige_programma==Variabel_Local:
        fridgelst, tfrilst, thouselst, pheatinglst, washmachlst, dishwashlst, pricelst= Python_Gams_Variabel_inclusief_local_functie.run()
    else:
        print 'ERROR... Geen programma"s gevonden'
        
    time_scheme=[]
    for i in range(len(pheatinglst)): #per kwartier
        time_scheme.append(day_start+ i*0.25)

    for i in range(len(time_scheme)):
        now_programs= []

        now_programs.append(int(pheatinglst[i])) #this is always the first value
        if int(fridgelst[i])==1:
            now_programs.append(fridge_program)
        if int(washmachlst[i])==1:
            now_programs.append(wash_mach_program)
        if int(dishwashlst[i])==1:
            now_programs.append(dish_wash_program)

        current_time= get_current_time(i)
        if current_time> 17.0 and current_time<24.00:  #voorbeelden van niet-GAMS programma's
            now_programs.append(light_downstairs_program)
        if current_time>=17.0 and current_time<=18.0:
            now_programs.append(tv_program)

        program_time_scheme.append(now_programs)
    return program_time_scheme


#@param the current and previous quarternumber
#@effect execute the current quarter
def main(countertje,prev_countertje):
    global sensor_data_interpreted,counter,prev_counter
    
    counter= countertje
    prev_counter= prev_countertje
    programs_on,category1= [],[]
    
    if counter>=96:
        counter=0
        prev_counter=10
        sensor_data_interpreted=[]
    
    while counter== prev_counter:
        counter+= 1
        if counter>= 96:
            counter= 0
            prev_counter= 10
            sensor_data_interpreted=[]
            #resetDay gebeurt helemaal onderaan, in loop()
        time.sleep(0.1)
        
    while counter > prev_counter+ 1:
        counter-= 1
    
    current_time= get_current_time(counter)
    
    #get sensor data
    arduinoNr= arduino1 #only ask data from first SEH
    sensor_data_interpreted, category1= communicatie.receive_data_arduino(arduinoNr) #category1 is een list met switches en de gelezen waarden (1/0)
    sensor_data_interpreted.append(category1)

    #get programs
    programs_on= get_program_IDs_now(counter)
    if counter>0:
        prev_programs_on= get_program_IDs_now(counter-1)
    all_programs_on= get_all_programs_on(programs_on,category1)

    ##control the first SEH
    programs_on_digital,programs_on_analog= sort_programs(programs_on, category1)
    
    arduninoNr= arduino1 #control first arduino
    control_arduino(arduinoNr,programs_on_digital,programs_on_analog)

    prev_counter= counter

    print 'The current time is: ', current_time
    print 'counter_number: ',counter
    print 'smart_programs_on: ', programs_on
    print 'all programs on: ', all_programs_on
    print 'values: ',current_time, sensor_data_interpreted, all_programs_on
    
    return counter, category1

####################################################################3############################################################################
########################3########################3########################3

#GUI

########################################
    
#Signals to connect to the Gui
class Signals:

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("HomeApp.glade")
    #show the program list window
    def showPrograms(self, button):
        window = builder.get_object("RunningPrograms")
        #builder.get_object("StatusWindow").hide()
        window.show()
    #hide the program list window
    def hidePrograms(self, button):
        window = builder.get_object("RunningPrograms")
        window.hide()
        #builder.get_object("StatusWindow").show()
    #show the history window
    def showHistory(self, button):
        window = builder.get_object("History")
        #builder.get_object("StatusWindow").hide()
        window.show()
    #hide the history window
    def hideHistory(self, button):
        window = builder.get_object("History")
        window.hide()
        #builder.get_object("StatusWindow").show()
        

########################################

#Get the lightButton's state from the gui
def getLightSwitch():
    button=builder.get_object("lightButton")
    return (button.get_active()==True)

#Rendering functions

#Set the time
def setTime(value):
    textbox=builder.get_object("labelTime")

    hours=str(int(value)/60)
    minutes=str(int(value)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    
    textbox.set_text(hours+ " : " + minutes)
#############################################Status
#render lights value
def setStatusLight(value):
    textbox=builder.get_object("lightButton")
    if(value > 1000):
        textbox.set_label("aan")
    else:
        textbox.set_label("uit")
#render temperature value
def setStatusTemp(value):
    textbox=builder.get_object("entry1")
    textbox.set_text(str(round(value,4)))
#render heating value
def setStatusHeating(value):
    textbox=builder.get_object("entry5")
    if(value >0):
        textbox.set_text("aan")
    else:
        textbox.set_text("uit")
#render consumption value
def setStatusConsumption(value):
    textbox=builder.get_object("entry3")
    textbox.set_text(str(round(value,4)))

#############################################House consumptions
#render hourly consumption
def setConsumptionHour(value):
    textbox=builder.get_object("labeldituurverbr")
    textbox.set_text(str(round(value,4)))
#render average consumption value    
def setConsumptionTotal(value):
    textbox=builder.get_object("labeltotaal")
    textbox.set_text(str(round(value,4)))
#render average day consumption value
def setConsumptionDay(value):
    textbox=builder.get_object("labeldag")
    textbox.set_text(str(round(value,4)))
#render average night consumption value
def setConsumptionNight(value):
    textbox=builder.get_object("labelnacht")
    textbox.set_text(str(round(value,4)))
#render all the above with this one function
def renderConsumptions():
    #setConsumptionHour
    if(len(consumptions)>3):
        setConsumptionHour(sum(consumptions[-4:])/4)
    #setConsumptionTotal
    if(len(consumptions)>0):
        setConsumptionTotal(sum(consumptions)/len(consumptions))
    #setConsumptionDay
    consumptionDay = 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]>=420 and times[i]<1320):
            consumptionDay+=consumptions[i]
            j+=1
    if(j==0):
        j=1
    consumptionDay = consumptionDay/j
    setConsumptionDay(consumptionDay)
    #setConsumptionNight
    consumptionNight= 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]<420 or times[i]>1320):
            consumptionNight+=consumptions[i]
            j+=1
    if(j==0):
        j=1
    consumptionNight = consumptionNight/j
    setConsumptionNight(consumptionNight)

    
#############################################Max/Min production/consumption
#render total spendings
def setTotalCosts(value):
    textbox=builder.get_object("labelblah2")
    textbox.set_text(str(round(value,4)))
#render the hour where electricity price was highest
def setMaxPriceHour(value):
    textbox=builder.get_object("ehntry1")
    textbox.set_text(str(value))
#render the hour where electricity price was lowest
def setMinPriceHour(value):
    textbox=builder.get_object("ehntry2")
    textbox.set_text(str(value))
#render the hour where electricity production was highest
def setMaxProductionHour(value):
    textbox=builder.get_object("ehntry3")
    textbox.set_text(str(value))
#render the hour where electricity production was lowest
def setMinProductionHour(value):
    textbox=builder.get_object("uitgavenSmart19")
    textbox.set_text(str(value))
#render the hour where electricity consumption was highest
def setMaxConsumptionHour(value):
    textbox=builder.get_object("ehntry4")
    textbox.set_text(str(value))
#render the hour where electricity consumption was lowest
def setMinConsumptionHour(value):
    textbox=builder.get_object("ehntry4bis")
    textbox.set_text(str(value))
#render the hour where electricity consumption from network was highest
def setMaxNetworkConsumptionHour(value):
    textbox=builder.get_object("ehntry5bis")
    textbox.set_text(str(value))
#render the hour where electricity consumption from network was lowest
def setMinNetworkConsumptionHour(value):
    textbox=builder.get_object("ehntry4bis1")
    textbox.set_text(str(value))
#render all the above with this one function
def renderMaxMinValues():
    #setTotalCosts
    i=0
    totalCost=0
    for i in range(len(times)):
        totalCost += electricityPrices[i]*networkConsumptions[i]
    setTotalCosts(totalCost)
    #setMaxPriceHour & setMinPriceHour
    maxPrice = 0
    minPrice = 0
    maxTime = 0
    minTime = 0
    i=0
    for i in range(len(times)):
        if(electricityPrices[i]>maxPrice):
            maxPrice = electricityPrices[i]
            maxTime = times[i]
        if(electricityPrices[i]<minPrice or minPrice == 0):
            minPrice = electricityPrices[i]
            minTime = times[i]
    hours=str(int(maxTime)/60)
    minutes=str(int(maxTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    setMaxPriceHour( hours+ " : " + minutes)

    hours=str(int(minTime)/60)
    minutes=str(int(minTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes
    setMinPriceHour( hours+ " : " + minutes)

    #setMaxProductionHour & setMinProductionHour
    maxProduction = 0
    minProduction = 0
    maxTime = 0
    minTime = 0
    i=0
    for i in range(len(times)):
        if(productions[i]>maxProduction):
            maxProduction= productions[i]
            maxTime = times[i]
        if(productions[i]<minProduction or minProduction == 0):
            minProduction = productions[i]
            minTime = times[i]
    hours=str(int(maxTime)/60)
    minutes=str(int(maxTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    setMaxProductionHour( hours+ " : " + minutes)

    hours=str(int(minTime)/60)
    minutes=str(int(minTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes
    setMinProductionHour( hours+ " : " + minutes)

    #setMaxConsumptionHour & setMinConsumptionHour
    maxConsumption = 0
    minConsumption = 0
    maxTime = 0
    minTime = 0
    i=0
    for i in range(len(times)):
        if(consumptions[i]>maxConsumption):
            maxConsumption= consumptions[i]
            maxTime = times[i]
        if(consumptions[i]<minConsumption or minConsumption == 0):
            minConsumption = consumptions[i]
            minTime = times[i]
    hours=str(int(maxTime)/60)
    minutes=str(int(maxTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    setMaxConsumptionHour( hours+ " : " + minutes)

    hours=str(int(minTime)/60)
    minutes=str(int(minTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes
    setMinConsumptionHour( hours+ " : " + minutes)

    #setMaxNetworkConsumptionHour & setMinNetworkConsumptionHour
    maxConsumption = 0
    minConsumption = None
    maxTime = 0
    minTime = 0
    i=0
    for i in range(len(times)):
        netCons=consumptions[i]-productions[i]
        if(netCons>maxConsumption):
            maxConsumption= netCons
            maxTime = times[i]
        if(netCons<minConsumption or minConsumption == None):
            minConsumption = netCons
            minTime = times[i]
        else:
            minConsumption = 0
    hours=str(int(maxTime)/60)
    minutes=str(int(maxTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    setMaxNetworkConsumptionHour( hours+ " : " + minutes)

    hours=str(int(minTime)/60)
    minutes=str(int(minTime)%60)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes
    setMinNetworkConsumptionHour( hours+ " : " + minutes)
        
#############################################Production
#render electricity production this hour
def setProductionHour(value):
    textbox=builder.get_object("uitgavenSmart")
    textbox.set_text(str(round(value,4)))
#render average electricity production
def setProductionTotal(value):
    textbox=builder.get_object("uitgavenSmart1")
    textbox.set_text(str(round(value,4)))
#render average electricity production at day
def setProductionDay(value):
    textbox=builder.get_object("uitgavenSmart2")
    textbox.set_text(str(round(value,4)))
#render average electricity production at night
def setProductionNight(value):
    textbox=builder.get_object("uitgavenSmart3")
    textbox.set_text(str(round(value,4)))
#render all the above in this method with this function
def renderProductions():
    #setProductionHour
    if(len(productions)>3):
        setProductionHour(sum(productions[-4:])/4)
    #setProductionTotal
    if(len(productions)>0):
        setProductionTotal(sum(productions)/len(productions))
    #setProductionDay
    productionDay = 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]>=420 and times[i]<1320):
            productionDay+=productions[i]
            j+=1
    if(j==0):
        j=1
    productionDay = productionDay/j
    setProductionDay(productionDay)
    #setProductionNight
    productionNight= 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]<420 or times[i]>1320):
            productionNight+=productions[i]
            j+=1
    if(j==0):
        j=1
    productionNight = productionNight/j
    setProductionNight(productionNight)
#############################################Network consumptions
#render electricity consumption from network this hour
def setConsumptionNHour(value):
    textbox=builder.get_object("uitgavenSmart4")
    textbox.set_text(str(round(value,4)))
#render average electricity consumption from network 
def setConsumptionNTotal(value):
    textbox=builder.get_object("uitgavenSmart5")
    textbox.set_text(str(round(value,4)))
#render electricity consumption from network at day
def setConsumptionNDay(value):
    textbox=builder.get_object("uitgavenSmart6")
    textbox.set_text(str(round(value,4)))
#render electricity consumption from network at night
def setConsumptionNNight(value):
    textbox=builder.get_object("uitgavenSmart7")
    textbox.set_text(str(round(value,4)))
#render all the above with this function
def renderConsumptionsN():
    #setConsumptionNHour
    if(len(networkConsumptions)>3):
        setConsumptionNHour(sum(networkConsumptions[-4:])/4)
    #setConsumptionNTotal
    if(len(networkConsumptions)>0):
        setConsumptionNTotal(sum(networkConsumptions)/len(networkConsumptions))
    #setConsumptionNDay
    consumptionDay = 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]>=420 and times[i]<1320):
            consumptionDay+=networkConsumptions[i]
            j+=1
    if(j==0):
        j=1
    consumptionDay = consumptionDay/j
    setConsumptionNDay(consumptionDay)
    #setConsumptionNNight
    consumptionNight= 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]<420 or times[i]>1320):
            consumptionNight+=networkConsumptions[i]
            j+=1
    if(j==0):
        j=1
    consumptionNight = consumptionNight/j
    setConsumptionNNight(consumptionNight)
#############################################Spendings
#render this hour's spendings 
def setSpendingsHour(value):
    textbox=builder.get_object("uitgavenSmart10")
    textbox.set_text(str(round(value,4)))
#render average spendings  
def setSpendingsTotal(value):
    textbox=builder.get_object("uitgavenSmart12")
    textbox.set_text(str(round(value,4)))
#render average spendings at day
def setSpendingsDay(value):
    textbox=builder.get_object("uitgavenSmart14")
    textbox.set_text(str(round(value,4)))
#render average spendings at night
def setSpendingsNight(value):
    textbox=builder.get_object("uitgavenSmart16")
    textbox.set_text(str(round(value,4)))
#render all the above
def renderSpendings():
    #setSpendingsHour
    if(len(spendings)>3):
        setSpendingsHour(sum(spendings[-4:])/4)
    #setSpendingsTotal
    if(len(spendings)>0):
        setSpendingsTotal(sum(spendings)/len(spendings))
    #setSpendingsDay
    spendingDay = 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]>=420 and times[i]<1320):
           spendingDay+=spendings[i]
           j+=1
    if(j==0):
        j=1
    spendingDay = spendingDay/j
    setSpendingsDay(spendingDay)
    #setSpendingsNight
    spendingNight= 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]<420 or times[i]>1320):
            spendingNight+=spendings[i]
            j+=1
    if(j==0):
        j=1
    spendingNight = spendingNight/j
    setSpendingsNight(spendingNight)
#############################################Electricity price
#render this hour's electricity price
def setPriceHour(value):
    textbox=builder.get_object("uitgavenSmart11")
    textbox.set_text(str(round(value,4)))
#render the average electricity price
def setPriceTotal(value):
    textbox=builder.get_object("uitgavenSmart13")
    textbox.set_text(str(round(value,4)))
#render the average electricity price at day
def setPriceDay(value):
    textbox=builder.get_object("uitgavenSmart15")
    textbox.set_text(str(round(value,4)))
#render the average electricity price at night
def setPriceNight(value):
    textbox=builder.get_object("uitgavenSmart17")
    textbox.set_text(str(round(value,4)))
#render all the above
def renderPrices():
    #setPriceHour
    if(len(electricityPrices)>3):
        setPriceHour(sum(electricityPrices[-4:])/4)
    #setPriceTotal
    if(len(electricityPrices)>0):
        setPriceTotal(sum(electricityPrices)/len(electricityPrices))
    #setPriceDay
    priceDay = 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]>=420 and times[i]<1320):
           priceDay+=electricityPrices[i]
           j+=1
    if(j==0):
        j=1
    priceDay = priceDay/j
    setPriceDay(priceDay)
    #setPriceNight
    priceNight= 0
    i=0
    j=0
    for i in range(len(times)):
        if(times[i]<420 or times[i]>1320):
            priceNight+=electricityPrices[i]
            j+=1
    if(j==0):
        j=1
    priceNight = priceNight/j
    setPriceNight(priceNight)
##############Program functions##############
#render the programs which ID's are in the given list
#@param programListID the list of program ID's from programs that are to be shown
def setProgramRows(programListID):
    programList=builder.get_object("progListStore")
    programList.clear()
    
    progsToAdd=getPrograms(programListID)
    print "ADD THESE PROGRAMS: ",progsToAdd
    print "THESE ARE THE IDS: ", programListID
    print "BOILER CONS: ",instantBoilerConsumption
    if len(progsToAdd)<1:
        return
    for prog in progsToAdd:
        programList.append(prog)

#Get device name, room, consumption, duration and category of the program's
#   which ID's are in the given list
#@param programListID the list containing program ID's
#@return    [(program tuple with ID=1), (program tuple with ID=2),...]
def getPrograms(programListID):
    if(len(programListID)<1):
        programListID.append(0)
        programListID.append(0)
    elif(len(programListID)<2):
        programListID.append(0)
    programs = list(QuerySmarthouse.query1("SELECT Program_ID, Device_name, Room_name, Consumption, Category " \
                  + "FROM program, device, room " \
                  + "WHERE program.Device_ID = device.Device_ID" \
                  + " AND room.Room_ID = program.Room_ID AND Program_ID IN %s" % str(tuple(programListID))))
    #Add program durations in the program tuples
    i=0
    returnList=[]
    for i in range(len(programs)):
        temp = list(programs[i])
        ID= temp[0]
        duration=getProgramDuration(ID)
        temp.pop(0)
        temp.insert(3, duration)
        
        #if device is "boiler" add the instant boiler consumption value
        name = (QuerySmarthouse.query2("SELECT Device_name FROM program, device WHERE program.Program_ID = %s " \
        +"AND program.Device_ID = device.Device_ID", ID))[0][0]
                                 
        if (name == 'verwarming'):
            consumption = instantBoilerConsumption
            temp.pop(2)
            temp.insert(2, consumption)   
        #Sort programs by their duration, from big to small
        j=len(returnList)
        while j>0 and (temp[3]>returnList[j-1][3]):
            j=j-1             
        temp=tuple(temp)
        returnList.insert(j,temp)
   
    #Convert all arguments to strings (chararrays)
    returnList2=[]
    for prog in returnList:
        progL=list(prog)
        newProgL=tuple(map(str,progL))
        returnList2.append(newProgL)
        
    return returnList2

#Return the given program's consumption
#@param programID the program we want the consumption of
#@return    the consumption of the program with ID = programID
def getProgramConsumption(programID):
    consumption = list(QuerySmarthouse.query1("SELECT Consumption " \
                      + "FROM Program " \
                      + "WHERE Program_ID = (%s)" % programID))
    if(len(consumption)>0):
        return list(consumption[0])[0]
    else:
        return 0

#Return the given program's duration, in minutes
#@param programID the program we want the consumption of
#@effect return (amount of programs with ID in program list since program
#        was started)*15
#@return    The duration of the program whose ID = ID
def getProgramDuration(ID):
    i=len(programs)-1
    j=0
    while i >= 0 and (ID in programs[i]) :
        j+=1
        i=i-1
    hours=str(j/4)
    minutes=str((j%4)*15)
    if(len(hours)<2):
        hours="0"+hours
    if(len(minutes)<2):
       minutes = "0"+minutes   
    return( hours+ " : " + minutes)    

#Return the current house consumption
#@param programListID   list containing running programs
#@effect    return Sum(getProgramConsumption(programListID))
#@return the total consumption of all programs with ID's in the given list
def getHouseConsumption(programListID):
    houseConsumption=0
    i=0
    for i in range(len(programListID)):
        programConsumption=getProgramConsumption(programListID[i])
        if(programConsumption>=0):
            houseConsumption += programConsumption
    return houseConsumption

#Return the current house production
#@param time    the current time
#@effect    get production matching current time from the database
#@return    the house production at the given time
#Given time must be in minutes (15, 45, 135,...)
def getHouseProduction(time):
    time=float(time)/60.0
    houseProduction= QuerySmarthouse.query1("SELECT production FROM house_electricity_production WHERE time=%s" %time)
    if(len(houseProduction)>0):
        return list(houseProduction[0])[0]
    else:
        return 0

#Return the current house consumption if it was not smart
#@param time    the current time
#@effect    get the non-smart consumption matching current time
#           from the database
#@return    the average consumption of a normal house at the given time
def getHouseConsumptionNotSmart(time):
    time=float(time)/60.0
    houseConsumptionNotSmart=QuerySmarthouse.query1("SELECT consumption FROM consumption_not_smart WHERE time=%s" %time)
    if(len(houseConsumptionNotSmart)>0):
        return list(houseConsumptionNotSmart[0])[0]
    else:
        return 0


##############Graph plot functions##############
#render current values in the plot and paint the plot
def updatePlot():
    plt=PlotValues.plotValues3(instantTimes, instantConsumptionValues, 'r*-', 'Verbruik (kWh)', instantProductions, 'g*-', 'Productie (kWh)',instantConsumptionNotSmartValues, 'y.-', 'Verbruik zonder SEH (kWh)')
    plotImg=builder.get_object("image1")
    plotImg.clear()
    plotImg.set_from_pixbuf(plt)

#add last consumption values to the plot's consumption array
#@param lastConsumption given last consumption value
def addLastConsumption(lastConsumption):
    if(len(instantConsumptionValues)>0):
        instantConsumptionValues.pop(0)
    instantConsumptionValues.append(lastConsumption)
#add last price values to the plot's prices array
#@param lastPrices given array containing last price values
def addLastPrices(lastPrices):
    for lastPrice in lastPrices:
        if(len(instantPrices)>0):
            instantPrices.pop(0)
        instantPrices.append(lastPrice)
#add last production values to the plot's production array
#@param lastProduction given last production value
def addLastProduction(lastProduction):
    if(len(instantProductions)>0):
        instantProductions.pop(0)
    instantProductions.append(lastProduction)
#add last time values to the plot's production times array
#@param lastTimes given array containing last time values
def addLastTimes(lastTimes):
    for lastTime in lastTimes:
        if(len(instantTimes)>0):
            instantTimes.pop(0)
        lastTime=float(lastTime)/60.0
        if(lastTime<6.0):
            lastTime+=24.0
        instantTimes.append(lastTime)
#add last consumption values without smarthouse to the plot's nonsmart array
#@param lastConsumption given last nonsmart consumption value
def addLastConsumptionNotSmart(lastConsumption):
    if(len(instantConsumptionNotSmartValues)>0):
        instantConsumptionNotSmartValues.pop(0)
    instantConsumptionNotSmartValues.append(lastConsumption)


#Update the data arrays and sensor values with the given data
#@param timeValues  given array containing last time values
#@param sensorValues    given array containing last arrays of sensor values
#@param programListIDs  given array containing last arrays of program ID's
#@param prices  given array containing last electricity price values
#@param boilerCons  given array containing last heating consumptions
#@effect    extend the data arrays with the corresponding given values
def update(timeValues, sensorValues, programListIDs, prices, boilerCons):
    global instantBoilerConsumption, light, temperature
    
    length=len(timeValues)
    if(len(sensorValues) != length or len(programListIDs) != length or len(prices) != length):
        raise Exception("Update arguments must have the same array length!")
                
    i=0
    for i in range(length):
        if (len(times)<1) or (timeValues[i] not in times):   
            consumption= getHouseConsumption(programListIDs[i])+boilerCons[i]
            production= getHouseProduction(timeValues[i])
            consumptionNotSmart = getHouseConsumptionNotSmart(timeValues[i])
            nettoConsumption= consumption-production
            spending= prices[i]*nettoConsumption
            #update data arrays
            consumptions.append(consumption)
            productions.append(production)
            networkConsumptions.append(nettoConsumption)
            spendings.append(spending)
            #graph data
            addLastConsumption(consumption)
            addLastProduction(production)
            addLastConsumptionNotSmart(consumptionNotSmart)
        else:
            timeValues.pop(i)
            sensorValues.pop(i)
            programListIDs.pop(i)
            prices.pop(i)
    #graph data  
    addLastPrices(electricityPrices)
    addLastTimes(timeValues)
    #update data arrays
    times.extend(timeValues)
    programs.extend(programListIDs)
    electricityPrices.extend(prices)

    instantBoilerConsumption = boilerCons[-1]
    if len(sensorValues)>0:
        if len(sensorValues[0])==2:
            light= sensorValues[0][0]
            temperature= sensorValues[0][1]

#Render the last values from the data arrays in the gui
def repaint():
    if(len(times)>0):
        updatePlot()

        #render status values
        setStatusLight(light)
        setStatusTemp(temperature)
        setStatusHeating(instantBoilerConsumption)

        
        setStatusConsumption(consumptions[-1])

        #update the program list
        setProgramRows(programs[-1])

        #render history values
        setTime(times[-1])
        renderConsumptions()
        renderMaxMinValues()
        renderProductions()
        renderConsumptionsN()
        renderSpendings()
        renderPrices()
#reset all data arrays, plot arrays and sensor values
def resetDay():
    global instantBoilerConsumption, light, temperature, instantConsumptionValues, instantPrices,instantProductions,instantTimes, instantConsumptionNotSmartValues,times,consumptions,productions,networkConsumptions,electricityPrices,spendings,programs
    #Delete all array values
    del instantConsumptionValues[:]
    del instantPrices[:]
    del instantProductions[:]
    del instantTimes[:]
    del instantConsumptionNotSmartValues[:]
    
    del times[:]
    del consumptions[:]
    del productions[:]
    del networkConsumptions[:]
    del electricityPrices[:]
    del spendings[:]
    del programs[:]
    #initialise the values for the graph
    instantConsumptionValues.extend([0]*96)
    instantPrices.extend([0]*96)
    instantProductions.extend([0]*96)
    instantTimes.extend([5.99]*96)
    instantConsumptionNotSmartValues.extend([0]*96)
    #initialise data arrays
    times=[]
    consumptions=[]
    productions=[]
    networkConsumptions=[]
    electricityPrices=[]
    spendings=[]
    programs=[]

    #Initialise sensor fields
    temperature=0
    light = 0

    #initialise instant boiler consumption
    instantBoilerConsumption = 0
    repaint()


####################################################################################################################
######################_______________#####################
#####################|Initialise GUI|#####################
######################---------------#####################
if __name__ == '__main__':
    #Initialise the main file
    init()
    #Initialise the interface

    builder = gtk.Builder()
    builder.add_from_file("HomeApp.glade")
    builder.connect_signals(Signals())

    #initialise the values for the graph
    instantConsumptionValues=([0]*96)
    instantPrices=([0]*96)
    instantProductions=([0]*96)
    instantTimes = ([5.99]*96)
    instantConsumptionNotSmartValues = ([0]*96)

    #initialise the data arrays
    times=[]
    consumptions=[]
    productions=[]
    networkConsumptions=[]
    electricityPrices=[]
    spendings=[]
    programs=[]

    #Initialise sensor fields
    temperature=0
    light = 0

    #initialise instant boiler consumption
    instantBoilerConsumption = 0

    ##addLastConsumption(10)
    ##updatePlot()

    #Show the Gui main frame
    window = builder.get_object("StatusWindow")
    window.move(975,500)
    window.show_all()
    window = builder.get_object("History")
    window.move(0,475)
    window.show_all()
    window = builder.get_object("plotWindow")
    window.move(975,0)
    window.show_all()
    window = builder.get_object("RunningPrograms")
    window.move(75,0)
    window.show_all()

#Get last values from main() and call update() then repaint() the gui,
#   then put itself back on the execution stack after 10ms
#@effect update(args) then repaint() then gobject.timeout_add(10, loop)
def loop():
    global counter, prev_counter

    time.sleep(0.01)
    counter_,category1= main(counter,prev_counter)
    thisSensorData= get_current_sensor_data()
    thisTime= get_current_time_minutes(counter_)
    if len(times)>0 and times[-1] >(5.30*60) and times[-1] < (6.00*60):
        time.sleep(10)
        resetDay()
    thisPrograms = get_current_programs(counter_,category1)
    thisPrices = get_current_electricity_price(counter_)
    thisBoilerCons = get_current_boiler_consumption(counter_)
    print 'gui_update_data: ',thisTime,thisSensorData,thisPrograms, thisPrices, thisBoilerCons
    update(thisTime,thisSensorData,thisPrograms, thisPrices, thisBoilerCons)
    print '\n'
    repaint()
    
    gobject.timeout_add(10, loop)


gobject.timeout_add(5000, loop)

gtk.main()

##plotNextValues()
##addLastConsumptionValue(7)
##plotNextValues()
##addLastConsumptionValue(5)
#plotNextValues()






































