import logging
import sys
from multiprocessing import Lock
from pathlib import Path

import pyttsx3
import threading
from CommandInterface import CommandInterface

"""
Implementation of TextToSpeechCommand that will produce sound from text in json object.

CEI-LAB, Cornell University 2019
"""


class TextToSpeechCommand(CommandInterface):
    _lock = Lock()

    def _speak(self, responseStatusCallback, jsonObject):
        """
        This method will be called to produce sound.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing text.

        Outputs:
            None
        """
        try:
            self._lock.acquire()
            jsonObject["response"] = "UNKNOWN_ERROR"
            engine = pyttsx3.init()  # This has to be here and not in a constructor
            engine.setProperty('rate', 145)
            if engine is not None:
                if "text" in jsonObject:
                    engine.say(str(jsonObject["text"]))
                    engine.runAndWait()
                    jsonObject["response"] = "SUCCESS"
                else:
                    jsonObject["response"] = "NO_TEXT_IN_JSON"
                    logging.error('TextToSpeechCommand : No text field in jsonObject')
            else:
                jsonObject["response"] = "OS_SYSTEM_ERROR"
                logging.error('TextToSpeechCommand : Speech engine not initialized')

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        # except:
        #     logging.error('TextToSpeechCommand : Error probably in responseStatus call or resource is busy')
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self._speak, args=(responseStatusCallback, jsonObject,))
        t1.start()


if __name__ == "__main__":
    obj = TextToSpeechCommand()
    obj.execute(None, {'text': 'Exterminate!'})
