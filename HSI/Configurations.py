import logging
import os

home = os.path.expanduser('~pi')

CONFIGURATIONS = {
    "IMAGES_DIRECTORY": "{}/Images/",  # IMPORTANT : Image folder will always be in home directory with name 'Images'
    "SHOW_DEFAULT_IMAGE": True,
    "DEFAULT_IMAGE_ON_STARTUP": "__0__.jpg",
    "DEFAULT_IMAGE_DEFAULT_LOCATION": "{}/HSI/resources/defaults/",
    "DEFAULT_IMAGE_OTHER_LOCATION": "{}/Images/",
    "RASPI_IP_ADDRESS": "199.168.1.212",
    "LOOP_BACK_IP_ADDRESS": "127.0.0.1",
    "TCP_PORT": 65432,
    "TCP_ENCODING": "utf-8",
    "DEFAULT_RECEIVING_PORT" : 28200,
    "NUMBER_OF_ALLOWED_FAILED_TCP_CONNECTIONS": 1000,
    "MAX_BYTES_OVER_TCP": 1024,
    "CHECK_NEW_IP_FROM_PI_FREQUENCY": 0.333,
    "RASPI_TXT_FILE_FULL_PATH_NAME" : "{}/HSI/ip.txt",
    "SENDING_IP_ADDRESS_TO_PI_COMMAND" : "sudo -u pi scp -rp {} pi@{}:/home/pi/MEng/meng-hsi-group/tcp",
    "SPEED_CONTROLLER_COMMAND" : "{}/HSI/resources/SmcCmd/./SmcCmd",
    "LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID" : "52FF-7506-8365-5650-5940-2167",
    "RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID" : "52FF-7206-8365-5650-1020-2567",
    "TIMEOFFLIGHT_COUNT_PERIOD" : 0.5, # Keep reading time-of-flight measurements and only send periodically on reading count. 
    "ENABLE_FILE_LOGGING" : False,
    "LOG_FILENAME" : "{}/hsi.log", # Always in home directory
    "LOGGING_LEVEL" : logging.DEBUG, # For detailed logs, change this to 'logging.DEBUG'
    "NUMBER_OF_AIRCHANNEL_PAIRS" : 3, # Number of air-channel pairs or systems. 
    "TOF_PINS" : [13,26,27], # BCM, [left, middle, right]
    "REALSENSE_PORT" : 1024,
    "TOF_PORT" : 1025,
    "EXT_CAM_PORT" : 1028,
    "DEFAULT_EXCAM_PORT" : 1026,
    "DEFAULT_INCAM_PORT" : 1027,
    "USB_CAM_ID" : "/dev/v4l/by-id/usb-HD_Camera_Manufacturer_VGA_USB_Camera_VGA_USB_Camera-video-index0",
    "RTSP_COMMAND" : "resources/v4l2rtspserver/v4l2rtspserver",
    "DISPLAY_IMAGE": None,
    "DIR1_1_PIN": 10,
    "DIR2_1_PIN": 18,
    "ENC1_1_PIN": 9,
    "ENC2_1_PIN": 11,
    "MPWM_1_PIN": 17,
    "DIR1_2_PIN": 24,
    "DIR2_2_PIN": 15,
    "ENC1_2_PIN": 25,
    "ENC2_2_PIN": 5,
    "MPWM_2_PIN": 14,
    "DIR1_3_PIN": 0,
    "DIR2_3_PIN": 22,
    "ENC1_3_PIN": 1,
    "ENC2_3_PIN": 12,
    "MPWM_3_PIN": 23,
    "FAN_PIN": 21
}
