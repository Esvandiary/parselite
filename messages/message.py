from __future__ import print_function, division
import datetime

class Message(object):
  def __init__(self, data, raw_data = None, source = None, time = datetime.now()):
    self._source = source
    self._data = data
    self._raw_data = raw_data
    self._time = time

  @property
  def data(self):
    return self._data

  @property
  def raw_data(self):
    return self._raw_data

  @property
  def time(self):
    return self._time

