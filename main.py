import machine
import time
import math

# Initialize pins for seven-segment display segments (A-G)
seven_segment_pins = [machine.Pin(pin, machine.Pin.OUT) for pin in range(7)]

# Initialize pins for controlling which digit (1-4) is active
seven_segment_display_digit = [machine.Pin(pin, machine.Pin.OUT) for pin in range(8, 12)]

# Initialize pin for the decimal point
seven_segment_dp = machine.Pin(7, machine.Pin.OUT)

# Initialize the timer for scanning the display
scanning_timer = machine.Timer(-1)

# Initialize the analog input pin for reading sensor data
input_analoge = machine.ADC(machine.Pin(26))

# Initialize the button pin with a pull-down resistor
btn = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Timer for handling debouncing
timer = machine.Timer()

# Global variable to hold the value to be displayed
display_value = 0

# Hex codes for displaying digits 0-9 on the seven-segment display
seven_segment_hex = [
    0x40,  # 0
    0x79,  # 1
    0x24,  # 2
    0x30,  # 3
    0x19,  # 4
    0x12,  # 5
    0x02,  # 6
    0x78,  # 7
    0x00,  # 8
    0x10,  # 9
]

# Function to display a digit on the specified position of the seven-segment display
def print_digit(digit, digit_idx, dp_enable):
    # Turn off all digits
    for i in range(4):
        seven_segment_display_digit[i].value(0)
    # Set the segments for the digit
    for i in range(7):
        seven_segment_pins[i].value((seven_segment_hex[digit] >> i) & 1)
    
    # Control the decimal point
    seven_segment_dp.value(not dp_enable)
    # Turn on the specific digit
    seven_segment_display_digit[3 - digit_idx].value(1)

# Function to format the floating-point number to three decimal places
def format_float(number):
    return "{:.3f}".format(number)

# Function to scan and update the seven-segment display
def seven_seg_scan(timer_init):
    global display_value
    value_str = format_float(display_value)  # Format the value
    digit_idx = 0  # Index to keep track of which digit to display
    
    for i, char in enumerate(value_str):
        if char == '.':
            continue
        digit = int(char)  # Convert character to integer digit
        # Check if the next character is a decimal point
        dot = (i < len(value_str) - 1 and value_str[i + 1] == '.')
        print_digit(digit, digit_idx, dot)  # Display the digit with or without the decimal point
        digit_idx += 1
        if digit_idx == 4:  # Only display up to 4 digits
            break
        time.sleep(0.003)  # Short delay to avoid flickering

# Function to disable the scanning timer
def disable_timer():
    global scanning_timer
    scanning_timer.deinit()

# Function to enable the scanning timer
def enable_timer():
    global scanning_timer
    scanning_timer.init(period=30, mode=machine.Timer.PERIODIC, callback=seven_seg_scan)

# Function to read the analog input and update the display value
def read_analoge():
    global display_value
    analoge_read = input_analoge.read_u16()  # Read the analog value
    display_value = (analoge_read * 3.3) / ((2 ** 16) - 1)  # Convert to voltage
    voltage_in_mv = round(display_value * 1000)
    print("Voltage: "+ str(voltage_in_mv) + " mv")  # Print the voltage in millivolts

# Function to handle the debouncing logic
def handle_debounce(timer):
    read_analoge()  # Read the analog value
    seven_seg_scan(timer)  # Update the display
    btn.irq(trigger=machine.Pin.IRQ_RISING, handler=debounce)  # Re-enable button interrupts

# Debounce function to ignore additional button presses
def debounce(pin):
    btn.irq(handler=None)  # Disable button interrupts
    timer.init(mode=machine.Timer.ONE_SHOT, period=200, callback=handle_debounce)  # Start debounce timer

# Setup function to initialize the system
def setup():
    enable_timer()  # Enable the display scanning timer
    btn.irq(trigger=machine.Pin.IRQ_RISING, handler=debounce)  # Set up the button interrupt

# Main entry point of the program
if __name__ == "__main__":
    setup()