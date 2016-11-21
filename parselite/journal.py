from __future__ import print_function, division
import io
import json
import logging
import os

from . import parsing
from . import filewatcher

log = logging.getLogger("journal")

default_journal_directory = os.path.join(os.path.expanduser('~'), "Saved Games", "Frontier Developments", "Elite Dangerous")


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
    self._parser = None

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

  def seek(self, loc, rel = 0):
    return self._fd.seek(loc, rel)

  def seekable(self):
    return True

  def tell(self):
    return self._fd.tell()

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


class JournalFileWatcher(filewatcher.LineBasedFileWatcher):
  def __init__(self, source, from_start = True, poll_interval = filewatcher.default_poll_interval):
    if not isinstance(source, JournalFile):
      source = JournalFile(source)
      self._control_source = True
    super(JournalFileWatcher, self).__init__(source, from_start, thread_name_prefix='JournalWatcher', poll_interval=poll_interval)

  def _is_callback_match(self, types, message):
    return (types is None or message.event in types)

  def start(self):
    if self._control_source:
      self._source.open()
    super(JournalFileWatcher, self).start()

  def stop(self):
    super(JournalFileWatcher, self).stop()
    if self._control_source:
      self._source.close()


class InvalidDataError(Exception):
  def __init__(self, message, data_line = None):
    self.message = message
    self.data = data_line
