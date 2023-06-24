"""
TODO add docstrings to functions / attributes 
"""

# IN =
# OUT =
# SPI =
# I2C =
# HARD_PWM =
# SERIAL =
# UNKNOWN =


INPUT = 1
OUTPUT = 0

HIGH = 1
LOW = 0

# common.h
MODE_UNKNOWN = -1
BOARD = 10
BCM = 11
SERIAL = 40
SPI = 41
I2C = 42
PWM = 43

# event_gpio.h
NO_EDGE = 0
RISING_EDGE = 1
FALLING_EDGE = 2
BOTH_EDGE = 3

# int add_edge_detect(unsigned int gpio, unsigned int edge, int bouncetime);
# void remove_edge_detect(unsigned int gpio);
# int add_edge_callback(unsigned int gpio, void (*func)(unsigned int gpio));
# int event_detected(unsigned int gpio);
# int gpio_event_added(unsigned int gpio);
# int event_initialise(void);
# void event_cleanup(int gpio);
# void event_cleanup_all(void);
# int blocking_wait_for_edge(unsigned int gpio, unsigned int edge, int bouncetime, int timeout);


def setmode(mode):
    """Set the mode of this library to select the pin numbering.

    :param mode: New Mode
    :type mode: [BCM,BOARD]
    """
    pass


def gpio_function(channel):
    """Check what a pin is currently set to (input/output/i2c/serial etc)

    :param channel: Channel number
    :type channel: int
    """
    pass


def getmode(mode):
    pass


def setup(channel, mode):
    """Setup a pin to be used as either input or output

    :param channel: Channel number
    :type channel: int
    :param mode: The mode to be selected
    :type mode: [INPUT,OUTPUT]
    """
    pass


def setwarnings(enable):
    pass


def input(channel):
    """Read the current value of a pin works both for input and output pins

    :param channel: Channel number
    :type channel: int
    """
    pass


def output(channel, state):
    """Set the output of a pin

    :param channel: Channel number
    :type channel: int
    :param state: Output signal
    :type state: [HIGH,LOW]
    """
    pass


def cleanup(channel=None):
    """Stop controlling any pins, and free them up for future/parallel processes.  Can be provided one or many channels.  If no channel is provided defaults to all.

    :param channel: Channel number
    :type channel: [int,int list], optional
    """
    pass


class PWM:
    """Object to manage PWM on a specific pin."""

    def __init__(self, channel, frequency):
        """Constructor.  Creates a PWM object.

        :param channel: channel to output on
        :type channel: int
        :param frequency: PWM frequency
        :type frequency: float
        """
        pass

    def start(self, duty):
        """Start PWM with a set duty cycle

        :param duty: duty cycle (0-100)
        :type duty: int
        """
        pass

    def ChangeFrequency(self, freq):
        """Change the frequency of PWM

        :param freq: New frequency
        :type freq: float
        """
        pass

    def ChangeDutyCycle(self, duty):
        """CHange the duty cycle of PWM

        :param duty: New duty cycle
        :type duty: int
        """
        pass

    def stop(self):
        """Stop performing PWM on this pin"""
        pass


def set_rising_event(channel, enable):
    pass


def set_falling_event(channel, enable):
    pass


def set_high_event(channel, enable):
    pass


def set_low_event(channel, enable):
    pass
