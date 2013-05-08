class MouseMeta(object):

    def press(self, x, y, button = 1):
        """Press the mouse on a givven x, y and button.
        Button is defined as 1 = left, 2 = right, 3 = middle."""
        raise NotImplementedError

    def release(self, x, y, button = 1):
        """Release the mouse on a givven x, y and button.
        Button is defined as 1 = left, 2 = right, 3 = middle."""
        raise NotImplementedError

    def click(self, x, y, button = 1, n = 1):
        """Click a mouse button n times on a given x, y.
        Button is defined as 1 = left, 2 = right, 3 = middle.
        """
        for i in range(n):
            self.press(x, y, button)
            self.release(x, y, button)
 
    def move(self, x, y):
        """Move the mouse to a given x and y"""
        raise NotImplementedError

    def position(self):
        """Get the current mouse position in pixels.
        Returns a tuple of 2 integers"""
        raise NotImplementedError


