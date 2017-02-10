#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2017 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
BETSE-specific exception hierarchy.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta

# ....................{ EXCEPTIONS                         }....................
#FIXME: Define an __init__() method asserting that the passed exception message
#is non-None, which Python permits by default but which is functionally useless.
class BetseException(Exception, metaclass=ABCMeta):
    '''
    Abstract base class of all BETSE-specific exceptions.
    '''
    pass


class BetseLogException(BetseException):
    '''
    Low-level logging-specific exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ os                    }....................
class BetseOSException(BetseException):
    '''
    General-purpose Low-level operating system (OS) exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ python                }....................
class BetsePyException(BetseException):
    '''
    General-purpose low-level Python interpreter exception.

    This exception is appropriate for use in relation to low-level issues
    concerning the active Python interpreter (e.g., inability to retrieve this
    interpreter's absolute path).
    '''
    pass


class BetsePyFrozenException(BetsePyException):
    '''
    Low-level exception pertaining to **frozen executables** (i.e., Python
    codebases converted into platform-specific executables).
    '''
    pass

# ....................{ EXCEPTIONS ~ arg                  }....................
#FIXME: Raise this exception throughout the "betse.cli" subpackage.
class BetseCLIArgException(BetseException):
    '''
    Command-line argument-specific exception.
    '''
    pass


class BetseCLIArgParserException(SystemExit):
    '''
    :class:`betse.script.argparse.ArgumentParser`-specific exception connoting
    the :meth:`betse.script.argparse.parse_args` method to have unsuccessfully
    parsed the argument list passed to the current command-line application.
    '''
    pass

# ....................{ EXCEPTIONS ~ object                }....................
class BetseModuleException(BetseException):
    '''
    Module-specific exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ callable              }....................
class BetseCallableException(BetseException):
    '''
    General-purpose exception applicable to all **callables** (e.g., functions,
    lambdas, methods, properties).
    '''
    pass


class BetseDecoratorException(BetseCallableException):
    '''
    Decorator-specific exception.
    '''
    pass


class BetseFunctionException(BetseCallableException):
    '''
    Function-specific exception.
    '''
    pass


class BetseLambdaException(BetseCallableException):
    '''
    Lambda-specific exception.
    '''
    pass


class BetseMethodException(BetseCallableException):
    '''
    Method-specific exception.
    '''
    pass


class BetseMethodUnimplementedException(
    BetseCallableException, NotImplementedError):
    '''
    Unimplemented method-specific exception.

    This exception is typically raised from **unimplemented optional methods**
    (i.e., non-mandatory methods _not_ intended to be called) of concrete
    subclasses of abstract base classes. While the optimal solution for
    defining **unimplemented mandatory methods** (i.e., non-optional methods
    also _not_ intended to be called) is via the canonical `@abc.abstractmethod`
    decorator, there currently exists no canonical alternative for defining
    optional methods. Hence, this exception.
    '''

    def __init__(self):

        # Avoid circular import dependencies.
        from betse.util.type.call import callers

        # Defer to superclass constructors.
        super().__init__('Method {}() unimplemented.'.format(
            callers.get_caller_basename()))

# ....................{ EXCEPTIONS ~ lib                   }....................
class BetseLibException(BetseException):
    '''
    General-purpose exception applicable to third-party dependencies.
    '''
    pass


class BetseMatplotlibException(BetseLibException):
    '''
    Matplotlib-specific exception.
    '''
    pass


class BetsePyDotException(BetseLibException):
    '''
    PyDot-specific exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ path                  }....................
class BetsePathException(BetseException):
    '''
    Path-specific exception.
    '''
    pass


class BetseDirException(BetsePathException):
    '''
    Directory-specific exception.
    '''
    pass


class BetseFileException(BetsePathException):
    '''
    File-specific exception.
    '''
    pass


class BetseArchiveException(BetsePathException):
    '''
    Archive-specific exception.
    '''
    pass


class BetseCommandException(BetseFileException):
    '''
    Command-specific exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ test                  }....................
class BetseTestException(BetseException):
    '''
    General-purpose exception pertaining to this application's test suite.
    '''
    pass

# ....................{ EXCEPTIONS ~ type                  }....................
class BetseTypeException(BetseException):
    '''
    General-purpose exception applicable to types (i.e., classes).
    '''
    pass


#FIXME: Rename to "BetseMappingException" for generality.
class BetseDictException(BetseTypeException):
    '''
    Dictionary-specific type or value exception.
    '''
    pass


class BetseEnumException(BetseTypeException):
    '''
    Enumeration-specific type or value exception.
    '''
    pass


class BetseNumericException(BetseTypeException):
    '''
    Exception generally applicable to both integer and float types and values.
    '''
    pass


class BetseIntException(BetseTypeException):
    '''
    Integer-specific type or value exception.
    '''
    pass


class BetseIterableException(BetseTypeException):
    '''
    Iterable-specific type or value exception.
    '''
    pass


class BetseSequenceException(BetseTypeException):
    '''
    Sequence-specific type or value exception.
    '''
    pass


class BetseStrException(BetseTypeException):
    '''
    String-specific type or value exception.
    '''
    pass


class BetseRegexException(BetseTypeException):
    '''
    Regular exception-specific type or value exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ science               }....................
class BetseSimException(BetseException):
    '''
    General-purpose simulation exception.
    '''
    pass


class BetseSimConfigException(BetseSimException):
    '''
    Simulation configuration-specific exception.
    '''
    pass


class BetseSimInstabilityException(BetseSimException):
    '''
    Simulation-specific exception indicating the current simulation to have
    unexpectedly failed due to computational instability.
    '''
    pass


#FIXME: For orthogonality, rename to "BetseSimVectorException".
class BetseVectorException(BetseSimException):
    '''
    Vector-specific exception.
    '''
    pass

# ....................{ EXCEPTIONS ~ science : visual      }....................
class BetseSimVisualException(BetseSimException):
    '''
    Simulation visualization-specific exception, applicable to both plots and
    animations.
    '''
    pass


class BetseSimVisualUnsatisfiedException(BetseSimVisualException):
    '''
    Simulation visualization-specific exception, applicable to both plots and
    animations, raised when any feature required by a visualization (e.g.,
    extracellular spaces) is disabled by the parent simulation configuration.
    '''
    pass


#FIXME: For orthogonality, rename to "BetseSimVisualLayerException".
class BetseLayerException(BetseSimVisualException):
    '''
    Simulation visualization layer-specific exception.
    '''
    pass
