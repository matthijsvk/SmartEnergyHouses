//code for the 'piper' arduino connected to the CCU

// the functions available are:
//- listen for Serial commands from the CCU
//- send them to the correct SEH

#include <VirtualWire.h>

const int transmit_pin = 12; //geel
const int receive_pin = 11;

const int MESSAGE_LENGTH=15;
uint8_t CCU_got[MESSAGE_LENGTH];
uint8_t SEH_got[MESSAGE_LENGTH];

const int DATAREQUEST=100; //commands
const int EMPTY = 12;

const int CCU_IP= 253;

void setup() {
  Serial.begin(9600);
  // Communication:  Initialise the IO and ISR
  vw_set_tx_pin(transmit_pin);
  vw_set_rx_pin(receive_pin);
  vw_set_ptt_inverted(true); // Required for DR3100
  vw_setup(2000);	 // Bits per sec
  
  int i;
  for (i = 0; i < MESSAGE_LENGTH; i++){
    SEH_got[i] = EMPTY;
    CCU_got[i] = EMPTY;
  }
}


void loop(){
  pipe_CCU_to_SEH(CCU_got);
  delay(2);  // delays van milliseconden!
  if (CCU_got[2]== DATAREQUEST){
    pipe_SEH_to_CCU(SEH_got); //uncomment if you want to send and listen afterward
  }
  int i;
  for (i = 0; i < 20; i++){
    SEH_got[i] = EMPTY;
    CCU_got[i] = EMPTY;
  }
}  

uint8_t pipe_CCU_to_SEH(uint8_t* CCU_got) {
  boolean received=false;
  while(received == false){ ///wait until serial command arrives
    if (Serial.available()){
      receive_serial_data(CCU_got);
      send_to_SEH(CCU_got);
      received= true;
    }
  }
}

uint8_t receive_serial_data(uint8_t* CCU_got){   // for the communication between arduino's replace this by the VirtualWire code
  int index=0;
  while (Serial.available() && index< MESSAGE_LENGTH) { 
      uint8_t inChar = Serial.parseInt();
      CCU_got[index] = inChar;
      index++;
  } 
}

uint8_t send_to_SEH(uint8_t* CCU_got){
      vw_send((uint8_t *)CCU_got, MESSAGE_LENGTH);
      vw_wait_tx(); // Wait until the whole message is gone
      delay(2);
}

uint8_t pipe_SEH_to_CCU(uint8_t* SEH_got) {  
      vw_rx_start();       // Start the receiver 
      receive_wireless_data(SEH_got);   
      vw_rx_stop();
      send_to_CCU(SEH_got);
    }

uint8_t receive_wireless_data(uint8_t* SEH_got) {
  uint8_t buf[VW_MAX_MESSAGE_LEN];
  uint8_t buflen = VW_MAX_MESSAGE_LEN;
  boolean received= false;
  while (received!=true) {// while the message hasn't been received, keep looking for message
      if (vw_get_message(buf, &buflen)){  // Non-blocking 
        received= true;
        if (buf[1]!=CCU_IP){
            break;
        }    
        int i;
        for (i = 0; i < MESSAGE_LENGTH; i++){ //message contains all the other info used by the command specified in header[2]
          SEH_got[i]= buf[i];
        }
      }
  }
  received= false;
}
  
uint8_t send_to_CCU(uint8_t* SEH_got){
  int i;
  for (i=0; i<MESSAGE_LENGTH;i++){
    Serial.print(SEH_got[i]);
    Serial.print(' ');
  }
  Serial.println();
  //als alternatief voor de for-lus(en dus ook de parser in communicatie.py)
  //Serial.println(SEH_got);
}
