"""CLI functions."""
import locale
import os
import platform
import struct
import sys

import pkg_resources

import rayml
from rayml.utils import get_logger


def print_info():
    """Prints information about the system, rayml, and dependencies of rayml."""
    logger = get_logger(__name__)
    logger.info("rayml version: %s" % rayml.__version__)
    logger.info("rayml installation directory: %s" % get_rayml_root())
    print_sys_info()
    print_deps()


def print_sys_info():
    """Prints system information."""
    logger = get_logger(__name__)
    logger.info("\nSYSTEM INFO")
    logger.info("-----------")
    sys_info = get_sys_info()
    for title, stat in sys_info:
        logger.info("{title}: {stat}".format(title=title, stat=stat))


def print_deps():
    """Prints the version number of each dependency."""
    logger = get_logger(__name__)
    logger.info("\nINSTALLED VERSIONS")
    logger.info("------------------")
    installed_packages = get_installed_packages()

    for package, version in installed_packages.items():
        logger.info("{package}: {version}".format(package=package, version=version))


# Modified from here
# https://github.com/pandas-dev/pandas/blob/d9a037ec4ad0aab0f5bf2ad18a30554c38299e57/pandas/util/_print_versions.py#L11
def get_sys_info():
    """Returns system information.

    Returns:
        List of tuples about system stats.
    """
    blob = []
    try:
        (sysname, nodename, release, version, machine, processor) = platform.uname()
        blob.extend(
            [
                ("python", ".".join(map(str, sys.version_info))),
                ("python-bits", struct.calcsize("P") * 8),
                ("OS", "{sysname}".format(sysname=sysname)),
                ("OS-release", "{release}".format(release=release)),
                ("machine", "{machine}".format(machine=machine)),
                ("processor", "{processor}".format(processor=processor)),
                ("byteorder", "{byteorder}".format(byteorder=sys.byteorder)),
                ("LC_ALL", "{lc}".format(lc=os.environ.get("LC_ALL", "None"))),
                ("LANG", "{lang}".format(lang=os.environ.get("LANG", "None"))),
                ("LOCALE", ".".join(map(str, locale.getlocale()))),
            ]
        )
    except (KeyError, ValueError):
        pass

    return blob


def get_installed_packages():
    """Get dictionary mapping installed package names to their versions.

    Returns:
        Dictionary mapping installed package names to their versions.
    """
    installed_packages = {}
    for d in pkg_resources.working_set:
        installed_packages[d.project_name.lower()] = d.version
    return installed_packages


def get_rayml_root():
    """Gets location where rayml is installed.

    Returns:
        Location where rayml is installed.
    """
    return os.path.dirname(rayml.__file__)