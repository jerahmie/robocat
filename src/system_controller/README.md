# System Controller

All code for The Robo Cat's Arduino Uno-based System Controller. The Robo Cat utilizes an Arduino Uno 8-Bit AVR board for the main system controller.

## Build Steps
To build the system controller sketch, I used the `arduino-cli` tool. 

### Install arduino-cli
Follow [these instructions](https://arduino.github.io/arduino-cli/0.21/installation/) to install the arduino-cli tool

### Install the Arduino AVR core 
`$ arduino-cli core install arduino:avr`

### Build and Upload the system_controller sketch
`$ arduino-cli compile -b arduino:avr:uno system_controller`

### Upload the Sketch

`arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno system_controller`

where port is given by 

`$ arduino-cli board list`
