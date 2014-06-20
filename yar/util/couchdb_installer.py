"""This module contains a collection of utility logic that implements
a CouchDB database installer. To use this module create design documents
as JSON files (just like CouchDB would expect) but instead of giving
the files .json extensions give them .py extensions are group them
all in a single module. For a full description of why the files are
py files see yar's setup.py - enjoy! Once the design docs have been
created create a mainline for the installer like the example below:

    #!/usr/bin/env python

    import logging

    from yar.key_store import design_docs
    from yar.util import couchdb_installer

    _logger = logging.getLogger("KEYSTORE_INSTALLER.%s" % __name__)

    class CommandLineParser(couchdb_installer.CommandLineParser):

        def __init__(self):
            description = (
                "The Key Store Installer is a utility used to create "
                "and/or delete the CouchDB database that implements "
                "yar's Key Store."
            )
            couchdb_installer.CommandLineParser.__init__(self, description)

    if __name__ == "__main__":
        couchdb_installer.main(CommandLineParser(), design_docs)

And that's all there is too it! Sweet:-)"""

import logging
import os
import sys
import glob
import httplib
import httplib2
import optparse

from yar.util import clparserutil

_logger = logging.getLogger("UTIL.%s" % __name__)


def _is_couchdb_accessible(host):
    """Returns True if there's a CouchDB server running on ```host```.
    Otherwise returns False. ```host``` is expected to be of the form
    host:port."""

    url = "http://%s" % host
    http_client = httplib2.Http()
    try:
        response, content = http_client.request(url, "GET")
    except:
        return False
    return httplib.OK == response.status


def _create_database(database, host):
    _logger.info("Creating database '%s' on '%s'", database, host)

    url = "http://%s/%s" % (host, database)
    http_client = httplib2.Http()
    response, content = http_client.request(url, "PUT")
    if httplib.CREATED != response.status:
        _logger.error("Failed to create database '%s' on '%s'", database, host)
        return False
    _logger.info("Successfully created database '%s' on '%s'", database, host)

    return True


def _create_design_docs(database, host, design_docs_module):
    #
    # now iterate thru each file in the same directory as this script
    # for files that end with ".json" - these files are assumed to be
    # design documents with the filename (less ".json" being the design
    # document name
    #
    _logger.info(
        "Creating design documents in database '%s' on '%s'",
        database,
        host)

    path = os.path.split(design_docs_module.__file__)[0]
    design_doc_filename_pattern = os.path.join(path, "*.py")
    for design_doc_filename in glob.glob(design_doc_filename_pattern):

        if design_doc_filename.endswith("__init__.py"):
            continue

        design_doc_name = os.path.basename(design_doc_filename)[:-len(".py")]

        _logger.info(
            "Creating design doc '%s' in database '%s' on '%s' from file '%s'",
            design_doc_name,
            database,
            host,
            design_doc_filename)

        with open(design_doc_filename, "r") as design_doc_file:
            design_doc = design_doc_file.read()

        url = "http://%s/%s/_design/%s" % (host, database, design_doc_name)
        http_client = httplib2.Http()
        response, content = http_client.request(
            url,
            "PUT",
            body=design_doc,
            headers={"Content-Type": "application/json; charset=utf8"})
        if httplib.CREATED != response.status:
            _logger.error("Failed to create design doc '%s'", url)
            return False
        _logger.info("Successfully created design doc '%s'", url)

    return True


def _delete_database(database, host):
    _logger.info("Deleting database '%s' on '%s'", database, host)

    http_client = httplib2.Http()

    url = "http://%s/%s" % (host, database)
    response, content = http_client.request(url, "GET")
    if httplib.NOT_FOUND == response.status:
        fmt = (
            "No need to delete database '%s' on '%s' "
            "since database doesn't exist"
        )
        _logger.error(fmt, database, host)
        return True

    url = "http://%s/%s" % (host, database)
    response, content = http_client.request(url, "DELETE")
    if httplib.OK != response.status:
        _logger.error("Failed to delete database '%s' on '%s'", database, host)
        return False

    _logger.info("Successfully deleted database '%s' on '%s'", database, host)
    return True


class CommandLineParser(optparse.OptionParser):
    """```CommandLineParser``` is an abstract base class used to
    parse command line arguments for a CouchDB installer.
    See this module's complete example for how to use this class."""

    def __init__(self, description):

        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            description=description,
            option_class=clparserutil.Option)

        default = logging.ERROR
        fmt = (
            "logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - "
            "default = %s"
        )
        help = fmt % logging.getLevelName(default)
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=default,
            type="logginglevel",
            help=help)

        default = "127.0.0.1:5984"
        help = "where's CouchDB running - default = %s" % default
        self.add_option(
            "--host",
            action="store",
            dest="host",
            default=default,
            type="hostcolonport",
            help=help)

        default = "creds"
        help = "database - default = %s" % default
        self.add_option(
            "--database",
            action="store",
            dest="database",
            default=default,
            type="string",
            help=help)

        default = False
        help = "delete before creating key store - default = %s" % default
        self.add_option(
            "--delete",
            action="store",
            dest="delete",
            default=default,
            type="boolean",
            help=help)

        default = True,
        help = "create key store - default = %s" % default
        self.add_option(
            "--create",
            action="store",
            dest="create",
            default=default,
            type="boolean",
            help=help)

        default = True,
        help = "create design docs - default = %s" % default
        self.add_option(
            "--createdesign",
            action="store",
            dest="create_design_docs",
            default=default,
            type="boolean",
            help=help)


def main(clp, design_docs_module):
    """```main``` is used to implement the core main line logic
    for a CouchDB installer. See this module's complete example
    for how to use this class."""

    (clo, cla) = clp.parse_args()

    logging.basicConfig(level=clo.logging_level)

    if not _is_couchdb_accessible(clo.host):
        _logger.fatal("CouchDB isn't running on '%s'", clo.host)
        sys.exit(1)

    if clo.delete:
        if not _delete_database(clo.database, clo.host):
            sys.exit(1)

    if clo.create:
        if not _create_database(clo.database, clo.host):
            sys.exit(1)

    if clo.create_design_docs:
        if not _create_design_docs(clo.database, clo.host, design_docs_module):
            sys.exit(1)

    sys.exit(0)
