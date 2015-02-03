betse
===========

`betse` (BioElectric Tissue Simulation Engine) simulates propagation of
electrical phenomena within biological tissue (e.g., ion channel-gated current
flow).

## Dependencies

`betse` requires the following non-pure-Python packages – which themselves
require non-Python libraries (e.g., C, Fortran) and hence are best installed
manually via the package manager specific to your current operating system:

* setuptools >= 7.0.
* Matplotlib >= 1.3.0.
* NumPy >= 1.9.0.
* PySide >= 1.1.0.
* PyYaml >= 3.10.
* SciPy >= 0.12.0.

`betse` also requires the following pure-Python packages – which Python-specific
package managers (e.g., `pip`, `setuptools`) will install for you and hence
require no manual installation:

* None, as of this writing.

### Linux Debian

Under Debian-based Linux distributions (e.g., Linux Mint, Ubuntu), such
dependencies are installable in a system-wide manner as follows:

    >>> sudo apt-get install python3-dev python3-matplotlib python3-numpy python3-pyside python3-scipy python3-setuptools python3-yaml

### Apple OS X

`betse` requires at least OS X 10.6 (Snow Leopard). Under such systems, such
dependencies are installable in a system-wide manner as follows:

. Register as an [Apple Developer](https://developer.apple.com). While free,
  such registration requires an existing Apple ID.
. Download [XCode](https://developer.apple.com/xcode). While free, such
  download requires an [Apple Developer] login.
. Install XCode, ensuring the "UNIX Development Support" checkbox is checked.
. Download and install [MacPorts](https://www.macports.org).
. Open a terminal window (e.g., by running the pre-bundled
  `Applications/Utilities`Terminal.app` application).
. Install dependencies:
    >>> sudo port install py34-matplotlib py34-numpy py34-pyside py34-scipy py34-setuptools py34-yaml
. Activate the version of Python required by betse:
    >>> sudo port select --set python python34

Note that MacPorts is a source-based package manager and hence extremely slow.
Expect the installation of dependencies to take several hours to several days.
(We're not kidding.)

## Installation

`betse` is installable into either:

* A system-wide directory accessible to all users of such system.
* A venv (i.e., virtual environment) isolated to the current user.

The latter has the advantage of avoiding conflicts with already installed
system-wide Python and non-Python packages (e.g., in the event that `betse`
requires different versions of such packages), but the corresponding
disadvantage of requiring reinstallation of such packages and all transitive
dependencies of such packages. Since several dependencies are heavy-weight
(e.g., Qt4) and hence costly to reinstall, this is a notable disadvantage.

Note that the string `${BETSE\_DIR}` should be replaced everywhere below by the
absolute path of the directory containing this file.

### System-wide

`betse` is installable into a system-wide directory as follows:

    >>> cd "${BETSE_DIR}"
    >>> python3 setup.py build
    >>> sudo python3 setup.py easy_install --no-deps .

Curiously, although the `develop` command for `setuptools` provides a
`--no-deps` option, the `install` command does not. Hence, the `easy\_install`
command is called above.

### User-specific

`betse` is installable into a user-specific venv by running the following
command **from within such venv**:

    >>> cd "${BETSE_DIR}"
    >>> ./setup.py install

This command should *not* be run outside of a venv. Doing so will reinstall all
dependencies of `betse` already installed by the system-wide package manager
(e.g., `apt-get`). This may superficially appear to work but invites obscure and
difficult to debug conflicts at `betse` runtime between dependencies reinstalled
by `setuptools` and dependencies already installed by such package maneger.

## Usage

`betse` is a front-facing application rather than backend framework. While
`betse`'s Python packages are importable by other packages, `betse` is typically
run by executing Python script wrappers installed to the current `${PATH}`.

### CLI

`betse` installs a low-level command line interface (CLI), runnable as follows:

    >>> betse

Such CLI is also runnable by invoking the main CLI module under the active
Python 3 interpreter as follows:

    >>> cd "${BETSE_DIR}"
    >>> python3 -m betse.cli

This has the minor advantage of working regardless of whether `betse` has been
installed or not, but the corresponding disadvantage of requiring more typing.

### GUI

`betse` also installs a high-level graphical user interface (GUI) implemented in
the popular cross-platform windowing toolkit Qt4, runnable as follows:

    >>> betse-qt &

Such GUI is also runnable by invoking the main GUI module under the active
Python 3 interpreter as follows:

    >>> cd "${BETSE_DIR}"
    >>> python3 -m betse.gui

## Development

For development purposes, `betse` is installable **editably** (i.e., as a
symbolic link rather than physical copy). As the name implies, editable
installations are modifiable at runtime and hence suitable for development.
Thanks to the magic of symbolic links, changes to the copy of `betse` from which
an editable installation was installed will be silently prograpagated back to
such installation.

`betse` is installable editably via both `pip` and `setuptools`. While there
appears to be no particular advantage to using one over the other, it remains
helpful to note that both apply. In either case, external executables (e.g.,
`betse`, `betse-qt`) will also be installed and usable in the expected manner.

### pip

`betse` is installable editably to a system-wide directory via `pip` as follows:

    >>> cd "${BETSE_DIR}"
    >>> sudo pip3 install --editable --no-deps .

### setuptools

`betse` is installable editably to a system-wide directory via `setuptools` as
follows:

    >>> cd "${BETSE_DIR}"
    >>> sudo python3 setup.py develop --no-deps

## Testing

`betse` is testable via `nose` as follows:

    >>> cd "${BETSE_DIR}"
    >>> ./setup.py test

If `nose` is already installed under the active Python 3 interpreter, improved
unit test output is available by either of the following two (effectively)
equivalent commands:

    >>> nosetests             # this works...
    >>> ./setup.py nosetest   # ...as does this.

## License

