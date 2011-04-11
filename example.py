"""
An Example Presentation

about Faketerm
"""

__author__ = "John Doe"

with bullets("Example slide"):
    print "first bullet point"
    print "second bullet point"
    print "third bullet point"
with shell() as ctx:
    ctx.transition = '%'
    print "echo 123"
    print "123"
    print "echo 123"
    print "WOO, SURPRISE! :-)"
    print "python"
with pyshell() as ctx:
    ctx.transition = None
    print "1 + 1"
    print "2"
    print "def foo():\n  pass"
    print ""
    print "1 / 0"
    ctx.throw(ZeroDivisionError("integer division or modulo by zero"))
with chapter() as ctx:
    ctx.transition = 3
    print "Thanks for listening.."
    print "QUESTIONS?"
