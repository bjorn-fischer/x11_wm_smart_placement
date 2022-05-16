#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

gridSpec = (
        '2,1',
        '3,3,1',
        '3,2,2')

USE_NEIGHBOUR = True
NEIGHBOUR_DIST = 30

class Rect(object):
    __slots__ = ('x1', 'y1', 'x2', 'y2')
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def contains(self, x, y):
        return x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2;

class Grid:
    def __init__(self, width, height, spec=''):
        self.width = width
        self.height = height
        self.spec = spec

        cols = [ int(x) for x in spec.split(',') ]

        self.rects = list()
        for x in range(len(cols)):
            x1 = x * (width / len(cols))
            x2 = (x + 1) * (width / len(cols))
            for y in range(cols[x]):
                y1 = y * (height / cols[x])
                y2 = (y + 1) * (height / cols[x])
                self.rects.append(Rect(x1, y1, x2, y2))

    def getRect(self, x, y):
        (x1, y1, x2, y2) = (-1, -1, -1, -1)
        for rect in self.rects:
            if rect.contains(x, y):
                (x1, y1, x2, y2) = (rect.x1, rect.y1, rect.x2, rect.y2)
                if not USE_NEIGHBOUR:
                    return (x1, y1, x2, y2)
                break

        if x1 >= 0:
            for rect in self.rects:
                if rect.contains(x - NEIGHBOUR_DIST, y):
                    x1 = rect.x1
                if rect.contains(x + NEIGHBOUR_DIST, y):
                    x2 = rect.x2
                if rect.contains(x, y - NEIGHBOUR_DIST):
                    y1 = rect.y1
                if rect.contains(x, y + NEIGHBOUR_DIST):
                    y2 = rect.y2
            return (x1, y1, x2, y2)

        return (-1, -1, -1, -1)

class RootFrame(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        self.set_size_request(100, 100)
        self.vexpand = True
        self.hexpand = True
        self.surface = None

        self.spec = ''

        self.area = Gtk.DrawingArea()
        self.add(self.area)

        self.area.connect("draw", self.onDraw)
        self.area.connect('configure-event', self.onConfigure)

    def init_surface(self, area):
        # Destroy previous buffer
        if self.surface is not None:
            self.surface.finish()
            self.surface = None

        self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                area.get_allocated_width(),
                area.get_allocated_height())

    def redraw(self):
        self.init_surface(self.area)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgba(0, 0, .6, .9)

        if self.spec != '':
            self.drawGrid(ctx)

        self.surface.flush()

    def onConfigure(self, area, event, data=None):
        self.redraw()
        return False

    def onDraw(self, area, context):
        if self.surface is not None:
            context.set_source_surface(self.surface, 0.0, 0.0)
            context.paint()
        else:
            print('Invalid surface')
        return False

    def setGrid(self, spec):
        self.spec = spec

        if self.spec == '':
            if hasattr(self, 'grid'):
                del self.grid
                self.queue_draw()
                self.redraw()
            return

        width = self.get_allocated_width()
        height = self.get_allocated_height()

        self.grid = Grid(width, height, self.spec)
        self.queue_draw()
        self.redraw()

    def drawGrid(self, ctx):
        if not hasattr(self, 'grid'):
            return

        ctx.set_line_width(7)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        for rect in self.grid.rects:
            ctx.move_to(rect.x1, rect.y1)
            ctx.line_to(rect.x2, rect.y1)
            ctx.line_to(rect.x2, rect.y2)
            ctx.line_to(rect.x1, rect.y2)
            ctx.line_to(rect.x1, rect.y1)

        ctx.close_path()
        ctx.stroke()

class WindowFrame(Gtk.Bin):
    def __init__(self, width, height):
        super().__init__()
        self.set_size_request(width, height)
        self.vexpand = False
        self.hexpand = False
        self.surface = None
        self.opacity = 1

        self.area = Gtk.DrawingArea()
        self.add(self.area)

        self.area.connect("draw", self.onDraw)
        self.area.connect('configure-event', self.onConfigure)

    def init_surface(self, area):
        if self.surface is not None:
            self.surface.finish()
            self.surface = None

        self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                area.get_allocated_width(),
                area.get_allocated_height())

    def redraw(self):
        self.init_surface(self.area)
        ctx = cairo.Context(self.surface)
        ctx.scale(self.surface.get_width(), self.surface.get_height())
        ctx.rectangle(0, 0, 1, 1)
        ctx.set_source_rgba(.5, .5, .5, self.opacity)
        ctx.fill()
        self.surface.flush()

    def onConfigure(self, area, event, data=None):
        self.redraw()
        return False

    def onDraw(self, area, context):
        if self.surface is not None:
            context.set_source_surface(self.surface, 0.0, 0.0)
            context.paint()
        else:
            print('Invalid surface')
        return False

class RootWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("Window Manager Smart Placement Demo")
        self.set_default_size(1200, 800)
        self.connect("destroy", Gtk.main_quit)
        self.connect('draw', self.draw)
        self.drag = False

        self.set_events(
                Gdk.EventMask.BUTTON_PRESS_MASK |
                Gdk.EventMask.BUTTON_RELEASE_MASK |
                Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.connect("button_press_event", self.onMousePress)
        self.connect("button_release_event", self.onMouseRelease)
        self.connect("motion_notify_event", self.onMouseMove)
        self.connect("key-press-event",self.onKeyPress)
        self.connect("key-release-event",self.onKeyRelease)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)
        self.show_all()

        self.root = RootFrame()
        self.fixed = Gtk.Fixed()
        self.fixed.set_halign(Gtk.Align.START)
        self.fixed.set_valign(Gtk.Align.START)

        self.origWidth = 500
        self.origHeight = 400
        self.window = WindowFrame(self.origWidth, self.origHeight)

        self.fixed.put(self.window, 100, 100)
        self.root.add_overlay(self.fixed)
        self.add(self.root)

    def onKeyPress(self, widget, event):
        if event.keyval == Gdk.KEY_q or event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
            return

        if not self.drag:
            self.root.setGrid('')
            return

        num = event.keyval - Gdk.KEY_1
        if num in range(len(gridSpec)):
            self.root.setGrid(gridSpec[num])
        else:
            self.root.setGrid('')

    def onKeyRelease(self, widget, event):
        self.root.setGrid('')

    def onMouseRelease(self, widget, event):
        if event.button == 1:
            self.drag = False
            self.window.opacity = 1
            self.queue_draw()
            self.window.redraw()

    def onMousePress(self, widget, event):
        if event.button == 1:
            a = self.window.get_allocation()
            if (event.x >= a.x and event.x <= a.x + a.width and
                    event.y >= a.y and event.y <= a.y + a.height):
                self.offsetX = event.x - a.x
                self.offsetY = event.y - a.y
                self.drag = True
                self.window.opacity = .7
            else:
                self.window.opacity = 1
                self.drag = False
                self.window.redraw()

    def onMouseMove(self, widget, event):
        if self.drag:
            if self.root.spec == '':
                self.fixed.move(self.window, event.x - self.offsetX, event.y - self.offsetY)
                self.window.set_size_request(self.origWidth, self.origHeight)
            else:
                (x1, y1, x2, y2) = self.root.grid.getRect(event.x, event.y)
                if x1 >= 0:
                    self.fixed.move(self.window, x1, y1)
                    self.window.set_size_request(x2 - x1, y2 - y1)

    def draw(self, widget, context):
        context.set_source_rgba(0, 0, 0, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)

if len(sys.argv) > 1:
    gridSpec = sys.argv[1:]

window = RootWindow()
window.show_all()
Gtk.main()

