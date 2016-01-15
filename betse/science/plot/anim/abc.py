#!/usr/bin/env python3
# Copyright 2014-2016 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Abstract base classes of all Matplotlib-based animation classes.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod  #, abstractstaticmethod
from betse.exceptions import BetseExceptionParameters
from betse.lib.matplotlib.mpl import mpl_config
from betse.lib.matplotlib.anim import FileFrameWriter
from betse.util.io import loggers
from betse.util.path import dirs, paths
from betse.util.type import types
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation

# ....................{ BASE                               }....................
#FIXME: Privatize all public attributes declared below. Raving river madness!
#FIXME: Rename all following parameters and attributes:
#* "clrAutoscale" to "is_colorbar_autoscaled".
#* "clrMin" to "colorbar_min".
#* "clrMax" to "colorbar_max".

class Anim(object, metaclass=ABCMeta):
    '''
    Abstract base class of all animation classes.

    Instances of this class animate the spatial distribution of modelled
    variables (e.g., Vmem) over all time steps of the simulation.

    Attributes
    ----------
    sim : Simulation
        Current simulation.
    cells : Cells
        Current cell cluster.
    p : Parameters
        Current simulation configuration.
    clrAutoscale : bool
        `True` if dynamically resetting the minimum and maximum colorbar values
        to be the corresponding minimum and maximum values for the current
        frame _or_ `False` if statically setting the minimum and maximum
        colorbar values to predetermined constants.
    clrMin : float
        Minimum colorbar value to be used. If `clrAutoscale` is `True`, the
        subclass is responsible for redefining this value as appropriate.
    clrMax : float
        Maximum colorbar value to be used. If `clrAutoscale` is `True`, the
        subclass is responsible for redefining this value as appropriate.
    colormap : Colormap
        Matplotlib colormap with which to create this animation's colorbar.
    fig : Figure
        Matplotlib figure providing the current animation frame.
    ax : FigureAxes
        Matplotlib figure axes providing the current animation frame data.
    _anim : FuncAnimation
        Low-level Matplotlib animation object instantiated by this high-level
        BETSE wrapper object.
    _colorbar_mapping : object
        The Matplotlib mapping (e.g., `Image`, `ContourSet`) to which this
        animation's colorbar applies.
    _is_saving_plotted_frames : bool
        `True` if both saving and displaying animation frames _or_ `False`
        otherwise.
    _save_frame_template : str
        `str.format()`-formatted template which, when formatted with the 0-based
        index of the current frame, yields the absolute path of the image file
        to be saved for that frame.
    _axes_title : str
        Text displayed above the figure axes. If a non-`None` value for the
        `axes_title` parameter is passed to the `animate()` method, this is that
        value; else, this is the value of the `figure_title` parameter passed to
        the same method.
    _axes_x_min : float
        Minimum value of the figure's X axis.
    _axes_x_max : float
        Maximum value of the figure's X axis.
    _axes_y_min : float
        Minimum value of the figure's Y axis.
    _axes_y_max : float
        Maximum value of the figure's Y axis.
    _type : str
        Basename of the subdirectory in the phase-specific results directory
        to which all animation files will be saved _and_ the basename prefix of
        these files.
    _writer_frames : MovieWriter
        Object writing frames from this animation to image files if enabled _or_
        `None` otherwise.
    _writer_video : MovieWriter
        Object encoding this animation to a video file if enabled _or_ `None`
        otherwise.
    '''

    # ..................{ CONCRETE ~ init                    }..................
    def __init__(
        self,

        # Mandatory parameters.
        sim: 'Simulator',
        cells: 'Cells',
        p: 'Parameters',
        type: str,
        clrAutoscale: bool,
        clrMin: float,
        clrMax: float,

        # Optional parameters.
        colormap: 'Colormap' = None,
    ) -> None:
        '''
        Initialize this animation.

        Parameters
        ----------
        sim : Simulator
            Current simulation.
        cells : Cells
            Current cell cluster.
        p : Parameters
            Current simulation configuration.
        type : str
            Basename of the subdirectory in the phase-specific results directory
            to which all animation files will be saved _and_ the basename prefix
            of these files.
        title_colorbar: str
            Text displayed above the figure colorbar.
        clrAutoscale : bool
            `True` if dynamically resetting the minimum and maximum colorbar
            values to be the corresponding minimum and maximum values for the
            current frame _or_ `False` if statically setting the minimum and
            maximum colorbar values to predetermined constants.
        clrMin : float
            Minimum colorbar value to be used if `clrAutoscale` is `False`.
        clrMax : float
            Maximum colorbar value to be used if `clrAutoscale` is `False`.
        colormap : Colormap
            Matplotlib colormap to be used in this animation's colorbar or
            `None`, in which case the default colormap will be used.
        '''
        # Validate core parameters.
        assert types.is_simulator(sim), types.assert_not_simulator(sim)
        assert types.is_cells(cells), types.assert_not_parameters(cells)
        assert types.is_parameters(p), types.assert_not_parameters(p)

        # Default unpassed parameters.
        if colormap is None:
            colormap = p.default_cm

        # Validate all remaining parameters *AFTER* defaulting parameters.
        assert types.is_str_nonempty(type), (
            types.assert_not_str_nonempty(type, 'Animation type'))
        assert types.is_bool(clrAutoscale), types.assert_not_bool(clrAutoscale)
        assert types.is_numeric(clrMin), types.assert_not_numeric(clrMin)
        assert types.is_numeric(clrMax), types.assert_not_numeric(clrMax)
        assert types.is_matplotlib_colormap(colormap), (
            types.assert_not_matplotlib_colormap(colormap))

        # Classify *AFTER* validating parameters.
        self.sim = sim
        self.cells = cells
        self.p = p
        self._type = type
        self.clrAutoscale = clrAutoscale
        self.clrMin = clrMin
        self.clrMax = clrMax
        self.colormap = colormap

        # Classify private attributes to be subsequently defined.
        self._axes_title = None
        self._colorbar_mapping = None
        self._writer_frames = None
        self._writer_video = None

        #FIXME: Abandon "pyplot", all who enter here!

        # Figure encapsulating this animation.
        self.fig = pyplot.figure()

        #FIXME: Relocalize all except "_axes_bounds". We don't appear to require
        #the individual bounds to be attributes.
        # Extent of the current 2D environment.
        self._axes_x_min = self.cells.xmin * self.p.um
        self._axes_x_max = self.cells.xmax * self.p.um
        self._axes_y_min = self.cells.ymin * self.p.um
        self._axes_y_max = self.cells.ymax * self.p.um
        self._axes_bounds = [
            self._axes_x_min,
            self._axes_x_max,
            self._axes_y_min,
            self._axes_y_max,
        ]

        # Figure axes scaled to the extent of the current 2D environment.
        self.ax = pyplot.subplot(111)
        self.ax.axis('equal')
        self.ax.axis(self._axes_bounds)

        # Initialize animation saving *AFTER* defining all attribute defaults.
        self._init_saving()


    def _init_saving(self) -> None:
        '''
        Initialize this animation for platform-compatible file saving if enabled
        by the current simulation configuration or noop otherwise.
        '''

        # True if both saving and displaying animation frames.
        self._is_saving_plotted_frames = (
            self.p.turn_all_plots_off is False and
            self.p.saveAnimations is True)

        # If animation saving is disabled, noop.
        if self.p.saveAnimations is False:
            return

        # Ensure that the passed directory and file basenames are actually
        # basenames and hence contain no directory separators.
        paths.die_unless_basename(self._type)

        # Path of the phase-specific parent directory of the subdirectory to
        # which these files will be saved.
        phase_dirname = None
        if self.p.plot_type == 'sim':
            phase_dirname = self.p.sim_results
        elif self.p.plot_type == 'init':
            phase_dirname = self.p.init_results
        else:
            raise BetseExceptionParameters(
                'Anim saving unsupported during the "{}" phase.'.format(
                    self.p.plot_type))

        #FIXME: Refactor all calls to os.makedirs() everywhere similarly.

        # Path of the subdirectory to which these files will be saved, creating
        # this subdirectory and all parents thereof if needed.
        save_dirname = paths.join(
            phase_dirname, 'animation', self._type)
        save_dirname = dirs.canonicalize_and_make_unless_dir(save_dirname)

        #FIXME: Pull the image filetype from the current YAML configuration
        #rather than coercing use of ".png".
        save_frame_filetype = 'png'

        # Template yielding the basenames of frame image files to be saved.
        # The "{{"- and "}}"-delimited substring will reduce to a "{"- and "}"-
        # delimited substring after formatting, which subsequent formatting
        # elsewhere (e.g., in the "FileFrameWriter" class) will expand with the
        # 0-based index of the current frame number.
        save_frame_template_basename = '{}_{{:07d}}.{}'.format(
            self._type, save_frame_filetype)

        # Template yielding the absolute paths of frame image files to be saved.
        self._save_frame_template = paths.join(
            save_dirname, save_frame_template_basename)

        # Object writing frames from this animation to image files.
        self._writer_frames = FileFrameWriter()

        # If both saving and displaying animation frames, prepare for doing so.
        # See the _save_frame() method for horrid discussion.
        if self._is_saving_plotted_frames:
            self._writer_frames.setup(
                fig=self.fig,
                outfile=self._save_frame_template,

                #FIXME: Pass the actual desired "dpi" parameter.
                dpi=mpl_config.get_rc_param('savefig.dpi'),
            )

    # ..................{ CONCRETE ~ animate                 }..................
    def _animate(
        self,
        frame_count: int,
        figure_title: str,
        colorbar_title: str,
        colorbar_mapping: object,
        axes_x_label: str,
        axes_y_label: str,
        axes_title: str = None,
    ) -> None:
        '''
        Display this animation if the current simulation configuration
        requests plots to be displayed or noop otherwise.

        This method is intended to be called as the last statement in the
        `__init__()` method of all subclasses of this superclass.

        Attributes
        ----------
        frame_count : int
            Number of frames to be animated.
        figure_title : str
            Text displayed above the figure itself.
        colorbar_title : str
            Text displayed above the figure colorbar.
        colorbar_mapping : object
            The Matplotlib mapping (e.g., `Image`, `ContourSet`) to which this
            colorbar applies.
        axes_title : str
            Text displayed above the figure axes but below the figure title
            (i.e., `_figure_title`) _or_ `None` if no such text is to be
            displayed.
        axes_x_label : str
            Text displayed below the figure's X axis.
        axes_y_label : str
            Text displayed to the left of the figure's Y axis.
        '''
        assert types.is_int(frame_count), types.assert_not_int(frame_count)
        assert types.is_str_nonempty(figure_title), (
            types.assert_not_str_nonempty(figure_title, 'Figure title'))
        assert types.is_str_nonempty(colorbar_title), (
            types.assert_not_str_nonempty(colorbar_title, 'Colorbar title'))
        assert types.is_str_nonempty(axes_x_label), (
            types.assert_not_str_nonempty(axes_x_label, 'X axis label'))
        assert types.is_str_nonempty(axes_y_label), (
            types.assert_not_str_nonempty(axes_y_label, 'Y axis label'))

        # Classify passed parameters.
        self._colorbar_mapping = colorbar_mapping

        # If labelling each plotted cell with that cell's unique 0-based index,
        # do so.
        if self.p.enumerate_cells is True:
            for cell_index, cell_centre in enumerate(self.cells.cell_centres):
                self.ax.text(
                    self.p.um*cell_centre[0],
                    self.p.um*cell_centre[1],
                    cell_index,
                    va='center',
                    ha='center',
                )

        # If both a figure and axes title are defined, display the figure title
        # as such above the axes title.
        if axes_title is not None:
            self._axes_title = axes_title
            self.fig.suptitle(
                figure_title, fontsize=14, fontweight='bold')
        # Else, display the figure title as the axes title.
        else:
            self._axes_title = figure_title

        assert types.is_str_nonempty(self._axes_title), (
            types.assert_not_str_nonempty(self._axes_title, 'Axis title'))

        # Display the axes title and labels.
        self.ax.set_title(self._axes_title)
        self.ax.set_xlabel(axes_x_label)
        self.ax.set_ylabel(axes_y_label)

        # Set the colorbar range.
        colorbar_mapping.set_clim(self.clrMin, self.clrMax)

        # Display the colorbar.
        colorbar = self.fig.colorbar(colorbar_mapping)
        colorbar.set_label(colorbar_title)

        #FIXME: For efficiency, we should probably be passing "blit=True," to
        #FuncAnimation(). Lemon grass and dill!

        # Create and assign an animation function to a local variable. If the
        # latter is *NOT* done, this function will be garbage collected prior
        # to subsequent plot handling -- in which case only the first plot will
        # be plotted without explicit warning or error. Die, matplotlib! Die!!
        self._anim = FuncAnimation(
            self.fig, self._plot_frame,

            # Number of frames to be animated.
            frames=frame_count,

            # Delay in milliseconds between consecutive frames.
            interval=100,

            # Indefinitely repeat this animation unless saving animations, as
            # doing so under the current implementation would repeatedly (and
            # hence unnecessarily) overwrite previously written files.
            repeat=not self.p.saveAnimations,
        )

        #FIXME: It appears that movies can be saved at this exact point via the
        #following lines:
        #
        #    video_filename = 'my_filename.mp4'
        #    video_encoder_name = 'ffmpeg'
        #    ani.save(filename=video_filename, writer=video_encoder_name)
        #
        #Both the "video_filename" and "video_encoder_name" variables used
        #above should be initialized from YAML configuration items. The latter
        #should probably be configured as a list of preferred encoders: e.g.,
        #
        #    # List of Matplotlib-specific names of preferred video encoders.
        #    # The first encoder available on the current $PATH will be used.
        #    video encoders: ['ffmpeg', 'avconv', 'mencoder']
        #
        #Given that, we would then need to iteratively search this list until
        #finding the first encoder available on the current $PATH. Doesn't look
        #too hard, actually. Grandest joy in the cornucopia of easy winter!
        #FIXME: Also note that movie encoders are configurable as follows,
        #which is probably a better idea than just passing a string above:
        #
        #    Writer = animation.writers[video_encoder_name]
        #    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        #    ani.save(filename=video_filename, writer=writer)
        #
        #Oh, wait. No, that's overkill. All of the above parameters are also
        #accepted by the ani.save() function itself, so string name it is!

        try:
            #FIXME: Refactor to *NOT* use the "pyplot" API. Juggling hugs!
            # If displaying animations, do so.
            if self.p.turn_all_plots_off is False:
                loggers.log_info(
                    'Plotting animation "{}"...'.format(self._type))

                # Display this animation.
                pyplot.show()
            # Else if saving animation frames, do so.
            elif self.p.saveAnimations is True:
                loggers.log_info(
                    'Saving animation "{}" frames...'.format(self._type))

                #FIXME: Pass the "dpi" parameter as well.
                self._anim.save(
                    filename=self._save_frame_template,
                    writer=self._writer_frames)
        # plt.show() unreliably raises exceptions on window close resembling:
        #     AttributeError: 'NoneType' object has no attribute 'tk'
        # This error appears to ignorable and hence is caught and squelched.
        except AttributeError as exc:
            # If this is that exception, mercilessly squelch it.
            if str(exc) == "'NoneType' object has no attribute 'tk'":
                pass
            # Else, reraise this exception.
            else:
                raise

    # ..................{ PRIVATE ~ plot                     }..................
    def _plot_frame(self, frame_number: int) -> None:
        '''
        Iterate the current animation to the next frame.

        This method is iteratively called by Matplotlib's `FuncAnimation()`
        class instantiated by our `_animate()` method. The subclass
        implementation of this abstract method is expected to modify this
        animation's figure and axes so as to display the next frame. It is
        _not_, however, expected to save that figure to disk; frame saving is
        already implemented by this base class in a general-purpose manner.

        Specifically, this method (in order):

        . Calls the subclass `_plot_frame_figure()` method.
        . Updates the current figure's axes title with the current time.
        . Optionally writes this frame to disk if desired.

        Parameters
        ----------
        frame_number : int
            0-based index of the frame to be plotted.
        '''
        assert types.is_int(frame_number), types.assert_not_int(frame_number)

        # Plot this frame onto this animation's figure.
        self._plot_frame_figure(frame_number)

        # If the above call to the subclass _plot_frame_figure() method modified
        # either the minimum or maximum colorbar values, rescale the colorbar;
        # else, noop.
        self._colorbar_mapping.set_clim(self.clrMin, self.clrMax)

        # Update this figure with the current time, rounded to three decimal
        # places for readability.
        self.ax.set_title('{} (time {:.3f}s)'.format(
            self._axes_title, self.sim.time[frame_number]))

        # If both saving and displaying animation frames, save this frame. Note
        # that if only saving but *NOT* displaying animations, this frame will
        # be handled by our _animate() method. Why? Because Matplotlib will fail
        # to iterate frames and hence call our _plot_next_frame() method calling
        # this method *UNLESS* our _animate() method explicitly calls the
        # FuncAnimation.save() method with the writer name "frame" signifying
        # our "FileFrameWriter" class to do so. (Look. It's complicated, O.K.?)
        # if self.p.saveAnimations is False:
        if self._is_saving_plotted_frames:
            self._writer_frames.grab_frame()


    @abstractmethod
    def _plot_frame_figure(self, frame_number: int) -> None:
        '''
        Plot the frame with the passed 0-based index onto the current figure.

        Parameters
        ----------
        frame_number : int
            0-based index of the frame to be plotted.
        '''
        pass
