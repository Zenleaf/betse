#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2015 by Alexis Pietak & Cecil Curry
# See "LICENSE" for further details.

'''
High-level constants describing `betse`'s program structure.

Such constants provide the absolute paths of files and directories intended for
general use by both the CLI and GUI. For portability, such constants are
initialized in a system-aware manner guaranteed to be sane under various
installation environments -- including PyInstaller-frozen executables and
`setuptools`-installed script wrappers.
'''

# ....................{ IMPORTS                            }....................
from betse import metadata
from betse.util.path import dirs, files, paths
from betse.util.system import oses
from os import environ, path
import pkg_resources, sys

# ....................{ CONSTANTS ~ dir                    }....................
#FIXME: Replace all existing calls to os.path.expanduser() with such constant.

HOME_DIRNAME = None   # initialized below
'''
Absolute path of the current user's home directory.
'''

DATA_DIRNAME = None   # initialized below
'''
Absolute path of `betse`'s data directory.

Such directory contains application-internal resources (e.g., media files)
frozen with the end-user executable binaries generated by PyInstaller.
'''

DOT_DIRNAME = None  # initialized below
'''
Absolute path of `betse`'s dot directory in the current user's home directory.

Such directory contains application-external resources (e.g., configuration
files) created at application runtime and subsequently editable by external
users and utilities.

Locations
----------
This path is operating system-specific as follows:

* Under Linux, this is `~/.betse/`. `betse` does *not* currently comply with the
  _XDG Base Directory Specification (e.g., `~/.local/share/betse`), which the
  principal authors of `betse` largely regard as unhelpful.
* Under OS X, this is `~/Library/Application Support/BETSE`.
* Under Windows, this is
  `C:\Documents and Settings\${User}\Application Data\BETSE`.

.. _XDG Base Directory Specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
'''

# ....................{ CONSTANTS ~ file                   }....................
LOG_DEFAULT_FILENAME = None   # initialized below
'''
Absolute path of the user-specific plaintext file to which `betse` logs
messages by default.
'''

SIMULATION_CONFIG_DEFAULT_FILENAME = None   # initialized below
'''
Absolute path of the application-wide YAML file providing the default tissue
simulation configuration.
'''

# ....................{ INITIALIZATION                     }....................
def init() -> None:
    '''
    Validate core directories and files required at program startup and
    initialize the corresponding module constants (e.g., `DOT_DIRNAME`).

    This function automatically creates non-existent paths where feasible and
    otherwise raises exceptions on such paths *not* being found or *not* having
    correct metadata (e.g., permissions).

    Such paths are required by both the CLI and GUI interfaces for `betse`. To
    support caller-specific exception handling, this function *must* be manually
    called early in program startup.
    '''
    _init_pathnames()
    _test_pathnames()

def _init_pathnames() -> None:
    '''
    Initialize all module constants (e.g., `DOT_DIRNAME`).
    '''
    # Declare such constants to be globals, permitting their modification below.
    global\
        HOME_DIRNAME, DATA_DIRNAME, DOT_DIRNAME,\
        LOG_DEFAULT_FILENAME,\
        SIMULATION_CONFIG_DEFAULT_FILENAME

    # Absolute path of the current user's home directory.
    HOME_DIRNAME = path.expanduser('~')

    # Relative path of the top-level data directory.
    data_root_basename = 'data'

    # Initialize the absolute path of BETSE's data directory.
    #
    # If the current application is a PyInstaller-frozen executable binary, the
    # bootloader for such binary will have added the PyInstaller-specific private
    # attribute "_MEIPASS" to the "sys" module, providing the absolute path of the
    # temporary directory containing all application data resources.
    if hasattr(sys, '_MEIPASS'):
        #FIXME: Is this right? Verify with additional online research.
        DATA_DIRNAME = paths.join(sys._MEIPASS, data_root_basename)
    # If the current application is a setuptools-installed script wrapper, the
    # data directory will have been preserved as is in the setuptools-installed
    # copy of the current Python package tree. In such case, query setuptools to
    # obtain such directory's path in a cross-platform manner. See also:
    #     https://pythonhosted.org/setuptools/pkg_resources.html
    elif pkg_resources.resource_isdir(__name__, data_root_basename):
        DATA_DIRNAME =\
            pkg_resources.resource_filename( __name__, data_root_basename)
    # Else, the current application is either setuptools-symlinked script
    # wrapper *OR* was invoked via the hidden "python3 -m betse.cli.cli"
    # command. In either case, such directory's path is directly obtainable
    # relative to the absolute path of the current module.
    else:
        DATA_DIRNAME = paths.join(
            paths.get_dirname(__file__), data_root_basename)

    # Initialize the absolute path of BETSE's dot directory.
    #
    # If the current system is OS X, set such directory accordingly.
    if oses.is_os_x():
        DOT_DIRNAME = paths.join(
            HOME_DIRNAME,
            'Library', 'Application Support',
            metadata.SCRIPT_NAME_CLI
        )
    # If the current system is Windows, set such directory accordingly.
    elif oses.is_windows():
        DOT_DIRNAME = paths.join(environ['APPDATA'], metadata.NAME)
    #FIXME: Explicitly assert POSIX compatibility here.
    # Else, assume the current system is POSIX-compatible.
    else:
        DOT_DIRNAME = paths.join(HOME_DIRNAME, '.' + metadata.SCRIPT_NAME_CLI)

    # Absolute path of the default user-specific file with which `betse` logs.
    LOG_DEFAULT_FILENAME = paths.join(
        DOT_DIRNAME, metadata.NAME.lower() + '.log')

    # Absolute path of the application-wide YAML file providing the default
    # tissue simulation configuration.
    SIMULATION_CONFIG_DEFAULT_FILENAME = paths.join(
        DATA_DIRNAME, 'yaml', 'sim_config.yaml')

def _test_pathnames() -> None:
    '''
    Validate all module constants (e.g., `DOT_DIRNAME`).
    '''
    # Fail unless requisite paths exist.
    dirs.die_unless_found(DATA_DIRNAME)
    files.die_unless_found(SIMULATION_CONFIG_DEFAULT_FILENAME)

    # Make betse's top-level dot directory if not found.
    dirs.make_unless_found(DOT_DIRNAME)

# --------------------( WASTELANDS                         )--------------------
    #FUXME: Uncomment this after we ascertain the correct path for DATA_DIRNAME,
    #which we should probably get around to!

    #FUXME: This *OBVIOUSLY* isn't right. We appear to have two options,
    #depending on how "betse" was installed:
    #
    #* If via "setup.py install", we should probably use "pkg_resources" to
    #  obtain the data directory.
    #* Else, assume it was via "setup.py symlink", in which case the data
    #  directory can probably be located in one of two ways (in order of
    #  inreasing complexity):
    #  * Use the "__file__" attribute of the current module to obtain the
    #    absolute path of such module. Given that, we can then obtain the
    #    absolute path of the data directory via path munging and the
    #    os.path.abspath(pathname) function, converting relative to absolute
    #    paths. (Double-check that, of course.)
    #  * Manually follow the symlink at
    #    "/usr/lib64/python3.3/site-packages/betse". Yeah. That seems horrid.
    #    Happily, the former approach should work.
#FUXME: The top-level "setup.py" script should be instructed to install the
#top-level "data" directory. Yeah!
#FUXME: Actually use this. More work than we currently care to invest.

# PROGRAM_CONFIG_DEFAULT_FILENAME = None   # initialized below
# '''
# Absolute path of the default user-specific file with which `betse` configures
# application-wide behaviour (e.g., log settings).
# '''
#     # Absolute path of the default user-specific file with which `betse`
#     # configures application-wide behaviour (e.g., log settings).
#     CORE_CONFIG_DEFAULT_FILENAME = paths.join(DOT_DIRNAME, 'core_config.yaml')

    # Defer such imports to avoid circular dependencies.
