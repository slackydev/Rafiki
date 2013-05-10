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

