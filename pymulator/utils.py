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


