import cv2
import picamera
import picamera.array

def cam():
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)
            while True:
                camera.capture(stream, 'bgr', use_video_port = True)
                cv2.imshow('frame', stream.array)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                stream.seek(0)
                stream.truncate()
            cv2.destroyAllWindows()
            
cam()