import time
import random

#-------------------------------------------------------------------
def wait_r(k,v):
    """ sleep everything for X time 
    """
    wait = round(random.uniform(k,v), 4)
    return time.sleep(wait)

#-------------------------------------------------------------------
class KeybdMeta(object):
    """The base class for Keybd.
    """

    def press_key(self, character=''):
        """Press a given character key."""
        raise NotImplementedError

    def release_key(self, character=''):
        """Release a given character key."""
        raise NotImplementedError

    def tap_key(self, character='', n=1, interval=0):
        """Press and release a given character key n times."""
        for i in xrange(n):
            self.press_key(character)
            wait_r(0.007, 0.015)
            self.release_key(character)
            time.sleep(interval)

    def type_string(self, char_string, interval=0):
        """A convenience method for typing longer strings of characters."""
        for i in char_string:
            time.sleep(interval)
            self.tap_key(i)

    def special_key_assignment(self):
        """Makes special keys more accessible."""
        raise NotImplementedError

    def lookup_character_value(self, character):
        """
        If necessary, lookup a valid API value for the key press from the
        character.
        """
        raise NotImplementedError

    def is_char_shifted(self, character):
        """Returns True if the key character is uppercase or shifted."""
        if character.isupper():
            return True
        if character in '<>?:"{}|~!@#$%^&*()_+=':
            return True
        return False
