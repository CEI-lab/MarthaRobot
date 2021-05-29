"""
Interface to declare the format to be used by all the commands.

CEI-LAB, Cornell University 2019
"""


class CommandInterface(object):

    def execute(self, responseStatusCallback, jsonObject):
        """
        This method will be called to execute the functionality implemented in a command.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing relevant data for a command.

        Outputs:
            None
        """
        raise NotImplementedError("CommandInterface.execute() not implemented")
