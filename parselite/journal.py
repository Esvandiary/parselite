from __future__ import print_function, division
import io
import json
import logging
import os
import threading
import time
from . import parsing

log = logging.getLogger("journal")


class JournalFile(io.IOBase):
  def __init__(self, filename, keep_raw = False):
    self._filename = filename
    self._fd = None
    self._parser = None
    self._keep_raw_data = keep_raw

  def open(self):
    self._fd = open(self._filename, 'r', 1)  # 0 = unbuffered, 1 = line-buffered
    header = self.readline()
    if header:
      # Read header data and act on it
      self._parser = parsing.create_parser("journal", {'version': header['gameversion'], 'build': header['build']})
      # Reset file to start
      self._fd.seek(0)
    else:
      raise InvalidDataError("could not read journal file header", None)

  def close(self):
    if not self.closed:
      self._fd.close()

  @property
  def closed(self):
    return (self._fd is None or self._fd.closed)

  def fileno(self):
    if self._fd:
      return self._fd.fileno()
    else:
      return None

  def flush(self):
    if not self.closed:
      self._fd.flush()

  def isatty(self):
    return False

  def readable(self):
    return True

  def readall(self):
    return list(self.readlines())

  def readline(self, size = -1):
    if not self.closed:
      data = self._fd.readline(size)
      if data:
        try:
          jdata = json.loads(data)
          if self._parser:
            obj = self._parser.parse(jdata)
            if self._keep_raw_data:
              obj.raw_data = data
            return obj
          else:
            return jdata
        except Exception as ex:
          raise
      else:
        return None
    else:
      raise IOError("tried to call readline on a closed journal file")

  def readlines(self, hint = -1):
    if not self.closed:
      line_cnt = 0
      valid_result = True
      while valid_result and (hint < 0 or line_cnt < hint):
        line_cnt += 1
        try:
          result = self.readline()
          if result:
            yield result
          else:
            return
        except Exception as ex:
          log.warning("Failed to parse file {} line {}: {}".format(self._filename, line_cnt, str(ex)))
    else:
      raise IOError("tried to call readlines on a closed journal file")

  def seek(self):
    raise io.UnsupportedOperation("journal file does not support seeking")

  def seekable(self):
    return False

  def tell(self):
    raise io.UnsupportedOperation("journal file does not support telling")

  def truncate(self, size = None):
    raise io.UnsupportedOperation("journal file does not support truncating")

  def writable(self):
    return False

  def writelines(self, lines):
    raise io.UnsupportedOperation("journal file does not support writelines")

  def __enter__(self):
    self.open()
    return self

  def __exit__(self, typ, value, traceback):
    self.close()

  __iter__ = readlines


class JournalFileWatcher(object):
  def __init__(self, source, from_start = True):
    self._source = source
    self._from_start = from_start
    self._thread = None
    self._wait_condition = None
    self._callbacks = []
    self._running = False
    self._poll_frequency = 0.1  # seconds

  def add_callback(self, message_types, fn):
    self._callbacks.append((message_types, fn))

  def remove_callback(self, fn):
    self._callbacks = [(k, v) for (k, v) in self._callbacks if v != fn]

  def start(self):
    self._thread = threading.Thread(self._run, name='JournalWatcher-{}'.format(self._source.fileno()))
    self._wait_condition = threading.Condition()
    self._thread.start()

  def stop(self):
    if self._running:
      self._running = False
      if self._thread.is_alive():
        self._wait_condition.acquire()
        self._wait_condition.notify_all()
        self._wait_condition.release()
        self._thread.join()
      return True
    else:
      return False

  def _run(self):
    cur_size = 0 if self._from_start else self._get_current_size()
    while self._running:
      iter_start_time = time.clock()
      new_size = self._get_current_size()
      if new_size > cur_size:
        for new_msg in self._source.readlines():
          self._execute_callbacks(new_msg)
      cur_size = new_size
      self._wait_condition.acquire()
      self._wait_condition.wait(self._poll_frequency - (time.clock() - iter_start_time))
      self._wait_condition.release()

  def _execute_callbacks(self, message):
    for (types, fn) in self._callbacks:
      if any([isinstance(message, t) for t in types]):
        fn(message)

  def _get_current_size(self):
    return os.fstat(self._source.fileno()).st_size


class InvalidDataError(Exception):
  def __init__(self, message, data_line = None):
    self.message = message
    self.data = data_line

