from __future__ import print_function, division
import collections
import logging
import os
import threading
import time

log = logging.getLogger("filewatcher")

default_poll_interval = 0.1  # seconds

class _QueueData(object):
  def __init__(self, name):
    self.name = name
    self.thread = None
    self.condition = threading.Condition()
    self.queue = collections.deque()
    self.running = False

class FileWatcher(object):
  def __init__(self, source, from_start = True, thread_name_prefix = 'FileWatcher', poll_interval = default_poll_interval):
    self._source = source
    self._from_start = from_start
    self._thread_prefix = thread_name_prefix
    self._thread = None
    self._wait_condition = None
    self._callbacks = []
    self._queues = {}
    self._running = False
    self._poll_interval = poll_interval

  def add_callback(self, message_types, fn, queue = None):
    if queue is not None and queue not in self._queues:
      log.debug("Setting up new queue '{}'".format(queue))
      self._queues[queue] = _QueueData(queue)
      if self._running:
        self._start_queue(queue)
    self._callbacks.append((message_types, fn, queue))

  def remove_callback(self, fn):
    self._callbacks = [(t, f, q) for (t, f, q) in self._callbacks if f != fn]
    # Now see if we have any unused queues
    zero_queues = set(self._queues.keys()) - set([t[2] for t in self._callbacks])
    for qname in zero_queues:
      log.debug("Stopping unused queue '{}'".format(qname))
      qdata = self._queues[qname]
      qdata.running = False
      if qdata.thread.is_alive():
        qdata.condition.acquire()
        qdata.condition.notify_all()
        qdata.condition.release()
        log.debug("Waiting for unused queue '{}' to join...".format(qname))
        qdata.thread.join()
        log.debug("Stopped unused queue '{}'".format(qname))
        qdata.thread = None
      del self._queues[qname]

  def read_all(self):
    if not self._running:
      self._running = True
      # Store current position for later
      old_pos = self._source.tell()
      self._source.seek(0)
      # Clear queues to force everything to happen synchronously
      old_queues = self._queues
      self._queues = {}
      new_size = self._get_current_size()
      for new_msg in self._get_new_messages(new_size, 0):
        self._execute_callbacks(new_msg)
      # Put source back where it was
      self._source.seek(old_pos)
      # Put queues back
      self._queues = old_queues
      self._running = False
      return True
    else:
      return False

  def start(self):
    if not self._running:
      self._thread = threading.Thread(target=self._run, name='{}-{}'.format(self._thread_prefix, self._source.fileno()))
      self._thread.daemon = True
      self._wait_condition = threading.Condition()
      self._running = True
      for qdata in list(self._queues.values()):
        self._start_queue(qdata)
      self._thread.start()
      return True
    else:
      return False

  def stop(self):
    if self._running:
      self._running = False
      log.debug("Stopping file watcher for {}".format(self._source))
      if self._thread is not None and self._thread.is_alive():
        self._wait_condition.acquire()
        self._wait_condition.notify_all()
        self._wait_condition.release()
        log.debug("Waiting for file watcher thread to join...")
        self._thread.join()
        log.debug("File watcher thread exited.")
        for qname, qdata in list(self._queues.items()):
          qdata = self._queues[qname]
          qdata.running = False
          if qdata.thread.is_alive():
            qdata.condition.acquire()
            qdata.condition.notify_all()
            qdata.condition.release()
            log.debug("Waiting for queue thread for queue '{}' to join...".format(qname))
            qdata.thread.join()
            log.debug("Queue thread for '{}' exited.".format(qname))
            qdata.thread = None
      self._thread = None
      self._wait_condition = None
      return True
    else:
      return False

  def check_for_data(self):
    if self._running:
      self._wait_condition.acquire()
      self._wait_condition.notify_all()
      self._wait_condition.release()
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
      timeout = (self._poll_interval - (time.clock() - iter_start_time)) if self._poll_interval else None
      if timeout is not None and timeout > 0.0:
        self._wait_condition.acquire()
        if self._running:
          self._wait_condition.wait(timeout)
        self._wait_condition.release()

  def _start_queue(self, qdata):
    log.debug("Starting queue '{}'".format(qdata.name))
    qdata.running = True
    qdata.thread = threading.Thread(target=self._run_queue, kwargs={'qdata': qdata}, name='{}-Q{}'.format(self._thread_prefix, qdata.name))
    qdata.thread.start()

  def _run_queue(self, qdata):
    qdata.running = True
    while self._running and qdata.running:
      callbacks = [(types, fn) for (types, fn, queue) in self._callbacks if queue == qdata.name]
      while any(qdata.queue):
        message = qdata.queue.popleft()
        for (types, fn) in callbacks:
          if self._is_callback_match(types, message):
            fn(message)
      qdata.condition.acquire()
      if self._running and qdata.running:
        qdata.condition.wait()
      qdata.condition.release()

  def _get_new_messages(self, new_size, cur_size):
    raise NotImplementedError("invalid use of base FileWatcher's message process method")

  def _execute_callbacks(self, message):
    for (types, fn, queue) in self._callbacks:
      if self._is_callback_match(types, message):
        if queue is None or queue not in self._queues:
          fn(message)
        else:
          qdata = self._queues[queue]
          qdata.queue.append(message)
          qdata.condition.acquire()
          qdata.condition.notify_all()
          qdata.condition.release()

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
