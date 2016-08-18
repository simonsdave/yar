# Execute the command line
#
#   python setup.py sdist --formats=gztar
#
# from the same directory as setup.py which will generate
# the file yar/yar-V.N.tar.gz where V.N is the version number
# used as the version argument to setup() below.
#
# To install the archieve just run pip using something like
#
#   pip install yar-V.N.tar.gz
#
# Note - if you're running pip install inside a Docker container
# then it probably means you got the archive into the container
# using a Dockerfile's ADD command. The ADD command decompresses
# the archive and extracts all files. This is fine. Just run the
# pip command on the directory to which the files are extracted.
# Probably something like this for yar:
#
#   pip install yar-1.0
#
# :TODO: add commentry about which version of setuptools should
# be used.

from setuptools import setup

setup(
    name="yar",
    packages=[
        "yar",
        "yar.util",
        "yar.app_service",
        "yar.auth_service",
        "yar.auth_service.basic",
        "yar.auth_service.mac",
        "yar.key_service",
        "yar.key_store",
        # see "data_files" comment on why the next shouldn't be here
        "yar.key_store.design_docs",
    ],
    scripts=[
        "bin/app_service",
        "bin/auth_service",
        "bin/key_service",
        "bin/key_store_installer",
        "bin/yarcurl",
        "bin/bulk_gen_creds",
    ],
    install_requires=[
        "httplib2==0.9.2",
        "jsonschema==2.5.1",
        "python-keyczar==0.716",
        "requests==2.11.1",
        "tornado==4.4.1",
        "tornado-memcache==0.1",
    ],
    dependency_links=[
        # wow was it tricky (for me) trying to figure out how to get
        # tornado-memcache to install corectly. there are lots of postings
        # talking about the basic url structure req'd but only the article
        # below seemed to highlight the need for the version number on
        # the end of the url.
        #
        #   http://lfhck.com/question/298293/can-pip-install-dependencies-not-specified-in-setuppy-at-install-time
        #
        # :TRICKY: the version number @ the end of the URL below matches
        # the version number in "install_requires" section of this setup.py
        # and the version number listed in tornado-memcache's setup.py.
        # all 3 of these version numbers had to match to get this all to
        # work correctly.
        "https://github.com/dpnova/tornado-memcache/tarball/master#egg=tornado-memcache-0.1",
    ],
    # MANIFEST.in in same directory as this setup.py should contain
    # the following:
    #
    #   include yar/key_store/design_docs/by_principal.json
    #   include yar/key_store/design_docs/by_identifier.json
    #
    # Also, the lines below shouldn't be commented out in this setup.py
    #
    #   data_files = [
    #       ("", ["yar/key_store/by_identifier.json"]),
    #       ("", ["yar/key_store/by_principal.json"]),
    #   ],
    #
    # And finally, yar.key_store.design_docs shouldn't be in packages.
    #
    # Wow, that's A LOT of stuff that should be done differently. What's up?
    # It's all about how setuptools or distutils (boy I struggle to understand
    # the Python packaging world!) handles (or really doesn't handle) packaging
    # and install of non-Python files. Design documents for the key store are
    # json documents and it was these files that I wanted to package up.
    # So what exactly was the problem?  As long as MANIFEST.in was around
    # and referenced the design documents (see above) running sdist:
    #
    #   python setup.py sdist
    #
    # did indeed package the design documents in the sdist generated egg
    # (yar/dist/yar-*.*.tar.gz). Yes this part worked! The problem came when
    # pip installing the egg:
    #
    #   pip install ./yar-*.*.tar.gz
    #
    # as per the docs @ http://pythonhosted.org//setuptools/setuptools.html#including-data-files
    # creds.json was put in sys.prefix by pip but what we wanted and expected
    # was for it to be put in the same directory as the yar.key_store package.
    #
    # After many hours of frustrating reading I came to the conclusion
    # that everyone would like things to work as I have described but it doesn't
    # and folks are just hacking around the problem. Thought I was off down a
    # promising path by using site.getsitepackages() to construct an install
    # path that would be used with the data_files statement. Something like:
    #
    #   site.getsitepackages()
    #
    # So what was the problem the the site approach? Works fine on Ubuntu but
    # site.getsitepackages() isn't available on Mac OS X (with the default 2.7
    # Python version).
    #
    # Some facts ... on Ubuntu 12.04:
    #
    #   yar installs to /usr/local/lib/python2.7/dist-packages/yar/__init__.pyc
    #   sys.prefix is /usr
    #   site.getsitepackages() returns:
    #       ['/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages']
    #
    # on Mac OS X Maverics:
    #
    #   sys.prefix is /System/Library/Frameworks/Python.framework/Versions/2.7
    #
    # The sol'n path I choose was to rename the .json files as .py files even
    # though they aren't actually .py files but just use them like .json files.
    #
    # Open questions
    # -- do the latest (2.1) setuptools need to be used?
    #    -- http://pythonhosted.org//setuptools/index.html
    #    -- https://pypi.python.org/pypi/setuptools#unix-based-systems-including-mac-os-x
    #
    # Helpful References
    # -- http://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distribute
    # -- http://stackoverflow.com/questions/2968701/2-techniques-for-including-files-in-a-python-distribution-which-is-better/2969087#2969087
    # -- http://stackoverflow.com/questions/12191339/add-data-files-to-python-projects-setup-py
    # -- http://stackoverflow.com/questions/11235820/setup-py-not-installing-data-files
    version=1.0,
    description="yar",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/yar"
)
