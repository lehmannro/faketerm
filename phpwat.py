class phpshell(shell):
    ps1 = "php> "
    ps2 = "php> "

with phpshell():
    print "0x0+4"
    print "8"
    print "0x0 +4"
    print "8"
    print "0x0+ 4  # because PHP developers know how to do a parser"
    print "4"
    print "# oh well, corrected in PHP 5.4, but guess what\n0b0+1"
    print "2"
    print "# and now guess what this gem does\n0x0+2 . 0x0 + 2"
    print "42"
    print "# https://bugs.php.net/bug.php?id=61095"
