import numpy as np
from . import evaluate
from skimage import color
from matplotlib import cm, pyplot as plt
import itertools as it
from math import ceil

###########################
# VISUALIZATION FUNCTIONS #
###########################

def imshow_grey(im, axis=None):
    """Show a segmentation using a gray colormap.

    Parameters
    ----------
    im : np.ndarray of int, shape (M, N)
        The segmentation to be displayed.

    Returns
    -------
    fig : plt.Figure
        The image shown.
    """
    if axis is None:
        fig, axis = plt.subplots()
    return axis.imshow(im, cmap='gray')


def imshow_magma(im, axis=None):
    """Show a segmentation using a magma colormap.

    Parameters
    ----------
    im : np.ndarray of int, shape (M, N)
        The segmentation to be displayed.

    Returns
    -------
    fig : plt.Figure
        The image shown.
    """
    if axis is None:
        fig, axis = plt.subplots()
    return axis.imshow(im, cmap='magma')


def imshow_rand(im, axis=None, labrandom=True):
    """Show a segmentation using a random colormap.

    Parameters
    ----------
    im : np.ndarray of int, shape (M, N)
        The segmentation to be displayed.
    labrandom : bool, optional
        Use random points in the Lab colorspace instead of RGB.

    Returns
    -------
    fig : plt.Figure
        The image shown.
    """
    if axis is None:
        fig, axis = plt.subplots()
    rand_colors = np.random.random(size=(ceil(np.max(im)), 3))
    if labrandom:
        rand_colors[:, 0] = rand_colors[:, 0] * 81 + 39
        rand_colors[:, 1] = rand_colors[:, 1] * 185 - 86
        rand_colors[:, 2] = rand_colors[:, 2] * 198 - 108
        rand_colors = color.lab2rgb(rand_colors[np.newaxis, ...])[0]
        rand_colors[rand_colors < 0] = 0
        rand_colors[rand_colors > 1] = 1
    rcmap = cm.colors.ListedColormap(np.concatenate((np.zeros((1, 3)),
                                                     rand_colors)))
    return axis.imshow(im, cmap=rcmap)


def show_multiple_images(*images, axes=None, image_type='raw'):
    """Returns a figure with subplots containing multiple images.

    Parameters
    ----------
    images : np.ndarray of int, shape (M, N)
        The input images to be displayed.
    axes: matplotlib.AxesImage, optional
        Whether to pass in multiple axes. Must be equal to the number of
        input images.
    image_type : string, optional
        Displays the images with different colormaps. Set to display
        'raw' by default. Other options that are accepted
        are 'grey' and 'magma', or 'rand'.

    Returns
    -------
    fig : plt.Figure
        The image shown.
    """
    number_of_im = len(images)
    figure = plt.figure()
    for i in range(number_of_im):
        ax = (figure.add_subplot(1, number_of_im, i+1) if axes is None
              else axes[i])
        if image_type == 'grey' or image_type == 'gray':
            imshow_grey(images[i], axis=ax)
        elif image_type == 'magma':
            imshow_magma(images[i], axis=ax)
        elif image_type == 'rand':
            imshow_rand(images[i], axis=ax)
        elif image_type == 'raw':
            ax.imshow(images[i])
        else:
            print("not a valid image type.")
            return None
        ax.set_title(f'Image number {i+1} with a {image_type} colormap.')
    return ax


def draw_seg(seg, im):
    """Return a segmentation map matching the original image color.

    Parameters
    ----------
    seg : np.ndarray of int, shape (M, N, ...)
        The segmentation to be displayed
    im : np.ndarray, shape (M, N, ..., C)
        The image corresponding to the segmentation.

    Returns
    -------
    out : np.ndarray, same shape and type as `im`.
        An image where each segment has uniform color.

    Examples
    --------
    >>> a = np.array([[1, 1, 2, 2],
    ...               [1, 2, 2, 3],
    ...               [2, 2, 3, 3]])
    >>> g = np.array([[0.5, 0.2, 1.0, 0.9],
    ...               [0.2, 0.8, 0.9, 0.6],
    ...               [0.9, 0.9, 0.4, 0.5]])
    >>> draw_seg(a, g)
    array([[0.3, 0.3, 0.9, 0.9],
           [0.3, 0.9, 0.9, 0.5],
           [0.9, 0.9, 0.5, 0.5]])
    """
    out = np.zeros_like(im)
    labels = np.unique(seg)
    if (seg==0).any():
        labels = labels[1:]
    for u in labels:
        mask = (seg == u).nonzero()
        color = im[mask].mean(axis=0)
        out[mask] = color
    return out


def display_3d_segmentations(segs, image=None, probability_map=None, axis=0,
                             z=None, fignum=None):
    """Show slices of multiple 3D segmentations.

    Parameters
    ----------
    segs : list or tuple of np.ndarray of int, shape (M, N, P)
        The segmentations to be examined.
    image : np.ndarray, shape (M, N, P[, 3]), optional
        The image corresponding to the segmentations.
    probability_map : np.ndarray, shape (M, N, P), optional
        The segment boundary probability map.
    axis : int in {0, 1, 2}, optional
        The axis along which to show a slice of the segmentation.
    z : int in [0, `(M, N, P)[axis]`), optional
        The slice to display. Defaults to the middle slice.
    fignum : int, optional
        Which figure number to use. Uses the default (new figure) if none is
        provided.

    Returns
    -------
    fig : plt.Figure
        The figure handle.
    """
    numplots = len(segs)
    if image is not None:
        numplots += 1
    if probability_map is not None:
        numplots += 1
    candidate_plot_arrangements = list(it.combinations_with_replacement(
                                       range(1, 5), 2))
    # get the smallest plot arrangement that can display the number of
    # segmentations we want
    plot_arrangement = [(i, j) for i, j in candidate_plot_arrangements
                        if i * j >= numplots][0]
    fig = plt.figure(fignum)
    current_subplot = 1
    if image is not None:
        plt.subplot(*plot_arrangement + (current_subplot,))
        imshow_grey(np.rollaxis(image, axis)[z])
        current_subplot += 1
    if probability_map is not None:
        plt.subplot(*plot_arrangement + (current_subplot,))
        imshow_magma(np.rollaxis(probability_map, axis)[z])
        current_subplot += 1
    for i, j in enumerate(range(current_subplot, numplots + 1)):
        plt.subplot(*plot_arrangement + (j,))
        imshow_rand(np.rollaxis(segs[i], axis)[z])
    return fig


def plot_vi(g, history, gt, fig=None):
    """Plot the VI from segmentations based on Rag and sequence of merges.

    Parameters
    ----------
    g : agglo.Rag object
        The region adjacency graph.

    history : list of tuples
        The merge history of the RAG.

    gt : np.ndarray
        The ground truth corresponding to the RAG.

    fig : plt.Figure, optional
        Use this figure for plotting. If not provided, a new figure is created.

    Returns
    -------
    None
    """
    v = []
    n = []
    seg = g.get_segmentation()
    for i in history:
        seg[seg==i[1]] = i[0]
        v.append(evaluate.vi(seg, gt))
        n.append(len(np.unique(seg)-1))
    if fig is None:
        fig = plt.figure()
    plt.plot(n, v, figure = fig)
    plt.xlabel('Number of segments', figure = fig)
    plt.ylabel('vi', figure = fig)


def plot_vi_breakdown_panel(px, h, title, xlab, ylab, hlines, scatter_size,
                            **kwargs):
    """Plot a single panel (over or undersegmentation) of VI breakdown plot.

    Parameters
    ----------
    px : np.ndarray of float, shape (N,)
        The probability (size) of each segment.
    h : np.ndarray of float, shape (N,)
        The conditional entropy of that segment.
    title, xlab, ylab : string
        Parameters for `matplotlib.plt.plot`.
    hlines : iterable of float
        Plot hyperbolic lines of same VI contribution. For each value `v` in
        `hlines`, draw the line `h = v/px`.
    scatter_size : int, optional
    **kwargs : dict
        Additional keyword arguments for `matplotlib.pyplot.plot`.

    Returns
    -------
    None
    """
    x = np.arange(max(min(px),1e-10), max(px), (max(px)-min(px))/100.0)
    for val in hlines:
        plt.plot(x, val/x, color='gray', ls=':', **kwargs)
    plt.scatter(px, h, label=title, s=scatter_size, **kwargs)
    # Make points clickable to identify ID. This section needs work.
    plt.xlim(xmin=-0.05*max(px), xmax=1.05*max(px))
    plt.ylim(ymin=-0.05*max(h), ymax=1.05*max(h))
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)


def plot_vi_breakdown(seg, gt, ignore_seg=[], ignore_gt=[],
                      hlines=None, subplot=False, figsize=None, **kwargs):
    """Plot conditional entropy H(Y|X) vs P(X) for both seg|gt and gt|seg.

    Parameters
    ----------
    seg : np.ndarray of int, shape (M, [N, ..., P])
        The automatic (candidate) segmentation.
    gt : np.ndarray of int, shape (M, [N, ..., P]) (same as `seg`)
        The gold standard/ground truth segmentation.
    ignore_seg : list of int, optional
        Ignore segments in this list from the automatic segmentation during
        evaluation and plotting.
    ignore_gt : list of int, optional
        Ignore segments in this list from the ground truth segmentation during
        evaluation and plotting.
    hlines : int, optional
        Plot this many isoclines between the minimum and maximum VI
        contributions.
    subplot : bool, optional
        If True, plot oversegmentation and undersegmentation in separate
        subplots.
    figsize : tuple of float, optional
        The figure width and height, in inches.
    **kwargs : dict
        Additional keyword arguments for `matplotlib.pyplot.plot`.

    Returns
    -------
    None
    """
    plt.ion()
    pxy,px,py,hxgy,hygx,lpygx,lpxgy = evaluate.vi_tables(seg, gt,
                                                         ignore_seg, ignore_gt)
    cu = -px*lpygx
    co = -py*lpxgy
    if hlines is None:
        hlines = []
    elif hlines == True:
        hlines = 10
    if type(hlines) == int:
        maxc = max(cu[cu!=0].max(), co[co!=0].max())
        hlines = np.arange(maxc/hlines, maxc, maxc/hlines)
    plt.figure(figsize=figsize)
    if subplot: plt.subplot(1,2,1)
    plot_vi_breakdown_panel(px, -lpygx,
        'False merges', 'p(S=seg)', 'H(G|S=seg)',
        hlines, c='blue', **kwargs)
    if subplot: plt.subplot(1,2,2)
    plot_vi_breakdown_panel(py, -lpxgy,
        'False splits', 'p(G=gt)', 'H(S|G=gt)',
        hlines, c='orange', **kwargs)
    if not subplot:
        plt.title('vi contributions by body.')
        plt.legend(loc='upper right', scatterpoints=1)
        plt.xlabel('Segment size (fraction of volume)', fontsize='large')
        plt.ylabel('Conditional entropy (bits)', fontsize='large')
        xmax = max(px.max(), py.max())
        plt.xlim(-0.05*xmax, 1.05*xmax)
        ymax = max(-lpygx.min(), -lpxgy.min())
        plt.ylim(-0.05*ymax, 1.05*ymax)


def add_opts_to_plot(ars, colors='k', markers='^', **kwargs):
    """In an existing active split-vi plot, add the point of optimal VI.

    By default, a star marker is used.

    Parameters
    ----------
    ars : list of numpy arrays
        Each array has shape (2, N) and represents a split-VI curve,
        with `ars[i][0]` holding the undersegmentation and `ars[i][1]`
        holding the oversegmentation for each `i`.
    colors : string, list of string, or list of float tuple, optional
        A color specification or list of color specifications. If there
        are fewer colors than split-VI arrays, the colors are cycled.
    markers : string, or list of string, optional
        Point marker specification (as defined in matplotlib) or list
        thereof. As with colors, if there are fewer markers than VI
        arrays, the markers are cycled.
    **kwargs : dict (string keys), optional
        Keyword arguments to be passed through to
        `matplotlib.pyplot.scatter`.

    Returns
    -------
    points : list of `matplotlib.collections.PathCollection`
        The points returned by each of the calls to `scatter`.
    """
    if type(colors) not in [list, tuple]:
        colors = [colors]
    if len(colors) < len(ars):
        colors = it.cycle(colors)
    if type(markers) not in [list, tuple]:
        markers = [markers]
    if len(markers) < len(ars):
        markers = it.cycle(markers)
    points = []
    for ar, c, m in zip(ars, colors, markers):
        opt = ar[:,ar.sum(axis=0).argmin()]
        points.append(plt.scatter(opt[0], opt[1], c=c, marker=m, **kwargs))
    return points

def add_nats_to_plot(ars, tss, stops=0.5, colors='k', markers='o', **kwargs):
    """In an existing active split-vi plot, add the natural stopping point.

    By default, a circle marker is used.

    Parameters
    ----------
    ars : list of numpy arrays
        Each array has shape (2, N) and represents a split-VI curve,
        with `ars[i][0]` holding the undersegmentation and `ars[i][1]`
        holding the oversegmentation for each `i`.
    tss : list of numpy arrays
        Each array has shape (N,) and represents the algorithm
        threshold that gave rise to the VI measurements in `ars`.
    stops : float, optional
        The natural stopping point for the algorithm. For example, if
        an algorithm merges segments according to a merge probability,
        the natural stopping point is at $p=0.5$, when there are even
        odds of the merge being a true merge.
    colors : string, list of string, or list of float tuple, optional
        A color specification or list of color specifications. If there
        are fewer colors than split-VI arrays, the colors are cycled.
    markers : string, or list of string, optional
        Point marker specification (as defined in matplotlib) or list
        thereof. As with colors, if there are fewer markers than VI
        arrays, the markers are cycled.
    **kwargs : dict (string keys), optional
        Keyword arguments to be passed through to
        `matplotlib.pyplot.scatter`.

    Returns
    -------
    points : list of `matplotlib.collections.PathCollection`
        The points returned by each of the calls to `scatter`.
    """
    if type(colors) not in [list, tuple]: colors = [colors]
    if len(colors) < len(ars): colors = it.cycle(colors)
    if type(markers) not in [list, tuple]: markers = [markers]
    if len(markers) < len(ars): markers = it.cycle(markers)
    if type(stops) not in [list, tuple]: stops = [stops]
    if len(stops) < len(ars): stops = it.cycle(stops)
    points = []
    for ar, ts, stop, c, m in zip(ars, tss, stops, colors, markers):
        nat = ar[:,np.flatnonzero(ts<stop)[-1]]
        points.append(plt.scatter(nat[0], nat[1], c=c, marker=m, **kwargs))
    return points

def plot_split_vi(ars, best=None, colors='k', linespecs='-', **kwargs):
    """Make a split-VI plot.

    The split-VI plot was introduced in Nunez-Iglesias et al, 2013 [1]

    Parameters
    ----------
    ars : array or list of arrays of float, shape (2, N)
        The input VI arrays. `ars[i][0]` should contain the
        undersegmentation and `ars[i][1]` the oversegmentation.
    best : array-like of float, len=2, optional
        Agglomerative segmentations can't get to (0, 0) VI if the
        starting superpixels are not perfectly aligned with the gold
        standard segmentation. Therefore, there is a point of best
        achievable VI. `best` should contain the coordinates of this
        point.
    colors : matplotlib color specification or list thereof, optional
        The color of each line being plotted. If there are fewer colors
        than arrays, they are cycled.
    linespecs : matplotlib line type spec, or list thereof, optional
        The line type to plot with ('-', '--', '-.', etc).
    kwargs : dict, string keys, optional
        Additional keyword arguments to pass through to plt.plot.

    Returns
    -------
    lines : matplotlib Lines2D object(s)
        The lines plotted.
    """
    if type(ars) not in [list, tuple]: ars = [ars]
    if type(colors) not in [list, tuple]: colors = [colors]
    if len(colors) < len(ars): colors = it.cycle(colors)
    if type(linespecs) not in [list, tuple]: linespecs = [linespecs]
    if len(linespecs) < len(ars): linespecs = it.cycle(linespecs)
    lines = []
    for ar, color, linespec in zip(ars, colors, linespecs):
        lines.append(plt.plot(ar[0], ar[1], c=color, ls=linespec, **kwargs))
    if best is not None:
        lines.append(plt.scatter(
            best[0], best[1],
            c=kwargs.get('best-color', 'k'), marker=(5,3,0), **kwargs)
        )
    return lines


def plot_decision_function(clf, data_range=None,
                           features=None, labels=None, feature_columns=[0, 1],
                           n_gridpoints=201):
    """Plot the decision function of a classifier in 2D.

    Parameters
    ----------
    clf : scikit-learn classifier
        The classifier to be evaluated.
    data_range : tuple of int, optional
        The range of values to be evaluated.
    features : 2D array of float, optional
        The features of the training data.
    labels : 1D array of int, optional
        The labels of the training data.
    feature_columns : tuple of int, optional
        Which feature columns to plot, if there are more than two.
    n_gridpoints : int, optional
        The number of points to place on each dimension of the 2D grid.
    """
    if features is not None:
        features = features[:, feature_columns]
        minfeat, maxfeat = np.min(features), np.max(features)
        featrange = maxfeat - minfeat

    if data_range is None:
        if features is None:
            data_range = (0, 1)
        else:
            data_range = (minfeat - 0.05 * featrange,
                          maxfeat + 0.05 * featrange)

    data_range = np.array(data_range)

    grid = np.linspace(*data_range, num=n_gridpoints, endpoint=True)
    rr, cc = np.meshgrid(grid, grid, sparse=False)
    feature_space = np.hstack((np.reshape(rr, (-1, 1)),
                               np.reshape(cc, (-1, 1))))
    prediction = clf.predict_proba(feature_space)[:, 1]  # Pr(class(X)=1)
    prediction = np.reshape(prediction, (n_gridpoints, n_gridpoints))

    fig, ax = plt.subplots()
    ax.imshow(prediction, cmap='RdBu')
    ax.set_xticks([])
    ax.set_yticks([])

    features = (features - data_range[0]) / (data_range[1] - data_range[0])

    if features is not None:
        if labels is not None:
            label_colors = cm.viridis(labels.astype(float) / np.max(labels))
        else:
            label_colors = cm.viridis(np.zeros(features.shape[0]))
        ax.scatter(*(features.T * n_gridpoints), c=label_colors)
    plt.show()


def plot_seeds(raw_image, seed_image, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1, 1)
    ax.imshow(raw_image, cmap='gray', interpolation='nearest')
    plt.autoscale = False
    ax.plot(*np.nonzero(seed_image)[::-1], 'r.')
