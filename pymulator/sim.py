""" Pymulator simulation objects """

import json
import datetime

from .serialize import PandasNumpyEncoderMixIn, hook


def importmodel(s):
    """
    Import model from string s specifying a callable. The string has the
    following structure:

        package[.package]*.model[:function]

    For example:

        foo.bar.mod:func

    Will be imported as

        from foo.bar.mod import func

    TODO: unbound class method
    """
    mname, fname = s.split(':')
    mod = __import__(mname, globals(), locals(), (fname,), 0)
    f = getattr(mod, fname)
    if not callable(f):
        raise ValueError("Model is not callable")
    return f


def funstr(fun):
    if not callable(fun):
        raise ValueError("Not a callable: {}".format(fun))
    return '{x.__module__}:{x.__qualname__}'.format(x=fun)


class Sim(object):
    """
    Simulation configuration. Includes information abou:
        - parameter spans
        - model callable
        - model outputs
        - results
        - PRNG seed / internal state

    This class mainly for correct JSON serialization/deserialization of the above information.
    """
    def __init__(self, modelstr, spans, outputs, seed=None):
        self.spans = spans
        self.model = modelstr
        self.outputs = outputs
        self.timestamp = datetime.datetime.now()
        self.seed = seed

    def __eq__(self, other):
        def _(obj):
            d = dict(obj.__dict__)
            return (d, d.pop('results', None), d.pop('state', None))
        return all(map(all, _(self), _(other)))

    def _getspans(self):
        return dict(self._spans)

    def _setspans(self, spans):
        if not hasattr(self, '_spans'):
            self._spans= {}
        for argument, vals_or_range in spans.items():
            self._spans[str(argument)] = list(vals_or_range)

    def _delspans(self):
        self._spans.clear()

    spans = property(_getspans, _setspans, _delspans, doc="Simulation spans")

    def _getmodel(self):
        return self._f

    def _setmodel(self, f_or_str):
        if isinstance(f_or_str, str):
            self._modelstr = f_or_str
            self._f = importmodel(f_or_str)
        elif callable(f_or_str):
            self._modelstr = funstr(f_or_str)
            self._f = f_or_str
        else:
            raise ValueError('Neither a callable nor a string: {}'.format(f_or_str))

    def _delmodel(self):
        del self._f
        del self._modelstr

    model = property(_getmodel, _setmodel, _delmodel, "Simulation model")

    def _setoutputs(self, outputs):
        self._outputs = list(map(str, outputs))

    def _getoutputs(self):
        return list(self._outputs)

    def _deloutput(self):
        self._outputs.clear()

    outputs = property(_getoutputs, _setoutputs, _deloutput, "Model outputs")

    def todict(self):
        d = {
            'spans': self.spans,
            'model': funstr(self.model),
            'timestamp': str(self.timestamp),
            'outputs': self.outputs
        }
        if hasattr(self, 'results'):
            d['results'] = self.results
        if hasattr(self, 'seed'):
            d['seed'] = self.seed
        if hasattr(self, 'state'):
            d['state'] = self.state
        return d

    def dumps(self):
        return json.dumps(self.todict(), cls=PandasNumpyEncoderMixIn, indent=4)

    def dump(self, path):
        with open(path, 'w') as f:
            f.write(self.dumps())

    def loads(self, s):
        return json.loads(s, hook=hook)

    def load(self, path):
        with open(path) as f:
            return self.loads(f.read())
