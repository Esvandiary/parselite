from __future__ import print_function, division
import messages.journal as m_journal

class MessageParser(object):
  def __init__(self, version_info):
    self._message_version = version_info

  def parse(self, message):
    raise NotImplementedError("invalid use of base MessageParser's parse method")


class JournalParser(MessageParser):
  def __init__(self, version_info):
    super(JournalParser, self).__init__(version_info)
    self._load_messages()

  def _load_messages(self):
    self._messages = {}
    versions = m_journal.get_valid_versions(self._message_version['version'])
    for name, elems in m_journal.messages.items():
      for v in versions:
        if v in elems:
          self._messages[name] = elems[v]
          break

_parsers = {
  "journal": JournalParser,
}

def create_parser(message_type, version_info):
  if message_type in _parsers:
    return _parsers[message_type](version_info)
  else:
    return None