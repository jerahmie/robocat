/*!
* Main system controller (Arduino Uno R3)
*
*
*/

#include <SPI.h>

// SPI pins
//const int DATAOUT = 11 // COPI
//const int DATAIN	= 12 // CIPO
//const int SPICLOCK = 13 // SCK
const int CHIPSELECT = 10; // cs
volatile int indx;

// global data buffer
char spibuf [4];

// motor shield gpio
const int E1 = 3;  ///<Motor1 Speed (analog)
const int E2 = 11; ///<Motor2 Speed (analog)
const int E3 = 5;  ///<Motor3 Speed (analog)
const int E4 = 6;  ///<Motor4 Speed (analog)

const int M1 = 4;  ///<Motor1 Direction (Digital)
const int M2 = 12; ///<Motor1 Direction (Digital)
const int M3 = 8;  ///<Motor1 Direction (Digital)
const int M4 = 7;  ///<Motor1 Direction (Digital)

/// Helper functions

void M1_advance(char Speed) ///<Motor1 Advance
{
	digitalWrite(M1, LOW);
	analogWrite(E1, Speed);
}

void M2_advance(char Speed) ///<Motor2 Advance
{
	digitalWrite(M2, LOW);
	analogWrite(E2, Speed);
}

void M3_advance(char Speed) ///<Motor3 Advance
{
	digitalWrite(M3, LOW);
	analogWrite(E3, Speed);
}

void M4_advance(char Speed) ///<Motor4 Advance
{
	digitalWrite(M4, LOW);
	analogWrite(E4, Speed);
}

void M1_back(char Speed) ///<Motor1 Back off
{
	digitalWrite(M1, HIGH);
	analogWrite(E1, Speed);
}

void M2_back(char Speed) ///<Motor2 Back off
{
	digitalWrite(M2, HIGH);
	analogWrite(E2, Speed);
}

void M3_back(char Speed) ///<Motor3 Back off
{
	digitalWrite(M3, HIGH);
	analogWrite(E3, Speed);
}

void M4_back(char Speed) ///<Motor4 Back off
{
	digitalWrite(M4, HIGH);
	analogWrite(E4, Speed);
}

void systems_check(void) ///<Execute a power-on systems check
{
	const char check_speed = 100;  // 0 to 255
	// forward
	M1_advance(check_speed);
	M4_advance(check_speed);
	delay(2000);

	// back
	M1_back(check_speed);
	M4_back(check_speed);
	delay(2000);

	// all stop
	M1_advance(0); // stop motors
	M4_advance(0);
	delay(2000);

	// spin right
	M1_advance(check_speed);  // left wheel motor
	M4_back(check_speed);  // right wheel motor
	delay(2000);  ///<Delay 2s
	// spin left
	M1_back(check_speed);
	M4_advance(check_speed);
	delay(2000);

	// all stop
	M1_advance(0); // stop motors
	M4_advance(0);
}


// update motor values
void update_motors(void) {
	if (spibuf[0] == 0) {
		M1_advance(spibuf[1]);
	}
	else if (spibuf[0] == 1) {
	  M1_back(spibuf[1]);
  }
	else {
		M1_advance(0);  // bad command.  stop M1 motor
	}
	if (spibuf[2] == 0) {
		M4_advance(spibuf[3]);
	}
	else if (spibuf[2] == 1) {
		M4_back(spibuf[3]);
	}
	else {
		M4_advance(0);  // bad command.  Stop M4 motor.
	}
	// clear spibuf and reset index
	for (int i=0; i<4; i++){
		spibuf[i] = 0;
	}
	indx = 0;
}


// setup()
void setup() {
	   Serial.begin(9600);
		 SPCR |= _BV(SPE);  // turn on SPI in peripheral mode
		 // initialize spi buffer 
		 spibuf[0] = 0x44;
		 spibuf[1] = 0x45;
		 spibuf[2] = 0x41;
		 spibuf[3] = 0x44;
		 pinMode(CHIPSELECT, INPUT);
		 //digitalWrite(CHIPSELECT, LOW);
		// configure SPI as peripheral
	   //SPI.begin();
		
		// configure motor controller pins
     for (int i=3; i<9; i++) {
     	 pinMode(i,OUTPUT);
     }
     for (int i=11; i<13; i++) {
     	 pinMode(i,OUTPUT);
     }
     delay(5000);  // wait 5 sec
		// Power-on self test (POST)
     //systems_check();  ///< Execute systems check.
		 // SPI peripheral device setup

		 pinMode(MISO, OUTPUT); //pinMode(MISO, OUTPUT);
		 pinMode(MOSI, INPUT); //
		 SPI.attachInterrupt();
}

ISR (SPI_STC_vect) {
	//indx = 0;
	byte c = SPDR;
	SPDR = 0x00; 
	if (indx < sizeof spibuf) {
		spibuf[indx++] = c;
	}
}



void loop() {
	Serial.write(spibuf);
	update_motors();
	//Serial.write("Update motors");
	delay(500);
	//Serial.write(0x8);
	//delay(500);
	//Serial.write(0x7c);
	//delay(500);
	//Serial.write(0x8);
	//delay(500);
}
