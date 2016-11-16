from __future__ import print_function, division
from .messages import journal_messages as m_journal
from . import gameversion

class MessageParser(object):
  def __init__(self, version_info):
    self._message_version = version_info

  def parse(self, data):
    raise NotImplementedError("invalid use of base MessageParser's parse method")


class JournalParser(MessageParser):
  def __init__(self, version_info):
    super(JournalParser, self).__init__(version_info)
    verstr = gameversion.get_version_string(version_info['version'], version_info['build'])
    self._valid_versions = m_journal.get_valid_versions(verstr)

  def parse(self, data):
    return m_journal.create_message(self._valid_versions, data)


_parsers = {
  "journal": JournalParser,
}

def create_parser(message_type, version_info):
  if message_type in _parsers:
    return _parsers[message_type](version_info)
  else:
    return None
