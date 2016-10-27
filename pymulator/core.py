#!/usr/bin/python3

import numpy
import scipy.stats
import pandas
import itertools
import json
import datetime


def draw(steps, n=10, alpha=1, beta=0.5, prng=numpy.random):
    assert steps > 0, "At least one step required"
    assert n > 0, "At least one item required"
    assert alpha >= 0, "Alpha must be non-negative"
    assert 0 <= beta <= 1, "Beta must be a probability"
    items = numpy.arange(n)
    q = numpy.linspace(0, 1, n, endpoint=False) + 1.0 / n
    pq = q / q.sum()
    c = numpy.ones(n)
    pc = c / n  # alpha not needed here
    for i in range(steps):
        u = prng.rand(1)
        if u < beta:
            # quality
            k = prng.choice(items, p=pq)
        else:
            k = prng.choice(items, p=pc)
        c[k] += 1
        pc = c ** alpha / numpy.sum(c ** alpha)
    quality = numpy.sum(q * c) / numpy.sum(c)
    result = scipy.stats.kendalltau(q, c)
    efficiency = result.correlation
    return {
        'results': {
            'quality': quality,
            'efficiency': efficiency
        },
        'parameters': {
            'steps': steps,
            'n': n,
            'alpha': alpha,
            'beta': beta,
        }
    }


def simulatereps(reps=10, **kwargs):
    reps = kwargs.pop('reps', 1)
    assert reps > 0, "reps must be > 0"
    tmp = []
    for i in range(reps):
        r = draw(**kwargs)
        tmp.append(r['results'])
    df = pandas.DataFrame(tmp)
    results = df.mean().to_dict()
    results.update(r['parameters'])
    return results


def simulate(spans):
    namedvalues = (itertools.product((k,), v) for k, v in spans.items())
    x = itertools.product(*namedvalues)
    tmp = []
    for tups in x:
        kw = dict(tups)
        d = simulatereps(**kw)
        tmp.append(d)
    return pandas.DataFrame(tmp)


def _default(df):
    return json.loads(df.to_json(orient='records'))


if __name__ == '__main__':
    path = './test.json'
    seed = 1
    numpy.random.seed(seed)
    spans = {
        'alpha': [0, 0.5, 1, 2],
        'beta': list(numpy.linspace(0, 1, num=21, endpoint=True)),
        'steps': [10000],
        'reps': [10]
    }
    c = simulate(spans)
    results = {
        'timestamp': str(datetime.datetime.now()),
        'seed': seed,
        'spans': spans,
        'records': c,
    }
    with open(path, 'w') as f:
        json.dump(results, f, default=_default)

    print('Results written to {}'.format(path))

