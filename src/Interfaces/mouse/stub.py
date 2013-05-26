#!/usr/bin/env python
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 This file is part of the Rafiki Macro Library (RML)
 Copyright (c) 2012-2013 by Jarl Holta

 RML is free software: you can redistribute it and/or modify
 it under the terms of the wxWindows licence.

 RML is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

 wxWindows licence: <http://opensource.org/licenses/wxwindows.php>
 You might have recieved a copy of the lisence.

 --- MouseCtrl-frame for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 

class MouseMeta(object):
	#--------------------------------------------------------------------
    def press(self, x, y, button = 1):
        """ Press the mouse on a givven x, y and button.
            1 = left, 2 = middle, 3 = right
        """
        raise NotImplementedError

    def release(self, x, y, button = 1):
        """ Release the mouse on a givven x, y and button.
            1 = left, 2 = middle, 3 = right
        """
        raise NotImplementedError

    def click(self, x, y, button = 1, n = 1):
        """ Click a mouse button n times at a given position.
            1 = left, 2 = middle, 3 = right
        """
        for i in range(n):
            self.press(x, y, button)
            self.release(x, y, button)

    def state(self, btn):
        """ Check weather a button is pressed down or not """
        raise NotImplementedError
 
    def move(self, x, y):
        """ Move the mouse to a given position defined by `x` and `y` """
        raise NotImplementedError

    def position(self):
        """ Get the current mouse position in pixels.
            Returns a tuple of 2 integers
        """
        raise NotImplementedError

