from __future__ import print_function, division
import os
import threading
import time

class FileWatcher(object):
  def __init__(self, source, from_start = True, thread_name_prefix = 'FileWatcher'):
    self._source = source
    self._from_start = from_start
    self._thread_prefix = thread_name_prefix
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
    if not self._running:
      self._thread = threading.Thread(target=self._run, name='{}-{}'.format(self._thread_prefix, self._source.fileno()))
      self._thread.daemon = True
      self._wait_condition = threading.Condition()
      self._running = True
      self._thread.start()
      return True
    else:
      return False

  def stop(self):
    if self._running:
      self._running = False
      if self._thread is not None and self._thread.is_alive():
        self._wait_condition.acquire()
        self._wait_condition.notify_all()
        self._wait_condition.release()
        self._thread.join()
      self._thread = None
      self._wait_condition = None
      return True
    else:
      return False

  def _run(self):
    cur_size = 0 if self._from_start else self._get_current_size()
    self._source.seek(cur_size)
    while self._running:
      iter_start_time = time.clock()
      new_size = self._get_current_size()
      if new_size > cur_size:
        for new_msg in self._get_new_messages(new_size, cur_size):
          self._execute_callbacks(new_msg)
      cur_size = new_size
      self._wait_condition.acquire()
      self._wait_condition.wait(self._poll_frequency - (time.clock() - iter_start_time))
      self._wait_condition.release()

  def _get_new_messages(self, new_size, cur_size):
    raise NotImplementedError("invalid use of base FileWatcher's message process method")

  def _execute_callbacks(self, message):
    for (types, fn) in self._callbacks:
      if self._is_callback_match(types, message):
        fn(message)

  def _is_callback_match(self, types, message):
    raise NotImplementedError("invalid use of base FileWatcher's callback match method")

  def _get_current_size(self):
    return os.fstat(self._source.fileno()).st_size

  def __del__(self):
    self.stop()


class LineBasedFileWatcher(FileWatcher):
  def _get_new_messages(self, new_size, cur_size):
    return self._source.readlines()

  def _is_callback_match(self, types, message):
    return True
