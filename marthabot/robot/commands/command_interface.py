"""
Interface to declare the format to be used by all the commands.

CEI-LAB, Cornell University 2019
"""


class CommandInterface():

    def execute(self, responseStatusCallback, jsonObject):
        """This method will be called to execute the functionality implemented in a command.

        :param responseStatusCallback: A callback function has to be passed, that will
                send the status of command execution to the source of the command. 
                This callback will be passed by the caller of execute().
        :type responseStatusCallback: func(dict)->None
        :param jsonObject: A JSON object containing relevant data for a command.
        :type jsonObject: json object
        :raises NotImplementedError: abstract class
        """
        raise NotImplementedError("CommandInterface.execute() not implemented")
