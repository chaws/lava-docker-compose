#include <Arduino.h>
#include <HardwareSerial.h>

#define BAUD_RATE 115200

// Let's deal with 8 relays only for now
#define NUM_RELAYS 8

// Magic number to wrap our target input
#define MAGIC_NUMBER 42 // sender must send the letter Z (upper case) before and after the actual input

// Controls relays states
int relays[NUM_RELAYS + 1];

// Sets a specific relay(1 to NUM_RELAYS) state(0 - LOW, 1 - HIGH)
int setRelayState(int relay, int state)
{
    if(relay < 1 || relay > NUM_RELAYS || state < 0 || state > 1)
        return - 1;

    digitalWrite(relays[relay], state ? LOW : HIGH);
    return 0;
}

// Set things up
void setup()
{
    // Init all relays with their designated arduino pin
    int i;
    for(i = 1; i <= NUM_RELAYS; i++)
    {
        // Each item is the corresponding pin in arduino
        relays[i] = i + 1;
        pinMode(relays[i], OUTPUT);
    }

    // Start serial port with 115200 baud
    Serial.begin(BAUD_RATE);

    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(2, HIGH);
}

// Main loop
void loop()
{
    int relay, state, incomingByte, input_idx = 0;

    for(; input_idx < 4;)
    {
        // Check if any data is available
        if(Serial.available() > 0)
        {
            // Start collecting input only when magic_number is detected
            incomingByte = Serial.read() - '0';
            if(input_idx == 0)
            {
                if(incomingByte == MAGIC_NUMBER)
                    input_idx++;
                else
                    continue;
            }

            else if(input_idx == 1)
            {
                relay = incomingByte;
                input_idx++;
            }

            else if(input_idx == 2)
            {
                state = incomingByte;
                input_idx++;
            }

            else if(input_idx == 3)
            {
                if(incomingByte == MAGIC_NUMBER)
                    input_idx++;
                else
                    continue;
            }
        }
        else
        {
            delay(500);
        }
    }

    // Input is good
    if(setRelayState(relay, state) == -1)
    {
        Serial.println("no");
        return;
    }

    // All good, send back confirmation
    Serial.println("ack");
}

// Main function
int main(void)
{
    init();
    setup();
    for(;;)
    {
        loop();
    }
}
