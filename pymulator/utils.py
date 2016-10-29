import base64
import json
import numpy
import pandas

class NumpyArrayEncoder(json.JSONEncoder):
    """
    Adapted from: http://stackoverflow.com/a/24375113
    """
    def default(self, obj):
        """
        If input object is an ndarray it will be converted into a dict holding
        dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, numpy.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = numpy.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64, dtype=str(obj.dtype), shape=obj.shape)
        # Let the base class default method raise the TypeError
        return super(NumpyArrayEncoder, self).default(obj)


class PandasDataFrameEncoder(json.JSONEncoder):
    """
    Encodes Pandas data frame objects are list of records
    """
    def default(self, obj):
        if isinstance(obj, pandas.DataFrame):
            d = {}
            d["__dataframe__"] = 'records'
            d['data'] = obj.to_dict(orient='records')
            return d
        # Let the base class default method raise the TypeError
        return super(PandasDataFrameEncoder, self).default(obj)


class PandasNumpyEncoderMixIn(json.JSONEncoder):
    def default(self, obj):
        try:
            return NumpyArrayEncoder().default(obj)
        except TypeError:
            pass
        try:
            return PandasDataFrameEncoder().default(obj)
        except TypeError:
            pass
        return super(PandasNumpyEncoderMixIn).default(obj)


def hook(d):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(d, dict) and '__ndarray__' in d:
        data = base64.b64decode(d['__ndarray__'])
        return numpy.frombuffer(data, d['dtype']).reshape(d['shape'])
    if isinstance(d, dict) and '__dataframe__' in d:
        return pandas.DataFrame.from_records(d['data'])
    return d


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


# if __name__ == '__main__':
    # expected = numpy.arange(100, dtype=numpy.float)
    # dumped = json.dumps(expected, cls=NumpyArrayEncoder)
    # result = json.loads(dumped, object_hook=json_numpy_obj_hook)


    # # None of the following assertions will be broken.
    # assert result.dtype == expected.dtype, "Wrong Type"
    # assert result.shape == expected.shape, "Wrong Shape"
    # assert np.allclose(expected, result), "Wrong Values"
