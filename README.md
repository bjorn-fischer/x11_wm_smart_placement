# x11_wm_smart_placement
Python demo for discussing smart placement feature for X11 window managers

## Smart Placement for Stacking and Compositing Window Managers

Tiling window managers always had the ability to arrange windows
automatically in a non-overlapping pattern. In addition to fast mouse-free
operation, this is one of the main advantages of this kind of window
managers. Mouse-oriented window managers (stacking and compositing)
have adopted some techniques to reduce the leg work when arranging a
number of windows into a desired setup: edge resistance, snap attact,
et al. Unfortunately none of these techniques get even close to the
feature set of tiling window managers wrt window placement.

What should smart interactive window placement inspired by tiling window
managers look like in stacking window managers? Microsoft™ Windows
11™ has _snap layouts_ which point in the right direction but still
are to messy to use. My idea is to use different key modifiers while
dragging a window. For common window managers the keyboard usually is
idle when dragging a window with the mouse. So why not simply use number
keys ```1``` ```2``` ```3``` ... as _modifiers_ to display different
(predefined) layouts as an overlay to which the dragged window snaps to.

## Smart Placement Demo

```smart_placement_demo.py``` is just a playground for exploring
techniques for smart window placement.

The demo app displays a transparent window which represents the root
window of an X11 session. On this _root window_ there is an abstract
representation of an application window which can be dragged using
the mouse. If a digit key is pressed (and hold) while dragging, a grid
overlay is displayed which the application window snaps to. There are
three predefined grids for the keys ```1```, ```2``` and ```3```. You can
use you own grid specification by stating them as command line arguments.

When ```USE_NEIGHBOUR``` is set to ```True``` in the python script, the
application window also snaps to adjacent combinations of grid elements.

## Design Considerations for Smart Placement

* optional

    This is the most important requirement, which already is fulfilled
    by the demo app by using modifier keys during the dragging
    operation. Unless a modifier key is pressed the dragging procedure
    should behave like prior to the implementation of smart placement. The
    principle of least astonishment should not be violated.

* use short sequences

    The normal operation is **start dragging** a window, **press** and
    hold a **modifier key**, let the window **snap** to the desired
    grid element(s), **drop** the window to stop the dragging mode,
    **release modifier key**. While not particularly short this sequence
    is interleaved between left and right hand, and should feel quite
    naturally. The sequence should not be prolonged without proper
    necessity, though.

* configurable run-time restrictions

* simple to implement

