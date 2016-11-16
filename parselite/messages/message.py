from __future__ import print_function, division
import datetime

class Message(object):
  def __init__(self, data, time = datetime.datetime.now(), source = None, raw_data = None):
    self._source = source
    self._data = data
    self._time = time
    # Allow setting raw data manually later if needed
    self.raw_data = raw_data

  @property
  def data(self):
    return self._data

  @property
  def time(self):
    return self._time

