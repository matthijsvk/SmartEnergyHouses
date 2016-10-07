# -*- coding: cp1252 -*-
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

import QuerySmarthouse
import QueryPowerData
import PlotValues


######################################
import time
import MySQLdb

import communicatie

import Python_Gams_DagNacht_GeenLocal_functie
import Python_Gams_DagNacht_Local_gn_Curt_functie
import Python_Gams_DagNacht_Local_functie

import Python_Gams_Variabel_GeenLocal_functie
import Python_Gams_Variabel_local_geen_curtail_functie
import Python_Gams_Variabel_inclusief_local_functie


DagNacht_GeenLocal=1
DagNacht_Local_gn_Curt=3
DagNacht_Local=2

Variabel_GeenLocal=4
Variabel_Local_gn_Curt=6
Variabel_Local=5

#################   CHOOSE YOUR PROGRAM  #################

huidige_programma= Variabel_Local

piper_poort= 'COM3'

##########################################################


#INDEX
#
#Main functions r.66
    #init() r.142
    #gui update functions r.175
    #program sorting & arduino controlling r
#
#
#
#

### MAIN FUNCTIONS ###
    
####################################################################3
########################3########################3########################3

arduino1= 1 #enkel arduino met nr 1
arduino2= 2

counter = 0 #global variables needed for main()
prev_counter= 10
prev_programs_on,prev_category1= [],[]
day_start=6.00
day_end= 5.45
time_scheme= []
program_time_scheme= []
pheatinglst= []
pricelst= []
#database=[]#Voor tests
##dagtarief= 10
##nachttarief= 5

#PINS
tv_switch= 14
#light_upstairs_switch=15
#light_downstairs_switch=15
lights_potmeter=15
light_sensor_pin=16
temp_sensor_pin=17

tv_pin=2 
heating_pin= 3
light_upstairs_pin= 4
light_downstairs_pin= 5
fornuis_pin=6
fridge_pin=7
#speakerpin= 8 # wordt gebruikt door arduino
wash_mach_pin= 9
auto_pin=10
dish_wash_pin= 11

device_pins= [2,3,4,5,6,7,8,9,10,11]  #0 and 1 are used for data transmission

#PRORAM NRS
light_upstairs_program=4
light_downstairs_program=5
light_analog_program=6

wash_mach_program= 9
dish_wash_program= 11
fridge_program= 7
tv_program=2
heating_program=3

digital_programs= [dish_wash_program, wash_mach_program, fridge_program, tv_program,light_upstairs_program,light_downstairs_program]  #3=dishwash; 4=wash_mach; 5= tv
#expansion: analog programs. e.g. dimmer
switch_digital_programs_list= {tv_switch:tv_program}
switch_analog_programs_list= {lights_potmeter:light_analog_program}#, light_upstairs_switch:light_upstairs_program, light_downstairs_switch:light_downstairs_program}


def get_device_pins(program): 
    'return alle pinnen die bij een bepaald programma horen (in een lijst)' 
    if type(program)==int:
        if program==light_upstairs_program:
            return [light_upstairs_pin]
        elif program==light_downstairs_program:
            return [light_downstairs_pin]
        
        elif program==dish_wash_program:
            return [dish_wash_pin]
        elif program==wash_mach_program:
            return [wash_mach_pin]
        elif program==fridge_program:
            return [fridge_pin]
        elif program== tv_program: #tv_program= 6; tv_switch = 19
            return [tv_pin]
    elif len(program)==2:
        if program[0]== light_analog_program:
            return [light_upstairs_pin,light_downstairs_pin]
    
        elif program[0]== heating_program:
            return [heating_pin] #heating pin = 3
    #####return QueryDatabase.query1("SELECT Device_pin FROM Program WHERE Program_id= '(%d)'",program) #####



#####   INIT  #####

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
    
    #test of alle pins werken
    arduinoNr=1
    ###communicatie.pin_control(arduinoNr,device_pins,1)
    communicatie.pin_control(arduinoNr,device_pins,0)
    
    print 'done \n'


##### Gui update functions #####
def get_current_sensor_data():
    sensor_data= []
    for data in sensor_data_interpreted:
        if (type(data)==int or type(data)==float): #append all data not in category1 ->#enkel licht en temperatuur
            sensor_data.append(data)
    return [sensor_data] 

#Return the current relative daytime in minutes
def get_current_time_minutes(counter):
    current_time= get_current_time(counter)    
    return [(current_time)*60]

def get_current_electricity_price(counter):   
    return [get_electricity_price(counter)]

def get_current_programs(counter,category1):
            
    return [get_all_programs_on(counter,category1)]

def get_current_boiler_consumption(counter):
    current_programs_on= get_program_IDs_now(counter)
    if len(current_programs_on)>0:
        boiler_cons=0
        for program in current_programs_on:
            if type(program)==list:
                if program[0]==heating_program:
                    return [program[1]*0.001]
        return [0]
         #boiler consumption is the first value
    else: return [0]


#### Program Sorting & Arduino Controlling ####

def sort_programs(programs_on, prev_programs_on, category1, prev_category1):
    global digital_programs
    
    if ((category1==prev_category1) and (programs_on==prev_programs_on)): #save time by leaving everything as is if nothing changed
        print 'same as previous state; not controlling'
        return [],[],[]

    #get new programs to be turned on and previous programs to be turned off. The other programs are the same as before.
    programs_on, programs_off= get_programs(programs_on, prev_programs_on)
    category1_programs_on, category1_analog_programs_on, category1_programs_off= get_category1_programs(category1, prev_category1)                 
    
    #splitsen in analoge/digitale programma's: aan/uit of met tussenstadia (bv licht vs verwarming)            
    programs_on_digital=[]
    programs_on_analog=[]
    programs_off_digital=[]
                
    for program in programs_on:  #new programs to be turned on
        if program in digital_programs:
            programs_on_digital.append(program)
        else:
            programs_on_analog.append(program)

    for category1_analog_program in category1_analog_programs_on:
        programs_on_analog.append(category1_analog_program)
        
    for category1_program in category1_programs_on: #all category 1 programs are digital (1/0)
        programs_on_digital.append(category1_program)
    

    for program in programs_off:#programs to be turned off
        programs_off_digital.append(program)
        
    for program in category1_programs_off:
        programs_off_digital.append(program)
                                   
    return programs_on_digital,programs_on_analog,programs_off_digital

def control_arduino(arduinoNr,programs_on_digital,programs_on_analog,programs_off_digital):
    
    #turn programs on/off
    if len(programs_off_digital)>0:
        arduino_turn_digital_programs_off(arduinoNr,programs_off_digital)

    if len(programs_on_digital)>0:
        arduino_turn_digital_programs_on(arduinoNr,programs_on_digital) 
        
    if len(programs_on_analog) > 0:
        arduino_turn_analog_programs_on(arduinoNr,programs_on_analog)
        

# Subfunctions of control_arduino #
                                   
def get_category1_programs(category1, prev_category1):
    category1_programs_on=[]
    category1_programs_off= []#programs that need to be turned off
    category1_analog_programs_on= []
    
    if category1!= prev_category1:
        
        for switch in category1: # remove all switches of which the state hasn't changed
            if switch in prev_category1: 
                category1.remove(switch)
    
        for switch in category1: #New states: get programs that belongs to each switch and add them to category1_programs_on/off
            switch_programs= get_programs_switch(switch)
            for switch_program in switch_programs:
                if switch_program in switch_digital_programs_list.values(): #only use if the switchprogram exists
                    if switch[1]==1:
                        category1_programs_on.append(switch_program)
                    else:
                        category1_programs_off.append(switch_program)
                        
                elif (len(switch_program)==2 and switch_program[0] in switch_analog_programs_list):
                    if switch_program[1]==0:
                        category1_programs_off.append(switch_program[0])
                    else:
                        category1_analog_programs_on.append(switch_program)
                
    else: pass                    
    return category1_programs_on, category1_analog_programs_on, category1_programs_off

def get_programs(programs_on, prev_programs_on):
    programs_off= []#programs that need to be turned off
    
    if programs_on!=prev_programs_on: #save time by not sending commands if same as before
        
        for program in prev_programs_on: #turn programs off that stopped
            if program not in programs_on:
                programs_off.append(program)
                
        for program in programs_on: #only turn new programs on
            if program in prev_programs_on:
                programs_on.remove(program)
                
    return programs_on, programs_off

    
def arduino_turn_digital_programs_on(arduinoNr,programs_on_digital):
    'turn all the pins from these programs on'
    on_pins = [] #pins for each device
    for program in programs_on_digital:
        device_pins= get_device_pins(program)
        for pin in device_pins:
            on_pins.append(pin)

    communicatie.pin_control(arduinoNr,on_pins,1) 

def arduino_turn_digital_programs_off(arduinoNr,programs_off_digital):
    'turn all the pins from these programs off'
    off_pins = [] #pins for each device
    for program in programs_off_digital:
        device_pins= get_device_pins(program)
        for pin in device_pins:
            off_pins.append(pin)
            
    communicatie.pin_control(arduinoNr,off_pins,0) 
    
def arduino_turn_analog_programs_on(arduinoNr,programs_on_analog):
    'turn all the pins from these programs on with the right value'
    on_pins = [] #pins for each device
    values= []
    
    for program in programs_on_analog:
        on_pins.append(get_device_pins(program))
        if program[0]==heating_program:
            values.append(communicatie.mapp(program[1],0,2000,0,253))
        else:
            value.append(communicatie.mapp(program[1],0,1025,0,253))
   
    for i in range(len(programs_on_analog)):
        communicatie.analog_pin_control(arduinoNr,on_pins[i],values[i])


def get_program_IDs_now(counter):
    return progam_time_scheme[counter]

def save_to_database(currrent_quarter,sensor_data,verbruik_nu): 
    'sla alle huidige gegevens op in de database om ze later te plotten'
                                   
    global database#test
    database.append([currrent_quarter,sensor_data,verbruik_nu])#test

def get_all_programs_on(counter,category1):
    all_programs_on=[]
    programs_on=get_program_IDs_now(counter)
    for program in programs_on:
        if type(program)==int:
            all_programs_on.append(program)
        elif len(program)==2:
            all_programs_on.append(program[0])
        
    for switch in category1:
        switch_programs= get_programs_switch(switch)
        
        for switch_program in switch_programs:
            if type(switch_program)==int:
                if switch[1]==1:
                    all_programs_on.append(switch_program)
            elif len(switch_program)==2:
                if switch_program[1]!=0:
                    all_programs_on.append(switch_program[0])
            
    return all_programs_on   

## geïmproviseerde functies (zonder database) ###
def get_programs_switch(switch):
    global switch_programs_list
    'return programma"s die bij een switch horen '
    if switch[0] in switch_digital_programs_list.keys():
        return [switch_digital_programs_list[switch[0]]]
    elif switch[0] in switch_analog_programs_list:
        switch_analog_prog_on=[]
        for prog in [switch_analog_programs_list[switch[0]]]:
            switch_analog_prog_on.append([prog,switch[1]])
        return switch_analog_prog_on
    else: return [light_downstairs_program]

def get_analog_value(program): #currently only used for heating, could be expanded with e.g. dimmer
    'return analoge waarde die hoort bij dit programma (bv verwarming op "hoog" programma -> 900)'
    if program not in digital_programs:
        return communicatie.mapp(program,0,2000,0,253) #heating
    #expansion:
    #if program in analog_programs:
    #   return analog_programs[program]
    return 0


                 
######################## TIME & GAMS functions ########################

def GAMS_init():
    # 1. Setup Gams Workspace
    # ws = gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.ShowLog)
    ws = gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.Off)
    # 2. Initialize Job
    job = ws.add_job_from_file('optimalisatie_energie.gms')
    return job

def time_to_quarters(time): #time is a float between 0.0 and 24.0
    return int(time/0.25 - day_start/.25)                                       

def get_current_time(counter):
    return time_scheme[counter]%24.0

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
    for i in range(len(pheatinglst)): #per kwartier
        time_scheme.append(day_start+ i*0.25)

    for i in range(len(time_scheme)):
        now_programs= []

        now_programs.append([heating_program,int(pheatinglst[i])]) #this is always the first value
        if int(fridgelst[i])==1:
            now_programs.append(fridge_program)
        if int(washmachlst[i])==1:
            now_programs.append(wash_mach_program)
        if int(dishwashlst[i])==1:
            now_programs.append(dish_wash_program)

        if time_scheme[counter]> 16.00:  #niet- GAMS programma's
            now_programs.append(light_downstairs_program)
            now_programs.append(light_upstairs_program)
        if time_scheme[counter]==17.00:
            now_programs.append(tv_program)
        
        program_time_scheme.append(now_programs)

    return program_time_scheme
        
def get_electricity_price(counter):
    if len(pricelst)>counter:
        return pricelst[counter]*0.001
    else: return 0
    
##    if current_time>22.00 or current_time <8.00:
##        electricity_price= nachttarief #nachttarief
##    else:
##        electricity_price= dagtarief #dagtarief
            
    return electricity_price


########################  MAIN  ########################

def main(countertje,prev_countertje):
    global sensor_data_interpreted,counter,prev_counter,prev_programs_on,prev_category1#,prev_counter#test
    
    counter= countertje
    prev_counter= prev_countertje
    
    run = True
    programs_on,category1= [],[]
    
    correction=1
    
    while counter== prev_counter:
        print 'gui updated'  #GUI.update(time_scheme[counter],sensor_data_interpreted,all_programs_on, electricity_price)
        counter+=1
        counter= counter%96
        if counter==0: #if the day starts again.
            print 'Day ended. Starting new day...'
            communicatie.pin_control(arduinoNr,device_pins,0)
            resetDay()
            time.sleep(3)
        time.sleep(0.1)

    
    while counter > prev_counter+ 1:
        #correction+=1
        counter= counter- correction
    prev_counter= counter
    
    current_time= get_current_time(counter)
        
    print 'The current time is: ', time_scheme[counter]
    print 'counter_number: ',counter 
    
    if counter>= len(progam_time_scheme): #als alle programma's voor vandaag afgerond zijn, sluit af
        return
    
    #get sensor data
    arduinoNr= 1 #only ask data from first SEH
    sensor_data_interpreted, category1= communicatie.receive_data_arduino(arduinoNr) #category1 is een list met switches en de gelezen waarden (1/0)
    sensor_data_interpreted.append(category1)

    #get programs
    programs_on= get_program_IDs_now(counter)
    print 'smart_programs_on: ', programs_on

    all_programs_on= get_all_programs_on(counter,category1) #add programs turned on by switches
    print 'all programs on: ', all_programs_on
    
    print 'values: ',current_time, sensor_data_interpreted, all_programs_on,'\n'
        
    ##control the first SEH
    programs_on_digital,programs_on_analog,programs_off_digital= sort_programs(programs_on, prev_programs_on, category1, prev_category1)
##    print 'digi_on:', programs_on_digital
##    print 'analog_on: ',programs_on_analog,
##    print 'prog_off: ', programs_off_digital
    arduninoNr= arduino1 #control first arduino
    control_arduino(arduinoNr,programs_on_digital,programs_on_analog,programs_off_digital)

    ######  Control second SEH  #####
##      arduinoNr= arduino2 #control second arduino
##      programs_on_digital,programs_on_analog,programs_off_digital)= .............
##      control_arduino(arduinoNr,programs_on_digital,programs_on_analog,programs_off_digital)
    
    #save if state of programs_on or category1 has changed
    if prev_programs_on != programs_on: 
        prev_programs_on = programs_on
    if prev_category1 != category1:
        prev_category1 = category1
        
    if prev_counter!= counter:
        prev_counter=counter
    print 'main  loop done'
    return counter, category1


####################################################################3
########################3########################3########################3

#    GUI FUNCTIONS    #
    
####################################################################3
########################3########################3########################3

class Signals:

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("HomeApp.glade")

    def showPrograms(self, button):
        window = builder.get_object("RunningPrograms")
        #builder.get_object("StatusWindow").hide()
        window.show()

    def hidePrograms(self, button):
        window = builder.get_object("RunningPrograms")
        window.hide()
        #builder.get_object("StatusWindow").show()

    def showHistory(self, button):
        window = builder.get_object("History")
        #builder.get_object("StatusWindow").hide()
        window.show()

    def hideHistory(self, button):
        window = builder.get_object("History")
        window.hide()
        #builder.get_object("StatusWindow").show()

    def setLights(self, toggleButton):
        button=builder.get_object("lightButton")
        if(button.get_active() == True):
            button.set_label("Aan")
        else:
            button.set_label("Uit")
        

########################################

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
def setStatusLight(value):
    textbox=builder.get_object("entry4")
    if(value == True):
        textbox.set_text("aan")
    else:
        textbox.set_text("uit")

def setStatusTemp(value):
    textbox=builder.get_object("entry1")
    textbox.set_text(str(value))

def setStatusHeating(value):
    textbox=builder.get_object("entry5")
    if(value == True):
        textbox.set_text("aan")
    else:
        textbox.set_text("uit")

def setStatusConsumption(value):
    textbox=builder.get_object("entry3")
    textbox.set_text(str(value))

#############################################House consumptions
def setConsumptionHour(value):
    textbox=builder.get_object("labeldituurverbr")
    textbox.set_text(str(value))
    
def setConsumptionTotal(value):
    textbox=builder.get_object("labeltotaal")
    textbox.set_text(str(value))

def setConsumptionDay(value):
    textbox=builder.get_object("labeldag")
    textbox.set_text(str(value))

def setConsumptionNight(value):
    textbox=builder.get_object("labelnacht")
    textbox.set_text(str(value))
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
def setTotalCosts(value):
    textbox=builder.get_object("labelblah2")
    textbox.set_text(str(value))
    
def setMaxPriceHour(value):
    textbox=builder.get_object("ehntry1")
    textbox.set_text(str(value))

def setMinPriceHour(value):
    textbox=builder.get_object("ehntry2")
    textbox.set_text(str(value))

def setMaxProductionHour(value):
    textbox=builder.get_object("ehntry3")
    textbox.set_text(str(value))

def setMinProductionHour(value):
    textbox=builder.get_object("uitgavenSmart19")
    textbox.set_text(str(value))

def setMaxConsumptionHour(value):
    textbox=builder.get_object("ehntry4")
    textbox.set_text(str(value))

def setMinConsumptionHour(value):
    textbox=builder.get_object("ehntry4bis")
    textbox.set_text(str(value))

def setMaxNetworkConsumptionHour(value):
    textbox=builder.get_object("ehntry5bis")
    textbox.set_text(str(value))

def setMinNetworkConsumptionHour(value):
    textbox=builder.get_object("ehntry4bis1")
    textbox.set_text(str(value))

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
        if(electricityPrices[i]<minPrice and minPrice != 0):
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
        if(productions[i]<minProduction and minProduction != 0):
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
        if(consumptions[i]<minConsumption and minConsumption != 0):
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
        if(netCons<minConsumption and minConsumption != None):
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
def setProductionHour(value):
    textbox=builder.get_object("uitgavenSmart")
    textbox.set_text(str(value))
    
def setProductionTotal(value):
    textbox=builder.get_object("uitgavenSmart1")
    textbox.set_text(str(value))

def setProductionDay(value):
    textbox=builder.get_object("uitgavenSmart2")
    textbox.set_text(str(value))

def setProductionNight(value):
    textbox=builder.get_object("uitgavenSmart3")
    textbox.set_text(str(value))

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
def setConsumptionNHour(value):
    textbox=builder.get_object("uitgavenSmart4")
    textbox.set_text(str(value))
    
def setConsumptionNTotal(value):
    textbox=builder.get_object("uitgavenSmart5")
    textbox.set_text(str(value))

def setConsumptionNDay(value):
    textbox=builder.get_object("uitgavenSmart6")
    textbox.set_text(str(value))

def setConsumptionNNight(value):
    textbox=builder.get_object("uitgavenSmart7")
    textbox.set_text(str(value))

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
def setSpendingsHour(value):
    textbox=builder.get_object("uitgavenSmart10")
    textbox.set_text(str(value))
    
def setSpendingsTotal(value):
    textbox=builder.get_object("uitgavenSmart12")
    textbox.set_text(str(value))

def setSpendingsDay(value):
    textbox=builder.get_object("uitgavenSmart14")
    textbox.set_text(str(value))

def setSpendingsNight(value):
    textbox=builder.get_object("uitgavenSmart16")
    textbox.set_text(str(value))

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
def setPriceHour(value):
    textbox=builder.get_object("uitgavenSmart11")
    textbox.set_text(str(value))
    
def setPriceTotal(value):
    textbox=builder.get_object("uitgavenSmart13")
    textbox.set_text(str(value))

def setPriceDay(value):
    textbox=builder.get_object("uitgavenSmart15")
    textbox.set_text(str(value))

def setPriceNight(value):
    textbox=builder.get_object("uitgavenSmart17")
    textbox.set_text(str(value))

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
    
def setProgramRows(programListID):
    
    programList=builder.get_object("progListStore")
    programList.clear()
    
    progsToAdd=getPrograms(programListID)
    print "ADD THESE PROGRAMS: ",progsToAdd
    print "THESE ARE THE IDS: ", programListID
    if len(progsToAdd)<1:
        return
    for prog in progsToAdd:
        programList.append(prog)
##def getPrograms(ID):
##    return [("hey", "lol", 9000, 10, 1), ("hey2", "lol", 9000, 10, 1)]
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
        temp.pop(0)
        temp.insert(3, getProgramDuration(ID))
        
        #if device is "boiler" add the instant boiler consumption value
        name = (QuerySmarthouse.query2("SELECT Device_name FROM program, device WHERE program.Program_ID = %s " \
        +"AND program.Device_ID = device.Device_ID", ID))[0][0]
                                 
        if name == "boiler":
            consumption = instantBoilerConsumption
            temp.pop(2)
            temp.insert(2, consumption)
            
        returnList.append(tuple(temp))
    #Convert all arguments to strings (chararrays)
    returnList2=[]
    for prog in returnList:
        progL=list(prog)
        newProgL=tuple(map(str,progL))
        returnList2.append(newProgL)
        
    return returnList2
##def getProgramConsumption(ID):
##    return 9000
def getProgramConsumption(programID):
    consumption = list(QuerySmarthouse.query1("SELECT Consumption " \
                      + "FROM Program " \
                      + "WHERE Program_ID = (%s)" % programID))
    if(len(consumption)>0):
        return list(consumption[0])[0]
    else:
        return 0

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

def getHouseConsumption(programListID):
    houseConsumption=0
    i=0
    for i in range(len(programListID)):
        programConsumption=getProgramConsumption(programListID[i])
        if(programConsumption>=0):
            houseConsumption += programConsumption
    return houseConsumption

#Time in minutes (15, 45, 135,...)
def getHouseProduction(time):
    time=float(time)/60.0
    houseProduction=QuerySmarthouse.query1("SELECT production FROM house_electricity_production WHERE time=%s" %time)
    if(len(houseProduction)>0):
        return list(houseProduction[0])[0]
    else:
        return 0

##def getInstantConsumption(programListID):
##    return QuerySmarthouse.query2("SELECT SUM(`Consumption`) FROM Program WHERE Program_ID in (%s)", programListID)
##
##def getAvgConsumption1():
##    return QuerySmarthouse.query1("SELECT AVG(`Consumption`) FROM Energycons_house WHERE DATEDIFF(minute, Timestamp, GETDATE()) >= 6 AND DATEDIFF(minute, Timestamp, GETDATE()) <= 12")
##
##def getAvgConsumption2():
##    return QuerySmarthouse.query1("SELECT AVG(`Consumption`) FROM Energycons_house WHERE DATEDIFF(minute, Timestamp, GETDATE()) >= 12 AND DATEDIFF(minute, Timestamp, GETDATE()) <= 18")
##
##def getAvgConsumption3():
##    return QuerySmarthouse.query1("SELECT AVG(`Consumption`) FROM Energycons_house WHERE DATEDIFF(minute, Timestamp, GETDATE()) >= 18 AND DATEDIFF(minute, Timestamp, GETDATE()) <= 24")
##
##def getMaxConsumption():
##    return QuerySmarthouse.query1("SELECT MAX(`Consumption`) FROM Energycons_house WHERE DATEDIFF(minute, Timestamp, GETDATE()) <= 6")
##
##
##def getMaxConsumptionHour():
##    return QuerySmarthouse.query1("SELECT Time(Timestamp) FROM Energycons_house WHERE DATEDIFF(minute, Timestamp, GETDATE()) <= 6")

##############Graph plot functions##############
def updatePlot():
    plt=PlotValues.plotValues2(instantTimes, instantConsumptionValues, 'r*-', 'Verbruik (kWh)', instantProductions, 'g*-', 'Productie (kWh)')
    plotImg=builder.get_object("image1")
    plotImg.clear()
    plotImg.set_from_pixbuf(plt)
    
def addLastConsumption(lastConsumption):
    if(len(instantConsumptionValues)>0):
        instantConsumptionValues.pop(0)
    instantConsumptionValues.append(lastConsumption)
def addLastPrices(lastPrices):
    for lastPrice in lastPrices:
        if(len(instantPrices)>0):
            instantPrices.pop(0)
        instantPrices.append(lastPrice)
def addLastProduction(lastProduction):
    if(len(instantProductions)>0):
        instantProductions.pop(0)
    instantProductions.append(lastProduction)
def addLastTimes(lastTimes):
    for lastTime in lastTimes:
        if(len(instantTimes)>0):
            instantTimes.pop(0)
        if(lastTime<6):
            lastTime+=24
        instantTimes.append(float(lastTime)/60.0)
        
    

########################################
##def getQuarterhourlyAVGLoads():
##    return QueryPowerData.query1("SELECT Time(timestamp), AVG(`load`) FROM loads GROUP BY Time(timestamp)")
##
##def getAVGLoad():
##    return QueryPowerData.query1("SELECT AVG(`load`)* FROM loads")
##########################################


def update(timeValues, sensorValues, programListIDs, prices, boilerCons):
##    programListIDs= program_time_scheme
##    boilercons= pheatinglst
##    prices= pricelst
    
    length=len(timeValues)
    if(len(sensorValues) != length or len(programListIDs) != length or len(prices) != length):
        raise Exception("Update arguments must have the same array length!")
                
    i=0
    for i in range(length):
        if (len(times)<1) or (timeValues[i] not in times):   
            consumption= getHouseConsumption(programListIDs[i])+boilerCons[i]
            production= getHouseProduction(timeValues[i])
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
    print "THIS TIME VALUE IS ", times
    programs.extend(programListIDs)
    electricityPrices.extend(prices)

    instantBoilerConsumption = boilerCons[-1]

    #TODO: sensorValues, disassemble and put in arrays

def repaint():
    if(len(times)>0):
        updatePlot()

        #render status values
        #setStatusLight(light)
        #setStatusTemp(temperature)
        #setStatusHeating(heating)

        
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

def resetDay():
    #initialise the values for the graph
    instantConsumptionValues=([0]*20)
    instantPrices=([0]*20)
    instantProductions=([0]*20)
    instantTimes = ([0]*20)

    #initialise data arrays
    del times[:]
    del consumptions[:]
    del productions[:]
    del networkConsumptions[:]
    del electricityPrices[:]
    del spendings[:]
    del programs[:]

    #Initialise sensor fields
    temperatureOutside = 0
    temperatueInside = 0
    light = False

    #initialise instant boiler consumption
    instantBoilerConsumption = 0
    repaint()


##########################################################
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
    instantConsumptionValues=([0]*20)
    instantPrices=([0]*20)
    instantProductions=([0]*20)
    instantTimes = ([0]*20)

    #initialise the data arrays
    times=[]
    consumptions=[]
    productions=[]
    networkConsumptions=[]
    electricityPrices=[]
    spendings=[]
    programs=[]

    #Initialise sensor fields
    temperatureOutside = 0
    temperatueInside = 0
    light = False

    #initialise instant boiler consumption
    instantBoilerConsumption = 0

    #for testing purposes

    ##addLastConsumption(10)
    ##updatePlot()

    #Show the Gui main frame

    builder.get_object("plotWindow").show_all()
    builder.get_object("RunningPrograms").show_all()
    builder.get_object("History").show_all()
    builder.get_object("StatusWindow").show_all()


def loop():
    global counter, prev_counter

#testing
    #addLastConsumptionValues([7,5,3,10,18])
    
    time.sleep(0.01)
    counter_,category1= main(counter,prev_counter)
    thisSensorData= get_current_sensor_data()
    thisTime= get_current_time_minutes(counter_)
    thisPrograms = get_current_programs(counter_,category1)
    thisPrices = get_current_electricity_price(counter_)
    thisBoilerCons = get_current_boiler_consumption(counter_)
    print 'update_data: ',thisTime,thisSensorData,thisPrograms, thisPrices, thisBoilerCons
    #update(thisTime,thisSensorData,thisPrograms, thisPrices, thisBoilerCons)

    #update([15], [[]], [[1,2,3,4,5]], [300], [0.02])
    #update([15,700,1400], [[],[],[]], [[1,1,1,1],[1,1,1,1],[1,1,1,1]], [300,250,200])
    #repaint()
    
    gobject.timeout_add(10, loop)

gobject.timeout_add(10, loop)

gtk.main()

##plotNextValues()
##addLastConsumptionValue(7)
##plotNextValues()
##addLastConsumptionValue(5)
#plotNextValues()



















