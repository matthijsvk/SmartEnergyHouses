//besturingsprogramma SEH
#include <VirtualWire.h>
#include <wprogram.h>
#include <wiring_private.h>
#include <pins_arduino.h>

// send/transmit 
const int transmit_pin = 13;
const int receive_pin = 12;

const int MESSAGE_LENGTH=15;
uint8_t CCU_got[MESSAGE_LENGTH];

uint8_t sensor_list[MESSAGE_LENGTH];
uint8_t sensor_data[MESSAGE_LENGTH];
uint8_t app_states[MESSAGE_LENGTH];
const int CCU_IP = 253;
const int ME_IP=1;

const int DATAREQUEST=100; //commands
const int PINCONTROLCOMMAND=101;
const int ANALOGPINCONTROLCOMMAND=102;

const int SENSOR_DATA_CHECK= DATAREQUEST + 10; //checks
const int PIN_CONTROL_CHECK = PINCONTROLCOMMAND + 10;
const int ANALOG_PIN_CONTROL_CHECK= ANALOGPINCONTROLCOMMAND + 10;

const int H=255;
const int L = 254;

const int EMPTY = 12;

//Appliances
const int tvPin=2;               //pin thaft lights the TV led and turns on the TV buzzer.
const int speakerPin=10;

//---------------------------------------- MAIN PROGS ------------------------------

void setup(){
  Serial.begin(9600);
  for (int pin=2; pin < 11 ;pin++){
    pinMode(pin,OUTPUT);
  }
  
  vw_set_tx_pin(transmit_pin);
  vw_set_rx_pin(receive_pin);
  vw_setup(2000);	 // Bits per sec

  int i;
  for (i = 0; i < 20; i++){
    CCU_got[i] = EMPTY;
    sensor_data[i] = EMPTY;
    sensor_list[i]= EMPTY;
    app_states[i]= EMPTY;
  }
}

void loop(){  
  //listen for incoming data from CCU
  get_data_CCU(CCU_got);
  int i;
  for (i=0; i<MESSAGE_LENGTH;i++){
    Serial.print(CCU_got[i]);
    Serial.print(' ');
  }
  Serial.println();

  switch (CCU_got[2]){ //look which function is called

    case (DATAREQUEST) :
    { // if a request for sensor data is received, gather and send the data
      int i;
      for (i=0;i<MESSAGE_LENGTH-3; i++){ //removing the header from CCU_got
        CCU_got[i]= CCU_got[i+3];
      }
      //get data
      getData(CCU_got,sensor_data); //CCU_got contains the sensor numbers

      //send data
      send_data_CCU(sensor_data);//send the package
      break;
    }

    case (ANALOGPINCONTROLCOMMAND): 
    {
      int i;
      for (i=0;i<MESSAGE_LENGTH-3; i++){ //removing the header from CCU_got
        CCU_got[i]= CCU_got[i+3];
      }
      controlPinsAnalog(CCU_got);
      //      
      //      // sending feedback
      //      send_data_CCU(CCU_got);
      break;
    }  

    case (PINCONTROLCOMMAND): 
    {
      int i;
      for (i=0;i<MESSAGE_LENGTH-3; i++){ //removing the header from CCU_got
        CCU_got[i]= CCU_got[i+3];
      }
      controlPinsDigital(CCU_got);

      //      // sending feedback
      //      send_data_CCU(CCU_got);
      break;
    }
    case (EMPTY):
    {
      //      Serial.println("empty msg");
    }
  default: 
    2;//Serial.println("error in data received");

  }//close switch c[2]
  // alle lijsten terug leeg:
  i=0;
  for (i = 0; i< MESSAGE_LENGTH; i++){
    CCU_got[i] = EMPTY;
    sensor_data[i] = EMPTY;
    sensor_list[i]= EMPTY;
    app_states[i]= EMPTY;
  }
}

//---------------------------------------- OTHER PROGS ------------------------------

//FUNCTIONS

//INPUT functions

void controlPinsDigital(uint8_t* CCU_got){
  int onOff= 0;
  int onOffpos=1;                //default pos for the 'H' of 'L'; normally on 3rd pos (when only one led)
  int i=1;
  while(CCU_got[i] != H && CCU_got[i] != L  && onOffpos < MESSAGE_LENGTH-3 ){ //for each additional int (ledPin): look one pos further
    onOffpos++;
    i++;
  }

  if(CCU_got[onOffpos]==H){
    onOff= 1;
  }
  else {
    onOff=0;
  }

  i=0;
  for (i=0; i<onOffpos; i++){ //turn on/off all the leds
     pinMode(CCU_got[i], OUTPUT);
     digitalWrite(CCU_got[i],onOff); //write onOff to the right pins
    }
  }
}

void controlPinsAnalog(uint8_t* CCU_got){

  int value= 0;
  int onOffpos=1;
  int i=1;
  while(CCU_got[i] != EMPTY  && onOffpos < MESSAGE_LENGTH-3 ){ //for each additional int (ledPin): look one pos further
    if (CCU_got[i] >20 && CCU_got[i]!= EMPTY){
      break;
    }
    onOffpos++;
    i++;
  }
  if(CCU_got[onOffpos] >20){
    value= CCU_got[onOffpos];
  }

  i=0;
  for (i=0; i<onOffpos; i++){ //turn on/off all the leds
    pinMode(CCU_got[i], OUTPUT);
    analogWrite(CCU_got[i],value); //write onOff to the right pins
  }
}


//DATA functions  

uint8_t get_data_CCU(uint8_t* CCU_received) {  
  vw_rx_start();       // Start the receiver 
  receive_wireless_data(CCU_received);   
  int i;
  for (i=0; i<MESSAGE_LENGTH;i++){
    Serial.print(CCU_received[i]);
    Serial.print(' ');
  }
  Serial.println();
  //      vw_rx_stop();
}


uint8_t receive_wireless_data(uint8_t* CCU_received) {
  uint8_t buf[VW_MAX_MESSAGE_LEN];
  uint8_t buflen = VW_MAX_MESSAGE_LEN;

  boolean received= false;
  while (received!=true) {// while the message hasn't been received, keep looking for message
    if (vw_get_message(buf, &buflen)) // Non-blocking 
    {
      received= true;
      if (buf[0] != CCU_IP || buf[1] != ME_IP){
        break;
      }
      int i;
      for (i = 0; i < MESSAGE_LENGTH; i++){ //message contains all the other info used by the command specified in header[2]
        CCU_received[i]= buf[i];
      }
    }
  }
  received= false;
}

uint8_t send_data_CCU(uint8_t* sensor_data){
  int i;
  for (i=0; i<MESSAGE_LENGTH;i++){
    Serial.print(sensor_data[i]);
    Serial.print(' ');
  }
  Serial.println();
  vw_send((uint8_t *)sensor_data, MESSAGE_LENGTH);
  vw_wait_tx(); // Wait until the whole message is gone
  delay(2);
}


// get sensor_data

uint8_t getData(uint8_t* sensor_list,uint8_t* sensor_data){
  sensor_data[0]= ME_IP;//initialize the header
  sensor_data[1]= CCU_IP;
  sensor_data[2]= SENSOR_DATA_CHECK;

  int i;
  int analogVal;
  while (i< MESSAGE_LENGTH && sensor_list[i]!= 0){
    //Serial.println(i);
    if (sensor_list[i]<20){
      if (sensor_list[i]<14){
        sensor_data[i+3]= digitalRead(sensor_list[i]);
      }

      else { //the other pins (temp, light,...)
        analogVal=0;
        for(int j = 0; j < 10; j++) { // takes 10 samples to make sure we get a good value
          long reading=analogRead(sensor_list[i]);
          analogVal += reading; 
          delay(10);
        }
        analogVal= analogVal/10.0;

        if (analogVal>70){//only scale the high numbers; otherwise, the temperature readings (usually 20-50) will give too low  values (= inaccurate values)
          analogVal= map(analogVal,70,1023,70,254);
        }
        if (analogVal==EMPTY){ //don't consider the value '2' as empty in communication.py (in 'convert wireless to list')
          analogVal=EMPTY+1;
        }
        analogVal= constrain(analogVal,0,255);
        sensor_data[i+3]= analogVal;
      }
    }
    i++;
  }
}


//Voor de tv:

//(*0.0000001)
const int C   = 1911;
const int C1  =  1804;
const int D   = 1703;
const int Eb =   1607;
const int E  =  1517;
const int F  =  1432;
const int F1  =  1352;
const int G  =  1276;
const int Ab   = 1204;
const int A   = 1136;
const int Bb  =  1073;
const int B  =  1012;
const int c  =     955;
const int c1 =     902;
const int d  =     851;
const int eb =     803;
const int e  =     758;
const int f  =     716;
const int f1=      676;
const int g  =     638;
const int ab =     602;
const int a  =     568;
const int bb =     536;
const int b =      506;

const int p =      0  ;//pausa

//int speaker = 9;    //staat al vanboven bij de pins
long vel = 7000;
int melod[] = {
  e, e,  e,  c, e,   g,  G,  c,  G,  E,  A,  B, Bb, A, G, e, g,  a, f, g,  e,  c, d, B, c};
int ritmo[] = {
  6, 12, 12, 6, 12, 24, 24, 18, 18, 18, 12, 12, 6, 12, 8, 8, 8, 12, 6, 12, 12, 6, 6, 6, 12};

void turnTvOn() {
  digitalWrite(tvPin, 1);
  for (int i=0; i<25; i++) {
    int tom = melod[i];
    int tempo = ritmo[i];

    long tvalue = tempo * vel;

    tocar(tom, tvalue);

    delayMicroseconds(1000); //pausa entre notas!
  }
  delay(20);
  digitalWrite(speakerPin, LOW);
}

void turnTvOff() {
  digitalWrite(tvPin, 0);
  digitalWrite(speakerPin, LOW);
}

void tocar(int tom, long tempo_value) {
  long tempo_gasto = 0;
  while (tempo_gasto < tempo_value) {
    digitalWrite(speakerPin, HIGH);
    delayMicroseconds(tom / 2);

    digitalWrite(speakerPin, LOW);
    delayMicroseconds(tom/2);

    tempo_gasto += tom;
  }
}
