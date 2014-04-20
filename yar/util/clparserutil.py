"""This module contains a series of generally useful and reusable
components for use when building extensions to the optparse module
which parses command lines."""

import re
import logging
import optparse

_logger = logging.getLogger("UTIL.%s" % __name__)


def _check_couchdb(option, opt, value):
    """Type checking function for command line parser's 'couchdb' type."""
    reg_ex_pattern = "^[^\s]+\:\d+\/[^\s]+$"
    reg_ex = re.compile(reg_ex_pattern)
    if reg_ex.match(value):
        return value
    msg = "option %s: required format is host:port/database" % opt
    raise optparse.OptionValueError(msg)


def _check_logging_level(option, opt, value):
    """Type checking function for command line parser's 'logginglevel' type."""
    reg_ex_pattern = "^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$"
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    if reg_ex.match(value):
        return getattr(logging, value.upper())
    fmt = (
        "option %s: should be one of "
        "DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL"
    )
    raise optparse.OptionValueError(fmt % opt)


def _check_host_colon_port(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonport' type."""
    return __check_host_colon_port(value, opt, value, False)


def _check_host_colon_port_parsed(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonportparsed' type."""
    return __check_host_colon_port(value, opt, value, True)


def __check_host_colon_port(option, opt, value, return_parsed_value):
    """Encapsulates 98% of the details for implementing the command line
    parser's 'hostcolonport' and 'hostcolonportparsed' types."""
    parsed_value = _parse_host_colon_port(value, must_have_host=True)
    if not parsed_value:
        msg = "option %s: should be host:port format" % opt
        raise optparse.OptionValueError(msg)
    return parsed_value if return_parsed_value else value


def _check_host_colon_ports(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonports' type."""
    return _parse_host_colon_ports(option, opt, value, return_parsed_pairs=False)


def _check_host_colon_ports_parsed(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonportsparsed' type."""
    return _parse_host_colon_ports(option, opt, value, return_parsed_pairs=True)


def _parse_host_colon_ports(option, opt, value, return_parsed_pairs):
    """```value``` is a string whose form is expected to be
    a series of host:port pairs seperated by commas. This function
    parses the string and returns a list of host, port tuples.
    If ```value``` is not in the expected format a
    optparse.OptionValueError exception is raised."""
    split_reg_ex = re.compile("\s*\,\s*")

    rv = []
    for server in split_reg_ex.split(value.strip()):
        parsed_server = _parse_host_colon_port(server, must_have_host=False)
        if not parsed_server:
            fmt = (
                "option %s: should be 'host:port, host:port, ... "
                "host:port' format"
            )
            raise optparse.OptionValueError(fmt % opt)
        rv.append(parsed_server if return_parsed_pairs else server)
    return rv


def _parse_host_colon_port(server, must_have_host):
    """```server``` is expected to be in the form of
    host:port if ```must_have_host``` is True otherwise
    ```server``` can be in host:port format or just be
    a port. This function extracts the host and
    port and returns these components as a string and
    int tuple respectively. If ```server``` is not in
    the expected form None is returned."""

    if must_have_host:
        host_colon_port_reg_ex_pattern = "^\s*(?P<host>[^\:]+)\:(?P<port>\d+)\s*$"
    else:
        host_colon_port_reg_ex_pattern = "^\s*(?:(?P<host>[^\:]+)\:)?(?P<port>\d+)\s*$"
    host_colon_port_reg_ex = re.compile(host_colon_port_reg_ex_pattern)

    match = host_colon_port_reg_ex.match(server)
    if not match:
        return None
    host = match.group("host")
    port = match.group("port")
    return (host, int(port))


def _check_boolean(option, opt, value):
    """Type checking function for command line parser's 'boolean' type."""
    true_reg_ex_pattern = "^(true|t|y|yes|1)$"
    true_reg_ex = re.compile(true_reg_ex_pattern, re.IGNORECASE)
    if true_reg_ex.match(value):
        return True
    false_reg_ex_pattern = "^(false|f|n|no|0)$"
    false_reg_ex = re.compile(false_reg_ex_pattern, re.IGNORECASE)
    if false_reg_ex.match(value):
        return False
    msg = "option %s: should be one of true, false, yes, no, 1 or 0" % opt
    raise optparse.OptionValueError(msg)


def _check_unix_domain_socket(option, opt, value):
    """Type checking function for command line
    parser's 'unixdomaintype' type."""
    reg_ex_pattern = "^(?:/[A-Za-z0-9]+)+$"
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    if reg_ex.match(value):
        return value

    msg = "option %s: should max reg ex patterh '%s'" % (opt, reg_ex_pattern)
    raise optparse.OptionValueError(msg)


class Option(optparse.Option):
    """Adds couchdb, hostcolonport, hostcolonports, boolean & logginglevel
    types to the command line parser's list of available types."""
    new_types = (
        "hostcolonport",
        "hostcolonportparsed",
        "hostcolonports",
        "hostcolonportsparsed",
        "logginglevel",
        "boolean",
        "couchdb",
        "unixdomainsocket",
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["hostcolonport"] = _check_host_colon_port
    TYPE_CHECKER["hostcolonportparsed"] = _check_host_colon_port_parsed
    TYPE_CHECKER["hostcolonports"] = _check_host_colon_ports
    TYPE_CHECKER["hostcolonportsparsed"] = _check_host_colon_ports_parsed
    TYPE_CHECKER["logginglevel"] = _check_logging_level
    TYPE_CHECKER["boolean"] = _check_boolean
    TYPE_CHECKER["couchdb"] = _check_couchdb
    TYPE_CHECKER["unixdomainsocket"] = _check_unix_domain_socket
