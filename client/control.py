import time, socket, json, pickle, ComparableDict, cv2
import numpy as np

def sendObject(message):
    # local host IP '127.0.0.1'
    host = '192.168.0.104'

    # Define the port on which you want to connect
    port = 65432

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # connect to server on local computer
    s.connect((host,port))

    s.send(json.dumps(message).encode() )
    s.close()

def receiveResponse(port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(("",port))
    s.listen(1)
    connection, address = s.accept()
    data = []
    while True:
        packet = connection.recv(4096)
        if not packet: break
        data.append(packet)
    s.close()
    data_arr = pickle.loads(b"".join(data))
    print(data_arr["data"])
    cv2.imshow("image",data_arr["data"]/np.amax(data_arr["data"]))
    # cv2.waitKey(0)

camera = {
"id" : int(time.time()),
"cmd" : "TimeofFlightCommand", #Command name
"type" : 'stream',
"height": 480,
"width": 640,
"count_period" : 10,
"colorize": 1,
"priority" : 1,#, Priority, type int
"receivingPort" : 12346
}

tts = {
"id" : int(time.time()),
"cmd" : "TextToSpeechCommand", #Command name
"text" : 'Top of the morning, Sir!',
"priority" : 1,#, Priority, type int
}


sendObject(camera)
# receiveResponse(12346)

_send_setspeed_object = {
"id" : int(time.time()),
"cmd" : "SetSpeedCommand", #Command name
"priority" : 1,#, Priority, type int
"leftSpeed" : 2400, ## Left speed value, type int
"rightSpeed" : 3200, ## Right speed value, type int
"receivingPort" : 12346
}

_send_setspeed_object_stop = {
"id" : int(time.time()),
"cmd" : "SetSpeedCommand", #Command name
"priority" : 1,#, Priority, type int
"leftSpeed" : 00, ## Left speed value, type int
"rightSpeed" : 00, ## Right speed value, type int
"receivingPort" : 12346
}
