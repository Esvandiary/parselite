from __future__ import print_function, division
import filewatcher
import os
import watchdog.observers
import watchdog.events

class DirectoryWatcher(watchdog.events.RegexMatchingEventHandler):
  def __init__(self, path, from_start = True, regexes, recursive = True, ignore_directories = False, case_sensitive = False):
    super(DirectoryWatcher, self).__init__(regexes, ignore_directories=ignore_directories, case_sensitive=case_sensitive)
    self._observer = watchdog.observers.Observer()
    self._observer.schedule(self, path, recursive=recursive)
    self._callbacks = []
    self._current_file = None

  def start(self):
    self._observer.start()

  def stop(self, block = True):
    self._observer.stop()
    if block:
      self._observer.join()
 
  def add_callback(self, message_types, fn, queue = None):
    self._callbacks.append((message_types, fn, queue))

  def remove_callback(fn):
    self._callbacks = [(t, f, q) for (t, f, q) in self._callbacks if f != fn]

  def on_created(self, event):
    # TODO: update current file
    pass

  def on_modified(self, event):
    # TODO: pass data onto FileWatcher, if this method is fast and reliable enough?
    pass

  def on_deleted(self, event):
    # TODO: check it's not our current active file, and ... do something ... if it is
    pass

