#!/usr/bin/env python3
# Copyright 2014-2017 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Abstract base classes of all vector field subclasses.
'''

# ....................{ IMPORTS                            }....................
import numpy as np
from abc import ABCMeta, abstractproperty
from betse.exceptions import BetseSimConfigException
from betse.lib.numpy import arrays
from betse.science.vector.vectors import VectorCells
from betse.util.py import references
from betse.util.type.callables import property_cached
from betse.util.type.types import type_check, NumericTypes, SequenceTypes
from numpy import ndarray

# ....................{ CLASSES                            }....................
class VectorFieldABC(object, metaclass=ABCMeta):
    '''
    Abstract base class of all vector field subclasses.

    Each subclass of this class provides properties efficiently yielding all
    X and Y components and magnitudes of the vector field of a single modelled
    variable (e.g., current density) for one or more simulation time steps.

    Attributes
    ----------
    _magnitude_factor : NumericTypes
        Factor by which to multiply each magnitude of each vector in this vector
        field, typically to scale vector magnitude to the desired units.
    '''

    # ..................{ INITIALIZERS                       }..................
    @type_check
    def __init__(self, magnitude_factor: NumericTypes = 1) -> None:
        '''
        Initialize this vector field.

        Parameters
        ----------
        magnitude_factor : optional[NumericTypes]
            Factor by which to multiply each magnitude of each vector in this
            vector field, typically to scale magnitude to the desired units.
            Defaults to 1, implying no scaling.
        '''

        # Classify the passed parameters.
        self._magnitude_factor = magnitude_factor

    # ..................{ PROPERTIES ~ abstract              }..................
    @abstractproperty
    def x(self) -> ndarray:
        '''
        Two-dimensional Numpy array whose:

        * First dimension indexes one or more time steps of this simulation.
        * Second dimension indexes each X component of each vector in this
          vector field for this time step.
        '''

        pass


    @abstractproperty
    def y(self) -> ndarray:
        '''
        Two-dimensional Numpy array whose:

        * First dimension indexes one or more time steps of this simulation.
        * Second dimension indexes each Y component of each vector in this
          vector field for this time step.
        '''

        pass

    # ..................{ PROPERTIES                         }..................
    @property_cached
    def magnitudes(self) -> ndarray:
        '''
        Two-dimensional Numpy array whose:

        * First dimension indexes one or more time steps of this simulation.
        * Second dimension indexes each magnitude of each vector in this vector
          field for this time step. For safety, this magnitude is guaranteed to
          be non-zero, avoiding division-by-zero errors elsewhere in the
          codebase when these magnitudes are subsequently divided by (e.g., to
          normalize the X or Y vector components).

        For space and time efficiency, the definition of this array is lazily
        deferred to the first read of this property.
        '''

        # Array of all vector magnitudes computed from the arrays of all
        # vector X and Y components such that each such magnitude is:
        #
        # * Incremented by a negligible positive value approximately equal
        #   to 0, avoiding inevitable division-by-zero errors elsewhere in
        #   the codebase when these magnitudes are subsequently divided by
        #   (e.g., to normalize the X or Y components).
        # * Multiplied by the previously passed factor, typically to scale
        #   magnitudes to the desired units.
        return (
            1e-15 + self._magnitude_factor*np.sqrt(self.x**2 + self.y**2))

    # ..................{ PROPERTIES ~ unit                  }..................
    @property_cached
    def unit_x(self) -> ndarray:
        '''
        Two-dimensional Numpy array whose:

        * First dimension indexes one or more time steps of this simulation.
        * Second dimension indexes each unitary X component of each unit vector
          in this vector field for this time step, produced by dividing that
          vector's original X component by that vector's original magnitude.

        For space and time efficiency, the definition of this array is lazily
        deferred to the first read of this property.
        '''

        return self.x / self.magnitudes


    @property_cached
    def unit_y(self) -> ndarray:
        '''
        Two-dimensional Numpy array whose:

        * First dimension indexes one or more time steps of this simulation.
        * Second dimension indexes each unitary Y component of each unit vector
          in this vector field for this time step, produced by dividing that
          vector's original Y component by that vector's original magnitude.

        For space and time efficiency, the definition of this array is lazily
        deferred to the first read of this property.
        '''

        return self.y / self.magnitudes

# ....................{ SUPERCLASSES ~ simulated           }....................
#FIXME: Obsolete. Remove after replacing the
#"VectorFieldCurrentIntra" and "VectorFieldCurrentIntraExtra" subclasses with
#simple instantiation of the new "VectorFieldCells" class.
class VectorFieldSimmedABC(VectorFieldABC):
    '''
    Abstract base class of all **simulated vector field subclasses** (i.e.,
    vector fields simulated by the current simulation, typically as attributes
    of the current :class:`Simulator` singleton).

    Attributes
    ----------
    _cells : Cells
        Current cell cluster.
    _p : Parameters
        Current simulation configuration.
    _sim : Simulator
        Current simulation.
    '''

    # ..................{ INITIALIZERS                       }..................
    @type_check
    def __init__(
        self,

        # Mandatory parameters.
        sim:   'betse.science.sim.Simulator',
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',

        # Optional parameters.
        is_ecm_needed: bool = False,

        # Superclass parameters.
        *args, **kwargs
    ) -> None:
        '''
        Initialize this simulated vector field.

        Parameters
        ----------
        sim : Simulator
            Current simulation.
        cells : Cells
            Current cell cluster.
        p : Parameters
            Current simulation configuration.
        is_ecm_needed : optional[bool]
            `True` only if this vector field requires extracellular spaces. If
            `True` and the passed configuration disables simulation of such
            spaces, an exception is raised. Defaults to `False`.

        All remaining parameters are passed as is to the superclass.

        Raises
        ----------
        BetseSimConfigException
            If `is_ecm_needed` is `True` _and_ this configuration disables
            simulation of extracellular spaces.
        '''

        # Initialize our superclass with all remaining parameters.
        super().__init__(*args, **kwargs)

        # If the subclass requires extracellular spaces but simulation of such
        # spaces is currently disabled, raise an exception.
        if is_ecm_needed and not p.sim_ECM:
            raise BetseSimConfigException('Extracellular spaces disabled.')

        # Classify core parameters with weak rather than strong (the default)
        # references, thus avoiding circular references and the resulting
        # complications thereof (e.g., increased memory overhead). Since these
        # objects necessarily live significantly longer than this plot, no
        # complications arise. Ergo, these attributes *ALWAYS* yield these
        # objects rather than non-deterministically yielding "None" if these
        # objects are unexpectedly garbage-collected.
        self._sim = references.proxy_weak(sim)
        self._cells = references.proxy_weak(cells)
        self._p = references.proxy_weak(p)

# ....................{ SUBCLASSES                         }....................
#FIXME: Merge this subclass entirely into the "VectorFieldABC" superclass
#*AFTER* eliminating the "VectorFieldSimmedABC" subclass. On doing so, the the
#"VectorFieldABC" superclass should be renamed to simply "VectorField" and cease
#having an "ABC" metaclass.
class VectorFieldArrayed(VectorFieldABC):
    '''
    Vector field whose X and Y components are two-dimensional sequences
    redefined at initialization time.
    '''

    # ..................{ INITIALIZERS                       }..................
    @type_check
    def __init__(
        self, x: SequenceTypes, y: SequenceTypes, *args, **kwargs) -> None:
        '''
        Initialize this vector field.

        Parameters
        ----------
        x : ndarray
            Two-dimensional sequence whose:
            * First dimension indexes one or more time steps of this simulation.
            * Second dimension indexes each X component of each vector in this
              vector field for this time step.
        y : ndarray
            Two-dimensional sequence whose:
            * First dimension indexes one or more time steps of this simulation.
            * Second dimension indexes each Y component of each vector in this
              vector field for this time step.

        All remaining parameters are passed as is to the superclass.
        '''

        # Initialize our superclass with all remaining parameters.
        super().__init__(*args, **kwargs)

        # Classify the passed sequences as Numpy arrays for efficiency.
        self._x = arrays.from_sequence(x)
        self._y = arrays.from_sequence(y)

    # ..................{ SUPERCLASS                         }..................
    @property
    def x(self) -> ndarray:
        return self._x

    @property
    def y(self) -> ndarray:
        return self._y

# ....................{ CLASSES ~ cells                    }....................
class VectorFieldCells(object):
    '''
    Cache of various related vector fields whose X and Y components are
    two-dimensional Numpy arrays describing the same underlying data spatially
    situated along different coordinate systems (e.g., cell centres, cell
    membrane vertices) for one or more simulation time steps.

    The input data encapsulated by this cache may be spatially situated at
    either:

    * The centre of each cell in the simulated cluster.
    * The vertex of each cell membrane in the simulated cluster.
    * The midpoint of each cell membrane in the simulated cluster.
    * The centre of each square grid space (in either dimension).

    Each property provided by this vector field (e.g.,
    :meth:`times_cell_centres`) then efficiently interpolates this input data
    from its original coordinate system into the corresponding output data in
    another coordinate system.

    Attributes
    ----------
    _x : VectorCells
        Two-dimensional array of the X components of all vectors in this field
        for one or more simulation time steps.
    _y : VectorCells
        Two-dimensional array of the Y components of all vectors in this field
        for one or more simulation time steps.
    '''

    # ..................{ INITIALIZERS                       }..................
    @type_check
    def __init__(self, x: VectorCells, y: VectorCells) -> None:
        '''
        Initialize this vector field cache.

        Parameters
        ----------
        x : VectorCells
            Two-dimensional array of the X components of all vectors in this
            field for one or more simulation time steps.
        y : VectorCells
            Two-dimensional array of the Y components of all vectors in this
            field for one or more simulation time steps.
        '''

        # Classify all passed parameters.
        self._x = x
        self._y = y

    # ..................{ PROPERTIES                         }..................
    # Read-only properties, preventing callers from setting these attributes.

    @property_cached
    def times_cells_centre(self) -> VectorFieldArrayed:
        '''
        Vector field whose X and Y components are two-dimensional Numpy arrays
        of data spatially situated at cell centres for one or more time steps.

        See Also
        ----------
        :meth:`VectorCells.times_cells_centre`
            Details on the structure of these arrays.
        '''

        return VectorFieldArrayed(
            x=self._x.times_cells_centre,
            y=self._y.times_cells_centre)


    @property_cached
    def times_grids_centre(self) -> VectorFieldArrayed:
        '''
        Vector field whose X and Y components are two-dimensional Numpy arrays
        of data spatially situated at grid space centres for one or more
        time steps.

        See Also
        ----------
        :meth:`VectorCells.times_grids_centre`
            Details on the structure of these arrays.
        '''

        return VectorFieldArrayed(
            x=self._x.times_grids_centre,
            y=self._y.times_grids_centre)


    @property_cached
    def times_membranes_midpoint(self) -> VectorFieldArrayed:
        '''
        Vector field whose X and Y components are two-dimensional Numpy arrays
        of data spatially situated at cell membrane midpoints for one or more
        time steps.

        See Also
        ----------
        :meth:`VectorCells.times_membranes_midpoint`
            Details on the structure of these arrays.
        '''

        return VectorFieldArrayed(
            x=self._x.times_membranes_midpoint,
            y=self._y.times_membranes_midpoint)


    @property_cached
    def times_membranes_vertex(self) -> VectorFieldArrayed:
        '''
        Vector field whose X and Y components are two-dimensional Numpy arrays
        of data spatially situated at cell membrane vertices for one or more
        time steps.

        See Also
        ----------
        :meth:`VectorCells.times_membranes_vertex`
            Details on the structure of these arrays.
        '''

        return VectorFieldArrayed(
            x=self._x.times_membranes_vertex,
            y=self._y.times_membranes_vertex)
