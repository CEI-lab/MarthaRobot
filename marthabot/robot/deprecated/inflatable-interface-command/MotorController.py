
class MotorController:

	def __init__(self, motor_speed_pin,
					   motor_direction_pin,
					   encoder_a_pin,
					   encoder_b_bin,
					   pwm_freq=1000)

		# Save pin numbers
		self.M_SPEED_PIN = motor_speed_pin
		self.M_DIR_PIN = motor_direction_pin
		self.ENCD_A_PIN = encoder_a_pin
		self.ENCD_B_PIN = encoder_b_bin

		# Set pin name convention
		GPIO.setmode(GPIO.BCM)
	
		# Setup pins
		GPIO.setup(self.ENCD_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.ENCD_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.M_SPEED_PIN, GPIO.OUT)
		GPIO.setup(self.M_DIR_PIN, GPIO.OUT)	

		# Create PWM object for motor speed
		self.motor_pwm = GPIO.PWM(self.M_SPEED_PIN, pwm_freq)

		# Set number of turn for encoders
		n_turns_a = 0
		n_turns_b = 0

	def encoder_a_callback(self, channel)

	def set_speed(self, speed, direction):
		
		assert (0 <= speed <= 255), 'Speed must be between 0 and 255'
		assert (direction == 1 or direction == 0) 'Direction must be boolean'

		# Set direction
		GPIO.output(self.M_DIR_PIN, direction)

		# Set speed
		self.motor_pwm.start(speed)

	def stop(self)
		
		self.motor_pwm.stop()

	def move_distance(self, speed, direction, n_turns_to_move)
		

		
	
		

	
