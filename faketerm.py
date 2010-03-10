#!/usr/bin/env python

from __future__ import with_statement
import curses
import sys

CONTEXTS = []

class Context:
    def __init__(self):
        self.buffer = []
        CONTEXTS.append(self)
    def __enter__(self):
        self.stdout_orig = sys.stdout
        sys.stdout = self
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.stdout_orig
    def write(self, line):
        if line != '\n':
            self.buffer.append(line)
    def __call__(self, win):
        pass
    def process(self):
        raise NotImplementedError

class slide(Context):
    def __init__(self, title):
        self.title = title
        Context.__init__(self)
    def __call__(self, win):
        win.addstr(self.title + "\n")
        win.addstr(len(self.title) * "=" + "\n\n")
    def process(self, win, c):
        if c in (10, 32): # space or return
            win.addstr("* %s\n" % self.buffer.pop(0))

class shell(Context):
    ps1 = "$ "
    def __init__(self):
        self.terminated = False
        Context.__init__(self)
    def __call__(self, win):
        win.addstr(self.ps1)
        if self.buffer:
            self.pos = 0
            self.cmd = self.buffer.pop(0)
            self.len = len(self.cmd)
            self.reply = self.buffer.pop(0)
        else:
            self.terminated = True
    def process(self, win, c):
        if c == 10:
            if self.terminated:
                raise StopIteration
            if self.pos >= self.len:
                win.addstr("\n%s\n" % self.reply)
                self(win)
                return
        if self.pos < self.len:
            win.addstr(self.cmd[self.pos])
            self.pos += 1

class pyshell(shell):
    ps1 = ">>> "

class python(Context):
    pass

def main(source):
    execfile(source)
    stdin = sys.stdin.fileno()
    try:
        win = curses.initscr()
        curses.noecho()
        for context in CONTEXTS:
            if 1: # transition effect
                y, x = win.getmaxyx()
                for i in xrange(x):
                    for j in xrange(y):
                        if i != x-1 or j != y-1:
                            win.addch(j, i, 42)
                    win.refresh()
                    curses.delay_output(5)
            curses.delay_output(200)
            win.clear()
            context(win)
            while 1:
                c = win.getch()
                try:
                    context.process(win, c)
                except Exception:
                    break
        while 1:
            break
            c = win.getch()
            if c in (10, 27): # return or escape
                break
#            else:
#                win.addstr(repr(c))
    finally:
        curses.reset_shell_mode()

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
