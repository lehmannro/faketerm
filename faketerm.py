#!/usr/bin/env python

from __future__ import with_statement
import curses
import sys

TRANSITION = '*'
CONTEXTS = []

class Context(object):
    def __init__(self, transition=TRANSITION):
        CONTEXTS.append(self)
        self.buffer = []
        self.transition = transition
        self.softspace = 0
    def __enter__(self):
        self.stdout_orig = sys.stdout
        sys.stdout = self
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.stdout_orig
    def write(self, line):
        if not (self.softspace and line == '\n'):
            self.buffer.append(line)
    def prepare(self, win):
        pass
    def process(self):
        raise NotImplementedError

class slide(Context):
    def __init__(self, title):
        self.title = title
        Context.__init__(self)
    def prepare(self, win):
        win.addstr(self.title + "\n")
        win.addstr(len(self.title) * "=" + "\n\n")
    def process(self, win, c):
        if c in (10, 32): # space or return
            win.addstr("* %s\n" % self.buffer.pop(0))
            if not self.buffer:
                y, x = win.getmaxyx()
                win.move(y-1, x-1)

class shell(Context):
    ps1 = "$ "
    def __init__(self):
        self.terminated = False
        Context.__init__(self)
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
            win.addstr(self.cmd[self.pos])
            self.pos += 1

class pyshell(shell):
    ps1 = ">>> "

class python(Context):
    pass

def main(source):
    # gather script with presentation instructions
    execfile(source)

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
        while 1:
            c = win.getch()
            if c == 27:
                break
    finally:
        curses.reset_shell_mode()

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
