import numpy
import scipy.stats

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
    return quality, efficiency
    #return {
    #    'results': {
    #        'quality': quality,
    #        'efficiency': efficiency
    #    },
    #    'parameters': {
    #        'steps': steps,
    #        'n': n,
    #        'alpha': alpha,
    #        'beta': beta,
    #    }
    #}

