## Protocol Document
###### Drafted on : 28th April 2019
###### Author : Labhansh Atriwal
###### Version : 1.0
##
##
##
##
#### List of Commands
###### 1. **FetchExternalCameraCaptureCommand** : To get live image from external camera mounted on the rover.
###### 2. **GetImagesNamesCommand** : To get all the images present in the "$HOME/Images" folder on the aero board. This folder is the official location for all the images.
###### 3. **ProcessProjectImageCommand** : To show or process or do both for an image that already exists in the folder $HOME/Images on aero board.
###### 4. **SetSpeedCommand** : To set speed of left and right wheels of the rover.
###### 5. **TextToSpeechCommand** : To produce a voice/sound from text.
###### 6. **FetchInternalCameraCaptureCommand** : To get continous live images from internal camera mounted inside the rover.
###### 7. **TimeofFlightCommand** : To get the time-of-flight sensor measurements.
###### 8. **ReadIMUCommand** : To get the IMU (BMI-160) sensor measurements and whether the rover is flipped.
###### 9. **BladderCommand** : To inflate and deflate air bladder via Arduino. 
##

###### **Case sensitve protocol**
##
##
##
##

### Detailed description of every command request and its response
##
#### 1. FetchExternalCameraCaptureCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "FetchExternalCameraCaptureCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"destination_username" : "", **Username of the destination system/computer where the image is sent**<br />
	"destination_ip" : "132.236.59.220",  **Destination IP Address. Default value is of PI(132.236.59.220).**<br />
	"destination_folder" : "",  **Folder name in destination system/computer where the image will be copied**<br />
	"destination_filename" : "", **Name to be given to the copied file name at the destination**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "FetchExternalCameraCaptureCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"CAMERA_ERROR" : **Camera not available on rover or some internal error with camera.**<br />
"INCOMPLETE_DESTINATION_INFO_IN_JSON" : **All JSON fields not provided for destination.**<br />
"DESTINATION_INFO_NOT_VALID" : **All JSON fields are provided for destination, but either the data is wrong or there are access/firewall/ssh-key issues.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
##
##
##
#### 2. GetImagesNamesCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "GetImagesNamesCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "GetImagesNamesCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"imageNames" : ["",""], **List of image names in "$HOME/Images" folder on the rover, type array of strings**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, probably the $HOME/Images folder is missing. Check logs for more info.**<br />
##
##
##
#### 3. ProcessProjectImageCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "ProcessProjectImageCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"imageFileName" : "", **Image file existing on the rover "$HOME/Images" folder, to be projected or processed**<br />
	"processImage" : true/false, **Flag to process image or not** <br />
	"projectImage" : true/false, **Flag to project image or not**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "ProcessProjectImageCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"IMAGE_PROCESSING_FAILED" : **Error in image processing library.**<br />
"FILE_NOT_EXIST" : **file you are trying to process doesn't exist.**<br />
"NO_FILE_SPECIFIED" : **"imageFileName" not specified in JSON.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
##
##
##
#### 4. SetSpeedCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "SetSpeedCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"leftSpeed" : ##, **Left speed value, type int**<br />
	"rightSpeed" : ##, **Right speed value, type int**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "SetSpeedCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, probably error with speed controllers. Check logs for more info.**<br />
"SPEED_VALUES_NOT_PROVIDED" : **Json Object doesn't have motor speed values.**<br />
##
##
##
#### 5. TextToSpeechCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "TextToSpeechCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"text" : "", **Text to be spoken, in string of lenght not more than 50 characters**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "TextToSpeechCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"text" : "", **Text to be spoken, in string of lenght not more than 50 characters**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"NO_TEXT_IN_JSON" : **No text field in JSON.**<br />
"OS_SYSTEM_ERROR" : **Issues with OS Speech engine "pyttsx3".**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
##
##
##
#### 6. FetchExternalCameraCaptureCommand

##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "FetchInternalCameraCaptureCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"startSendingImages" : True/False, **Flag to start or stop continous transmission of images to the destination**<br />
	"destination_username" : "", **Username of the destination system/computer where the image is sent**<br />
	"destination_ip" : "132.236.59.220",  **Destination IP Address. Default value is of PI(132.236.59.220).**<br />
	"destination_folder" : "",  **Folder name in destination system/computer where the image will be copied**<br />
	"destination_filename" : "", **Name to be given to the copied file name at the destination**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "FetchInternalCameraCaptureCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"CAMERA_ERROR" : **Camera not available on rover or some internal error with camera.**<br />
"INCOMPLETE_DESTINATION_INFO_IN_JSON" : **All JSON fields not provided for destination.**<br />
"DESTINATION_INFO_NOT_VALID" : **All JSON fields are provided for destination, but either the data is wrong or there are access/firewall/ssh-key issues.**<br />
"INTERNAL_CAMERA_TRANSMISSION_ALREADY_ON" : **If transmission is already turned on**<br />
"INTERNAL_CAMERA_TRANSMISSION_ALREADY_OFF" : **If transmission is already turned off**<br />
"INTERNAL_CAMERA_TRANSMISSION_TURNED_ON" : **If transmission is turned on**<br />
"INTERNAL_CAMERA_TRANSMISSION_TURNED_OFF" : **If transmission is turned off**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
##
##
##
#### 7. TimeofFlightCommand
##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "TimeofFlightCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"startSendingToF" : true/false, **Flag to receive the time-of-flight measurements or not**<br />
	"countPeriod": ##, **(optional) default to be 5, for faster sending frequency recommand value 3, higher frequency with smaller value**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "TimeofFlightCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"startSendingToF" : true/false, **Flag to receive the time-of-flight measurements or not**<br />
	"countPeriod": ##, **(optional) default to be 5, for faster sending frequency recommand value 3, higher frequency with smaller value**<br />
	"receivingPort": ##, <br />
	"clientIPAddress": ##, **client IP address**<br />
	"values" : [ # ], **a list of time-of-flight values**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"TIMEOFFLIGHT_TRANSMISSION_ALREADY_ON" : **If transmission is already turned on**<br />
"TIMEOFFLIGHT_TRANSMISSION_ALREADY_OFF" : **If transmission is already turned off**<br />
"TIMEOFFLIGHT_TRANSMISSION_TURNED_ON" : **If transmission is turned on**<br />
"TIMEOFFLIGHT_TRANSMISSION_TURNED_OFF" : **If transmission is turned off**<br />
"READING_NOISE_ERROR" : **There is data corrupted in the serial port.** <br />
"READING_SPLIT_ERROR" : **There is potential noise in the serial port.** <br />
##
##
##
#### 8. ReadIMUCommand
##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "ReadIMUCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "ReadIMUCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"angular velocity" :  [ # ], **a list of angular velocity values**<br />
	"accelerometer" :  [ # ], **a list of acceleration values**<br />
	"roverFlipped" : true/false, **Status of the rover orientation.**<br />
	"clientIPAddress": ##, **client IP address**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"SUCCESS" : **Operation executed successfully.**<br />
"DATA_ERROR" : **IMU the reading data return error.**<br />
"READING_ERROR" : **IMU reading error.**<br />
"IMU_CONFIG_ERROR" : **IMU configure error.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
##
##
##
#### 9. BladderCommand
##### Request packet from SENDER to ROVER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "BladderCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"select" : [ # ], **List of selection on air channels(3 pairs as default)**<br />
	"action" : Inflate/Deflate, **Action of baldder(case sensitive : smaller case)**<br />
	"receivingPort": ## <br />
}<br />

##### Response packet from ROVER to SENDER:

{<br />
	"id" : ##,  **Timestamp in milliseconds (int), always unique**<br />
	"cmd" : "BladderCommand", **Command name**<br />
	"priority" : ##, **Priority, type int**<br />
	"receivingPort": ##, <br />
	"select" : [ # ], **List of selection on air channels(3 pairs as default)**<br />
	"action" : inflate/deflate, **Action of baldder(case sensitive : smaller case)**<br />
	"response" : "" **Response given back to the command operator/sender**<br />
}<br />

##### Different responses:

"INFLATE_SUCCESS" : **Inflate success.**<br />
"DEFLATE_SUCCESS" : **Deflate success.**<br />
"INCORRECT_INFLATE_DEFLATE_FIELD" : **There is a typo in the action field.**<br />
"SERIAL_CONNECTION_CLOSED" : **Can't open serial.**<br />
"ACTION_OR_SELECT_FIELD_NOT_IN_JSON" : **Misses either the action or select field.**<br />
"PROCESS_BLADDER_COMMAND" : **Processing bladder command.**<br />
"ERROR_INCORRECT_SELECTION_NUMBER" : **The number of select is incorrect.**<br />
"UNKNOWN_ERROR" : **Any other unknown error, check logs for more info.**<br />
