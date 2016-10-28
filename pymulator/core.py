import numpy
import pandas
import itertools
import functools
import json
import datetime
import inspect

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
    """
    rep = kwargs.pop('_reps', None)
    y = f(**kwargs)
    sig = inspect.signature(f)
    a = sig.bind(**kwargs)
    a.apply_defaults()
    try:
        del a.arguments['prng']
    except KeyError:
        pass
    ytup = tuple(y)
    ny = len(ytup)
    if names is None:
        names = ['Var{}'.format(i) for i in range(ny)]
    r = dict(zip(names, ytup))
    r.update(dict(a.arguments))
    if rep is not None:
        r['_reps'] = rep
    return r


def simulate(c):
    """
    Simulate from configuration object
    """
    mname, fname = c['model'].split(':')
    mod = __import__(mname, globals(), locals(), (fname,), 0)
    f = getattr(mod, fname)
    assert callable(f), "Model is not callable"
    namedvalues = (itertools.product((k,), v)
                   for k, v in c['spans'].items())
    x = itertools.product(*namedvalues)
    tmp = []
    if 'seed' in c:
        numpy.random.seed(c['seed'])
    elif 'state' in c:
        numpy.random.set_state(c['state'])
    else:
        c['state'] = numpy.random.get_state()
    if with_progress:
        n = functools.reduce(int.__mul__,
                             map(len, c['spans'].values()))
        x = ETABar(c['model'], max=n).iter(x)
    for tups in x:
        kw = dict(tups)
        d = simulateone(f, names=c['outputs'], **kw)
        tmp.append(d)
    df = pandas.DataFrame(tmp)
    cols = list(df.columns)
    for n in c['outputs']:
        cols.remove(n)
    cols.remove('_reps')
    return df.groupby(cols, as_index=False).mean()


def _default(df):
    return json.loads(df.to_json(orient='records'))


if __name__ == '__main__':
    path = './test.json'
    spans = {
        'alpha': [0, 0.5, 1, 2],
        'beta': list(numpy.linspace(0, 1, num=21, endpoint=True)),
        'steps': [100],
        '_reps': list(range(10))
    }
    c = {
        'spans': spans,
        'model': 'urn:draw',
        'seed': 1,
        'timestamp': str(datetime.datetime.now()),
        'outputs': ['quality', 'efficiency']
    }
    df = simulate(c)
    c['records'] = df
    with open(path, 'w') as f:
        json.dump(c, f, default=_default, indent=4)

    print('Results written to {}'.format(path))

