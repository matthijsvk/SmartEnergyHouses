import serial
import time
import MySQLdb
#import database

#arduinoNr= 1
CCU_IP=253

pwm_pins= [3,5,6,9,10,11]

DATAREQUEST=100; #commands
PIN_CONTROL_COMMAND=101
ANALOG_PIN_CONTROL_COMMAND= 102
PIN_STATE_REQUEST= 103

SENSOR_DATA_CHECK= DATAREQUEST + 10 #checks
PIN_CONTROL_CHECK = PIN_CONTROL_COMMAND + 10
ANALOG_PIN_CONTROL_CHECK = ANALOG_PIN_CONTROL_COMMAND + 10

TEMPERATURE= 90 #sensor types
LIGHT=91
SOLAR=92
POTMETER= 94
SWITCH=95

EMPTY= 12
MESSAGE_LENGTH= 15

sensor_types,sensor_list= [],[]
poortje='COM3'
   
def init(poort='COM3'):
    global arduino,sensor_types,sensor_lists, poortje
    poortje= poort
    
    sensor_types,sensor_list= get_sensor_lists(1)
    arduino = serial.Serial(poort, 9600, timeout=10)
    time.sleep(2)

def close():
    global arduino
    arduino.close()

#command functions
def receive_data_arduino(arduinoNr):
    "receive data from the arduino "
    sensor_data_interpreted,category1= interpret_sensor_data(arduinoNr) #interpret data of arduino i
    return sensor_data_interpreted,category1 #a list of sensorvalues for the arduino

def get_pin_states(arduinoNr):
    command= [CCU_IP, arduinoNr, PIN_STATE_REQUEST]+ [EMPTY]*(MESSAGE_LENGTH-3)
    arduino.write(str(command))
    pin_states= arduino.readline()
    
    return convert_wireless_to_list(pin_states)

def pin_control(arduinoNr,pinnrs,onOff):
    print'pincontrol',pinnrs, onOff
    'deze functie zet pinnen aan of uit. arduinoNr is int, pinnrs is een list, onOff is 0 or 1 (dus int)'
    
    onOff+= 254
    
    command= [CCU_IP, arduinoNr, PIN_CONTROL_COMMAND] + pinnrs + [onOff] + [EMPTY]*(MESSAGE_LENGTH-3-len(pinnrs)-1)
    arduino.write(str(command))
    time.sleep(0.2)

def analog_pin_control(arduinoNr,pinnrs,value):
    print 'analog_pincontrol',pinnrs
    'deze functie zet pinnen aan of uit. arduinoNr is int, pinnrs is een list, onOff is 0 or 1 (dus int)'
    for pin in range(len(pinnrs)):
        if pinnrs[pin] not in pwm_pins:
            pinnrs[pin]=10 #pin 10 is not used for anything
    
    command= [CCU_IP, arduinoNr, ANALOG_PIN_CONTROL_COMMAND] + pinnrs + [value] + [EMPTY]*(MESSAGE_LENGTH-3-len(pinnrs)-1)
    arduino.write(str(command))
    time.sleep(0.2)
    

#subfunctions of command functions    
def interpret_sensor_data(arduinoNr):
    
    sensor_list,sensor_types=  get_sensor_lists(arduinoNr) 
    sensor_data= get_sensor_data(arduinoNr,sensor_list)
    
    sensor_data_interpreted= []
    category1=[]
    
##    if len(sensor_list)!= len(sensor_types):
##        print 'dit kan niet'
    if len(sensor_list)!=len(sensor_data):
        while len(sensor_data)<len(sensor_list):
            sensor_data.append(0)
    
    for i in range(len(sensor_list)):
        if sensor_data[i]>70:
            sensor_data[i] = mapp(sensor_data[i],70,256,70,1023) #map to get back the range from 0-1023
        
        if sensor_types[i]!= SWITCH:
            sensor_data_interpreted.append(interpret_sensor(sensor_data[i],sensor_types[i]))  
        else:
            category1.append([sensor_list[i], interpret_sensor(sensor_data[i],sensor_types[i])])
    return sensor_data_interpreted,category1

def get_sensor_data(arduinoNr,sensor_list):
    'returns a list with all the sensor_readings from this house'
    
    global arduino,poortje
    pinnrs= sensor_list #TEST
    
    command= [CCU_IP, arduinoNr, DATAREQUEST] + pinnrs + [EMPTY]*(MESSAGE_LENGTH-3-len(pinnrs))
    print 'command', command
    string='testjearntisars'
    arduino.write(str(command))
    string = arduino.readline()
    if len(string)<5:
        string='testjearntisars'

    resend= True
    if (string[0]==str(arduinoNr) and string[2:5]==str(CCU_IP)):
        resend= False
        
    while resend==True:
        arduino.close()
        time.sleep(2)
        arduino = serial.Serial(poortje, 9600, timeout=3)
        time.sleep(2)
        print 'resending command...'
        arduino.write(str(command))
        string = arduino.readline()
        if len(string)<5:
            string='testjearntisars'
        
        if (string[0]==str(arduinoNr) and string[2:5]==str(CCU_IP)):
            resend= False
    print string
    return convert_wireless_to_list(string)


def interpret_sensor(sensor_reading,sensor_type):

    #temperatures to degrees Celcius
    if sensor_type== TEMPERATURE:
        sensor_interpreted= round(sensor_reading*5*100/1024.0,2)
        
    #lightlvl
    elif sensor_type== LIGHT:
        lightlvl= sensor_reading
        sensor_interpreted= lightlvl
    
    #solar panel production
    elif sensor_type== SOLAR:
        C=0.2*4  #panels output 0.2 Amps, can be changed for real panels
        solarProduction= C* sensor_reading/5.0*4 #the max value (4 volts) is 1023/5*4
        sensor_interpreted= solarProduction

    elif sensor_type== POTMETER:
        sensor_interpreted= sensor_reading

    elif sensor_type== SWITCH:
        if sensor_reading>1000:
            sensor_interpreted=1
        else:
            sensor_interpreted=0
                             
    else: sensor_interpreted= 'error in data interpretation'
    
    return sensor_interpreted

def convert_wireless_to_list(string):
    lst = list(string[:])
    lst2  = []
    tmp = ''
    i = 0
    #print lst
    while i< len(lst):    # verwijderen van alle spaties
        if lst[i] == ' ':
            del lst[i]
            lst2.append(tmp)
            tmp = ''
            i -= 1
        else:
            tmp += lst[i]
        i += 1
    if lst2 == '':          # verwijderen van evt. begin temp
        del lst2[0]
    i = 0
    while i < 3:            # verwijderen van header
        del lst2[0]
        i += 1
    i = 0
    while i < len(lst2):    # verwijderen van overbodige nullen en conversie naar int
        if lst2[i] == str(EMPTY):
            del lst2[i]
        else:
            lst2[i] = int(lst2[i])
            i += 1
    return lst2
        
def mapp( x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;   


###### NOG TE BEKIJKEN ######

def get_sensor_lists(arduinoNr):
    return [14,15,16,17],[SWITCH,SWITCH,LIGHT,TEMPERATURE]#test

##    sensor_pin_list= []
##    sensor_types_list= []
##    
##    temp_sensor_pins = QuerySmarthouse.query1("SELECT Pinnbr FROM Sensor WHERE Sensor_name  LIKE '%TEMPERATURE%'")
##    for i in range(len(temp_sensor_pins)):
##        sensor_pin_list.append(temp_sensor_pins[i])
##        sensor_types_list.append(TEMPERATURE)
##
##    light_sensor_pins = QuerySmarthouse.query1("SELECT Pinnbr FROM Sensor WHERE Sensor_name LIKE '%LIGHT%'")
##    for i in range(len(light_sensor_pins)):
##        sensor_pin_list.append(light_sensor_pins[i])
##        sensor_types_list.append(LIGHT)
##
##    return sensor_pin_list,sensor_types_list


###------------------- test code ------------------------###  

def analog_pincontrol_test():
    print 'analog_pincotrol_test'
    for i in range(0,5):
        analog_pin_control(1,[5],50*i)

def pincontrol_test():
    print 'pincotrol_test'
    for i in range(0,5):
        pin_control(1,[5],i%2)
        
def pinstates_test():
    print 'pinstates_test'
    print get_pin_states(1);

def sensor_test():
    print 'sensor_test'
    print 'interpreted: ',receive_data_arduino(1) #interpret data of arduino 1

    
###--------------------- running tests ----------------------###
    
###print 'initializing, please wait a sec'
##init()
##pincontrol_test()
##sensor_test()
##pin_control(1,[3,5],1)
###pinstates_test()
##print 'done'
