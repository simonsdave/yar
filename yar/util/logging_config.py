"""yar servers were typically configuring the logging infrastructure
in exactly the same way. To avoid duplicated code this logic has been
centralized in the configure() function of this module."""

import logging
import time

def configure(level, filename, syslog):
    """This function is expected to be called from the server's
    mainline with level, filename and syslog probably coming from
    the server's command line parser."""

    logging.Formatter.converter = time.gmtime
    format = (
        "%(relativeCreated)d\t%(asctime)s\t%(levelname)s\t"
        "%(module)s.%(funcName)s:%(lineno)d\t%(message)s"
    )
    logging.basicConfig(
        level=level,
        format=format,
        filename=filename)

    if syslog:
        handler = logging.handlers.SysLogHandler(address=syslog)
        logging.getLogger().addHandler(handler)
