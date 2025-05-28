import re


class AnyType(str):
    """A special class that is always equal in not equal comparisons.
        Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


class ContainsAnyDict(dict):
    def __contains__(self, key):
        return True

    def __init__(self, type):
        self.type = type

    def __getitem__(self, key):
        return (self.type, )


def get_last_audio_from_args(kwargs, reGetGroup=re.compile("^audio([0-9]+)$")):
    last_audio = 0

    for key in kwargs.keys():
        m = reGetGroup.match(key)
        if m is not None:
            i = int(m.group(1))
            if i >= last_audio:
                last_audio = i
    return last_audio
