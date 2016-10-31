import numpy
import pandas
import itertools
import functools
import inspect

from . import sim

# Progress bar
try:
    import progress.bar
    with_progress = True
    class ETABar(progress.bar.IncrementalBar):
        suffix = '%(index)d/%(max)d [%(percent).0f%% - %(eta_td)s]'
except ImportError:
    import warnings
    warnings.warn("Could not import progress bar module")
    with_progress = False


def simulateone(f, names=None, **kwargs):
    """
    Simulate one replica of one point in the space of parameters

    Parameters
    ==========
    f : callable
        The model

    names : sequence
        Optional; list of output variable names. If not specified: out1, out2, ...

    kwargs : dict
        Dictionary of model parameters

    Returns
    =======
    r : dict
        A dictionary with all bound arguments of f and, for each
    """
    try:
        del kwargs['_reps']
    except KeyError:
        pass
    y = f(**kwargs)
    sig = inspect.signature(f)
    a = sig.bind(**kwargs)
    a.apply_defaults()
    try:
        # remove stuff we don't need to return
        del a.arguments['prng']
    except KeyError:
        pass
    ytup = tuple(y)
    ny = len(ytup)
    if names is None:
        names = ['out{:d}'.format(i) for i in range(ny)]
    r = dict(zip(names, ytup))
    r.update(dict(a.arguments))
    return r


def simulate(s):
    """
    Simulate from configuration object

    Parameters
    ==========
    c : dict
        A configuration dictionary
    """
    namedvalues = (itertools.product((k,), v) for k, v in s.spans.items())
    x = itertools.product(*namedvalues)
    tmp = []
    # Set the pseudo-random number generator
    if s.seed is not None:
        numpy.random.seed(s.seed)
    elif hasattr(s, 'state'):
        numpy.random.set_state(s.state)
    else:
        s.state = numpy.random.get_state()
    # Progress bar
    if with_progress:
        n = functools.reduce(int.__mul__,
                             map(len, s.spans.values()))
        x = ETABar(sim.funstr(s.model), max=n).iter(x)
    # Sequential sulation loop
    for tups in x:
        kw = dict(tups)
        d = simulateone(s.model, names=s.outputs, **kw)
        tmp.append(d)
    # Average results
    df = pandas.DataFrame(tmp)
    cols = list(df.columns)
    for n in s.outputs:
        cols.remove(n)
    return df.groupby(cols, as_index=False).mean()


if __name__ == '__main__':
    path = './test.json'
    spans = {
        'alpha': [0, 0.5, 1, 2],
        'beta': list(numpy.linspace(0, 1, num=21, endpoint=True)),
        'steps': [100],
        '_reps': list(range(10))
    }
    s = sim.Sim('urn:draw', spans, ['quality', 'efficiency'], seed=1)
    df = simulate(s)
    s.results = df
    s.dump(path)
    print('Results written to {}'.format(path))

