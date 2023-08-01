






from threading import Event

class ChildEvent(Event):
  def __init__(self,parent = None):
    super().__init()
    self._parent = parent

  def set_parent(self,parent):
    self._parent = parent

  def set(self):
    super().set()
    self._parent.update()

  def clear(self):
    super().clear()
    self._parent.update()


class AndEvent(Event):
    
  def __init__(self, *events):
    super().__init__()
    self._children: list[ChildEvent] = list(events)
    for event in self._children:
      event.set_parent(self)
    
  def update(self):
    bools = [e.is_set() for e in self._children]
    if all(bools):
      self.set()
    else:
      self.clear()

  def addChild(self, child):
    self._children.append(child)
  
class OrEvent(Event):
    
  def __init__(self, *events):
    super().__init__()
    self._children: list[ChildEvent] = list(events)
    for event in self._children:
      event.set_parent(self)    
      
  def update(self):
    bools = [e.is_set() for e in self._children]
    if any(bools):
      self.set()
    else:
      self.clear()

  def addChild(self, child):
    self._children.append(child)
  
