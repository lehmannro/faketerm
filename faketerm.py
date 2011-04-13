#!/usr/bin/env python
"""
Faketerm
========

**Faketerm** allows you to play presentations on your terminal.  You can use it
as a *playback device* if you want to show shell examples, which naturally live
on the console.

Run the example script through ``python faketerm.py example.py``.

It is inspired by `PlayerPiano <http://pypi.python.org/pypi/PlayerPiano>`_ and
requires Python 2.7.

There are actually two phases to a presentation:  parsing and display.

During the parsing phase the presentation script is run (see `main`).  All
created `Slide`s are automatically added sequentially to the timeline (which is
global -- this is a one-shot program).  Parsing is finished when the script ran
completely.  If the script includes a docstring it is added as a title
slide (a `chapter`).

The display phase is the application's mainloop (see `play`).  It initializes
`curses` and replays all slides, ordered and one after another.  When a slide
has been determined to be activated control is mostly handed over to it and
`Slide.prepare` is called.  Events are still received by the mainloop, it just
passes them down to the active slide via `Slide.process`.

When a slide is finished it just needs to throw an error.  Transitions are
shown as requested by the *following* slide (which makes sense as you can have
a transition before your first explicitly added slide due to the automatically
generated title slide, but never after your last slide).

"""
from __future__ import with_statement
import curses
import sys


TRANSITION = "*"
TIMELINE = []


class Slide(object):
    """Base class for all slides.  It parses the presentation script and
    manages the display.  While the former is generically implemented in this
    class, the latter needs to be implemented by subclasses.

    It maintains an internal `buffer` of lines to display.  How these are
    interpreted exactly depends on the individual subclass.  All lines
    `print`ed while the context is activated are automatically added to it.
    Slides also partially implement the `file` protocol to achieve this, ie.
    `softspace` and `write`.

    Presentation authors add information to a slide by entering it through the
    ``with`` statement.  It acts as a *context manager.*

    >>> a = Slide()
    >>> with a:  # usually collapsed to ``with Slide():``
    ...     print "first line"
    ...     print "second line"
    ...
    >>> a.buffer
    ['first line', 'second line']

    Transitions can be configured by setting :attr:`transition`.  If it is a
    character the screen will be swiped clean with that glyph;  the screen will
    flash that number of times if it is an integer.  To have a blank
    transition, set it to ``None``.

    """
    def __init__(self):
        # needed by mainloop
        TIMELINE.append(self)
        self.transition = TRANSITION
        # file-like interface
        self.buffer = []
        self.softspace = 0

    def __enter__(self):
        self.stdout_orig = sys.stdout
        sys.stdout = self
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.stdout_orig

    def write(self, line):
        if not (self.softspace and line == '\n'):
            self.buffer.append(line)

    def prepare(self, win):
        """Called when control is handed over to a slide.

        :param win: curses window

        """
        pass

    def process(self, win, c):
        """Called when an event is received while activated.

        :param win: curses window
        :param c: character code

        """
        raise NotImplementedError


class chapter(Slide):
    """Cover page for individual chapters.  All text is centered."""

    def prepare(self, win):
        y, x = win.getmaxyx()
        offset = (y - len(self.buffer)) // 2
        for i, line in enumerate(self.buffer):
            win.addstr(offset + i, 0, line.center(x-1))

    def process(self, win, c):
        if c == 10: # return
            raise StopIteration


BULLET = "*"
UNDERLINE = "="

class bullets(Slide):
    """List of items.  Each bullet point is shown sequentially, after pressing
    Enter or Space.

    """
    def __init__(self, title, bullet=BULLET, underline=UNDERLINE):
        self.title = title
        self.bullet = bullet
        self.underline = underline
        self.last = None
        Slide.__init__(self)

    def prepare(self, win):
        win.addstr(self.title + "\n")
        win.addstr(len(self.title) * self.underline + "\n\n")

    def process(self, win, c):
        if c in (10, 32): # space or return
            win.deleteln()
            if self.last is not None:
                win.addstr("%s %s\n" % (self.bullet, self.last))
            self.last = self.buffer.pop()
            win.addstr("%s %s" % (self.bullet, self.last), curses.A_BOLD)
            y, x = win.getyx()
            win.move(y, 0)
            if not self.buffer:
                y, x = win.getmaxyx()
                win.move(y-1, x-1)


class shell(Slide):
    """Shell interaction.  Input is shown after each keypress, output after you
    press Enter.  I/O is added by individual print statements.

    :attr ps1: initial prompt
    :attr ps2: prompt after an embedded newline

    """
    ps1 = "$ "
    ps2 = "> "

    def __init__(self):
        self.terminated = False
        Slide.__init__(self)

    def prepare(self, win):
        self.next_action(win)

    def next_action(self, win):
        win.addstr(self.ps1)
        if self.buffer:
            self.pos = 0
            self.cmd = self.buffer.pop(0)
            self.len = len(self.cmd)
        else:
            self.terminated = True

    def process(self, win, c):
        if c == 10:
            if self.terminated:
                raise StopIteration
            if self.pos >= self.len:
                win.addstr("\n%s\n" % self.buffer.pop(0))
                self.next_action(win)
                return
        if self.pos < self.len:
            ch = self.cmd[self.pos]
            if ch == '\n':
                if c == 10:
                    ch += self.ps2
                else:
                    return
            win.addstr(ch)
            self.pos += 1

class pyshell(shell):
    """A shell resembling the interactive Python interpreter."""
    ps1 = ">>> "
    ps2 = "... "

    def throw(self, exc):
        print ("Traceback (most recent call last):\n"
               "  File \"<stdin>\", line 1, in <module>\n"
               "%s: %s" % (exc.__class__.__name__, exc))


def main(source):
    """Parse a script of presentation instructions and run it."""
    import runpy
    mod = runpy.run_path(source, globals())
    if '__doc__' in mod:
        with chapter() as title:
            title.transition = None
            for line in mod['__doc__'].strip().splitlines():
                print line
            if '__author__' in mod:
                print
                print
                print "by %s" % (mod['__author__'],)
        TIMELINE.insert(0, TIMELINE.pop()) # move to front

    # now, play the presentation
    play(TIMELINE)

def play(contexts):
    """Play back a sequence of `contexts`."""
    try:
        win = curses.initscr()
        curses.noecho()
        for context in contexts:
            # transition effect
            if context.transition is not None:
                if isinstance(context.transition, int):
                    for _ in xrange(context.transition):
                        curses.flash()
                        curses.delay_output(350)
                else:
                    y, x = win.getmaxyx()
                    for i in xrange(x):
                        for j in xrange(y):
                            if i != x-1 or j != y-1:
                                win.addch(j, i, ord(context.transition))
                        win.refresh()
                        curses.delay_output(7)

            # load next slide
            curses.delay_output(200)
            win.clear()
            context.prepare(win)

            # mainloop
            while 1:
                c = win.getch()
                try:
                    context.process(win, c)
                except Exception:
                    break

        # finished
        y, x = win.getmaxyx()
        outro = "  Press ESC to exit presentation mode. "
        win.addnstr(y-1, max(0, x-len(outro)-1), outro, x-1,
                    curses.A_REVERSE)
        while 1:
            c = win.getch()
            if c == 27:
                break
    finally:
        curses.reset_shell_mode()
        curses.endwin()


if __name__ == '__main__':
    main(sys.argv[1])
