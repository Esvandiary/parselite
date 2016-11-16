from __future__ import print_function, division
import re


_re_buildstr = re.compile("^\\s*r(?P<client>\\d+)/r(?P<server>\\d+)\\s*$")
_re_simplever = re.compile("^(?P<major>\\d+)\\.(?P<minor>\\d+)$")


_build_mapping = {
  "2.2": {
    124484: "2.2.00",
    125374: "2.2.01",
    126898: "2.2.02",
  }
}


def get_version_string(gameversion, buildstr):
  buildmatch = _re_buildstr.match(buildstr)
  if buildmatch is not None:
    cbuild = int(buildmatch.group("client"))
    if gameversion in _build_mapping and cbuild in _build_mapping[gameversion]:
      return _build_mapping[gameversion][cbuild]
  return gameversion


def is_simple_version(verstr):
  return (_re_simplever.match(verstr) is not None)
