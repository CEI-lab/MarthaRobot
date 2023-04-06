"""
Interface to declare the format to be used by all the command registries.

CEI-LAB, Cornell University 2019
"""


class CommandRegistryInterface(object):

    def __init__(self):
        pass

    def setObject(self, keyCmdString, valueCommandObj):
        """
        This method will be called to add the command name with the respective Command class.

        Inputs:
            keyCmdString : Command name as used in JSON protocol, for the respective command
                passed as value.
            valueCommandObj : Object of a command class that inherits CommandInterface corresponding
                the provided key.

        Outputs:
            None

        """
        raise NotImplementedError("CommandRegistryInterface.setObject() not implemented")

    def getObject(self, keyCmdString):
        """
        This method will be called to add the command name with the respective Command class.

        Inputs:
            keyCmdString : Command name as used in JSON protocol, for the respective command
                passed as value.

        Outputs:
            Object of a command class that inherits CommandInterface corresponding
                the provided key. If there is no entry along the key, then return None.

        """
        raise NotImplementedError("CommandRegistryInterface.getObject() not implemented")
