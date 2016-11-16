from __future__ import print_function, division
import io
import json
import logging
import threading

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
      self._parser = parsing.MessageParser("journal", {'version': header['gameversion'], 'build': header['build']})
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
          obj = json.loads(data)
          return MAGICAL_PARSING(obj, self._keep_raw_data)
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



class JournalWatcher(object):
  def __init__(self, source):
    self._source = source
    self._thread = None
    self._callbacks = []

  def add_callback(self, message_types, fn):
    self._callbacks.append((message_types, fn))

  def remove_callback(self, fn):
    self._callbacks = [(k, v) for (k, v) in self._callbacks if v != fn]

  def start(self):
    raise NotImplementedError("start")

  def stop(self):
    raise NotImplementedError("stop")


class InvalidDataError(Exception):
  def __init__(self, message, data_line = None):
    self.message = message
    self.data = data_line