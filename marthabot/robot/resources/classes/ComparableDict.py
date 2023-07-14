# from collections import ChainMap

"""
A singleton priority queue class. Implemented QueueInterface.
CEI-LAB, Cornell University 2019
"""

class ComparableDict(dict):
    '''
    Variant of ChainMap that allows direct updates to inner scopes
    '''

    def __eq__(self, other):
        '''
        Overwrite comparison operator on equal operator. 
        Input :
            other : another ComparableDict. 
        Output : 
            Return if the two "id" value are the same. 
        '''
        return self.get("id") == other.get("id")
    
    def __lt__(self, other):
        '''
        Overwrite comparison operator on less than operator. 
        Input :
            other : another ComparableDict. 
        Output : 
            Return if this ComparableDict "id" is less than other ComparableDict "id". 
        '''
        try:
            return self.get("id") < other.get("id")
        except:
            return False
