#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2016 by Alexis Pietak & Cecil Curry
# See "LICENSE" for further details.

'''
High-level Python facilities.

This module provides functionality pertaining to the active Python interpreter
as a whole.

Caveats
----------
Word size-specific functions (e.g., `is_wordsize_64()`) are generally considered
poor form. Call these functions _only_ where necessary.
'''

# ....................{ IMPORTS                            }....................
import platform, sys
from betse import metadata
from betse.exceptions import BetseInterpreterException
from betse.util.io.log import logs
from betse.util.type.types import type_check, SequenceTypes
from collections import OrderedDict

# ....................{ INITIALIZERS                       }....................
def init() -> None:
    '''
    Validate the active Python interpreter.

    This function does _not_ validate this interpreter's version, as the
    top-level module `betse.metadata` already does so at the beginning of
    application startup. Rather, this function (in order):

    . Logs a non-fatal warning if this interpreter is _not_ 64-bit.
    '''

    # If this Python interpreter is 32- rather than 64-bit, log a non-fatal
    # warning. While technically feasible, running BETSE under 32-bit Python
    # interpreters imposes non-trivial constraints detrimental to sanity.
    if is_wordsize_32():
        logs.log_warning(
            '32-bit Python interpreter detected. '
            '{name} will be confined to low-precision datatypes and '
            'at most 4GB of available RAM, '
            'impeding the reliability and scalability of modelling. '
            'Consider running {name} only under '
            '64-bit Python interpreters.'.format(name=metadata.NAME)
        )

# ....................{ TESTERS                            }....................
def is_testing() -> bool:
    '''
    `True` only if the active Python interpreter is running a test session
    (e.g., with the `py.test` test harness).
    '''

    return metadata._IS_TESTING

# ....................{ TESTERS ~ wordsize                 }....................
def is_wordsize_32() -> bool:
    '''
    `True` only if the active Python interpreter is **32-bit** (i.e., was
    compiled with a 32-bit toolchain into a 32-bit executable).
    '''

    return not is_wordsize_64()


def is_wordsize_64() -> bool:
    '''
    `True` only if the active Python interpreter is **64-bit** (i.e., was
    compiled with a 64-bit toolchain into a 64-bit executable).
    '''

    # Avoid circular import dependencies.
    from betse.util.type import ints

    # Return whether or not the maximum integer size supported by this Python
    # interpreter is larger than the maximum value for variables of internal
    # type `Py_ssize_t` under 32-bit Python interpreters. While somewhat obtuse,
    # this condition is well-recognized by the Python community as the optimal
    # means of portably testing this. Less preferable alternatives include:
    #
    # * "return 'PROCESSOR_ARCHITEW6432' in os.environ", which depends upon
    #   optional environment variables and hence is clearly unreliable.
    # * "return platform.architecture()[0] == '64bit'", which fails under:
    #   * OS X, returning "64bit" even when the active Python interpreter is a
    #     32-bit executable binary embedded in a so-called "universal binary."
    return sys.maxsize > ints.INT_VALUE_MAX_32_BIT

# ....................{ GETTERS                            }....................
def get_wordsize() -> int:
    '''
    Size in bits of variables of internal type `Py_ssize_t` for the active
    Python interpreter.

    This function is guaranteed to return:

    * `64`, if this is a 64-bit interpreter.
    * `32`, if this is a 32-bit interpreter.
    '''

    return 64 if is_wordsize_64() else 32


def get_version() -> str:
    '''
    Human-readable `.`-delimited string specifying the most recent version of
    the Python language supported by the active Python interpreter (e.g.,
    `2.7.10`, `3.4.1`).
    '''

    return platform.python_version()

# ....................{ GETTERS ~ path                     }....................
def get_command_line_prefix() -> list:
    '''
    List of one or more shell words unambiguously running the executable binary
    specific to the active Python interpreter and machine architecture.

    Since the absolute path of the executable binary for the active Python
    interpreter is insufficient to unambiguously run this binary under the
    active machine architecture, this function should _always_ be called in lieu
    of `get_filename()` when attempting to rerun this interpreter as a
    subprocess of the current Python process. As example:

    * Under OS X, the executable binary for this interpreter may be bundled with
      one or more other executable binaries targetting different machine
      architectures (e.g., 32-bit, 64-bit) in a single so-called "universal
      binary." Distinguishing between these bundled binaries requires passing
      this interpreter to a prefixing OS X-specific command, `arch`.
    '''

    # Avoid circular import dependencies.
    from betse.util.os import oses

    # List of such shell words.
    command_line = None

    # If this is OS X, this interpreter is only unambiguously runnable via the
    # OS X-specific "arch" command.
    if oses.is_os_x():
        # Run the "arch" command.
        command_line = ['arch']

        # Instruct this command to run the architecture-specific binary in
        # Python's universal binary corresponding to the current architecture.
        if is_wordsize_64():
            command_line.append('-i386')
        else:
            command_line.append('-x86_64')

        # Instruct this command, lastly, to run this interpreter.
        command_line.append(get_filename())
    # Else, this interpreter is unambiguously runnable as is.
    else:
        command_line = [get_filename()]

    # Return this list.
    return command_line


def get_filename() -> str:
    '''
    Absolute path of the executable binary for the active Python interpreter.
    '''

    # Absolute path of the executable binary for the active Python interpreter
    # if this path is retrievable by Python *OR* either "None" or the empty
    # string otherwise.
    py_filename = sys.executable

    # If this path is retrievable by Python, raise an exception.
    if not py_filename:
        raise BetseInterpreterException(
            'Absolute path of Python interpreter not retrievable.')

    # Return this path.
    return py_filename

# ....................{ GETTERS ~ metadata                 }....................
def get_metadata() -> OrderedDict:
    '''
    Ordered dictionary synopsizing the active Python interpreter.
    '''

    # Avoid circular import dependencies.
    from betse.util.py import freezers

    # This dictionary.
    metadata = OrderedDict((
        ('version', get_version()),
        ('wordsize', get_wordsize()),
        ('is frozen', freezers.is_frozen()),
    ))

    # Return this dictionary.
    return metadata

# ....................{ RUNNERS                            }....................
@type_check
def run(command_args: SequenceTypes, **popen_kwargs) -> None:
    '''
    Rerun the active Python interpreter as a subprocess of the current Python
    process, raising an exception on subprocess failure.

    Parameters
    ----------
    command_args : list
        List of zero or more arguments to be passed to this interpreter.
    popen_kwargs : dict
        Dictionary of keyword arguments to be passed to `subprocess.Popen()`.

    See Also
    ----------
    run()
        Low-level commentary on subprocess execution.
    '''

    # Avoid circular import dependencies.
    from betse.util.path.command import runners

    # List of one or more shell words comprising this command.
    command_words = get_command_line_prefix() + command_args

    # Rerun this interpreter.
    return runners.run(command_words, **popen_kwargs)
