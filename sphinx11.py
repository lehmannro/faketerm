with bullets("Let's play Jeopardy:   IT for 100...") as ctx:
    ctx.transition = None
    print "a software package"
    print "released 2007"
    print "21,000 lines of code"
    print "written in Python"
    print "by the Pocoo team"
    print "you all love it"
    print "you ALL LOVE it"

with chapter() as ctx:
    ctx.transition = '*'
    print "Sphinx 1.1 Release"
    print ""
    print ""
    print "by The Sphinx Team"

with bullets("Exciting New Features") as ctx:
    ctx.transition = '*'
    print "Python 3000 support via 2to3"
    print "gettext-style Internationalization"
    print "Texinfo builder"
    print "MathJax extension"
    print "localized full-text search"
    print "sphinx-apidoc"
    print "Web Support library"
    print "6 new translations"
    print "... lots and lots of small enhancements ..."
'''
with shell():
    print "make gettext"
    print """python ../sphinx-build.py -b gettext    . _build/locale
Running Sphinx v1.1
loading pickled environment... done
building [gettext]: targets for 46 source files that are out of date
updating environment: 0 added, 0 changed, 0 removed
looking for now-outdated files... none found
preparing documents... done

writing message catalogs... [ 12%] glossary
writing message catalogs... [ 25%] config
writing message catalogs... [ 37%] markup
writing message catalogs... [ 50%] faq
writing message catalogs... [ 62%] tutorial
writing message catalogs... [ 75%] intro
writing message catalogs... [ 87%] builders
writing message catalogs... [100%] man

Build finished. The message catalogs are in _build/locale."""
with shell() as ctx:
    ctx.transition = 0
    print "cd _build/locale"
    print ""
    print "ls"
    print """builders.pot     faq.pot       glossary.pot    man.pot
config.pot       markup.pot    tutorial.pot    intro.pot"""
    print "tail -5 tutorial.pot"
    print """#: ../../tutorial.rst:256
# 0c93871bb03b4ec3b020a19174f057f1
msgid "This is the usual lay-out.  However, :file:`conf.py` can also live in another directory, the :term:`configuration directory`.  See :ref:`invocation`."
msgstr \"\""""
    print "make O=\"-D language=de\" html"
    print """Running Sphinx v1.1
loading translations [de]... done
reading sources...
writing output...

Build finished. The HTML pages are in _build/html."""
    print "python"

with pyshell() as ctx:
    ctx.transition = 0
    print "from sphinx.websupport import WebSupport"
    print ""
    print "support = WebSupport(srcdir='sphinx/doc')"
    print ""
    print "support.get_document('tutorial')"
    print """{'title':  u'First Steps with Sphinx',
 'body': u'<h1>First Steps...',
 'script': u'<script type="text/javascript">...',
 'sidebar': '<div class="sphinxsidebar">...',
 'css': ...,
 'relbar': ...}"""
    print ""
'''

with chapter() as ctx:
    ctx.transition = 2
    print "Sphinx 1.1"
    print ""
    print "coming to a Cheeseshop near you"
    print "on Sunday"
    print ""
    print ""
    print ":-)"
    print ""
    print ""
    print "-- Robert Lehmann"
