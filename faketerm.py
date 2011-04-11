#!/usr/bin/env python

from __future__ import with_statement
import curses
import sys

TRANSITION = '*'
CONTEXTS = []

class Slide(object):
    """Base class for all slides.

    It maintains an internal `buffer` of lines to display.  How these are
    interpreted exactly depends on the individual subclass.  All lines
    `print`ed while the context is activated are automatically added to it.

    You activate a context by entering it through the ``with`` statement.  (It
    acts as a *context manager.*)

    """
    def __init__(self, transition=TRANSITION):
        CONTEXTS.append(self)
        self.buffer = []
        self.transition = transition
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
        pass
    def process(self):
        raise NotImplementedError

class chapter(Slide):
    def __init__(self, text='', transition=TRANSITION):
        Slide.__init__(self, transition=transition)
        self.buffer.extend(text.splitlines())
    def prepare(self, win):
        y, x = win.getmaxyx()
        offset = (y - len(self.buffer)) // 2
        for i, line in enumerate(self.buffer):
            win.addstr(offset + i, 0, line.center(x-1))
    def process(self, win, c):
        if c == 10: # return
            raise StopIteration

class bullets(Slide):
    def __init__(self, title):
        self.title = title
        Slide.__init__(self)
    def prepare(self, win):
        win.addstr(self.title + "\n")
        win.addstr(len(self.title) * "=" + "\n\n")
    def process(self, win, c):
        if c in (10, 32): # space or return
            win.addstr("* %s\n" % self.buffer.pop(0))
            if not self.buffer:
                y, x = win.getmaxyx()
                win.move(y-1, x-1)

class shell(Slide):
    ps1 = "$ "
    ps2 = "> "
    def __init__(self):
        self.terminated = False
        Slide.__init__(self)
    def prepare(self, win):
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
                self.prepare(win)
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
    ps1 = ">>> "
    ps2 = "... "

    def throw(self, exc):
        print ("Traceback (most recent call last):\n"
               "  File \"<stdin>\", line 1, in <module>\n"
               "%s: %s" % (exc.__class__.__name__, exc))


def main(source):
    # gather script with presentation instructions
    import runpy
    mod = runpy.run_path(source, globals())
    if '__doc__' in mod:
        with chapter(mod['__doc__'], transition=None):
            if '__author__' in mod:
                print
                print
                print "by %s" % (mod['__author__'],)
        CONTEXTS.insert(0, CONTEXTS.pop()) # move to front

    # now, play the presentation
    play(CONTEXTS)

def play(contexts):
    stdin = sys.stdin.fileno()
    try:
        win = curses.initscr()
        curses.noecho()
        for context in contexts:
            if context.transition is not None: # transition effect
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
            curses.delay_output(200)
            win.clear()
            context.prepare(win)
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
    import sys
    main(sys.argv[1])
