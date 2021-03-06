# --------------------------------------------------------
# Dragon
# Copyright(c) 2017 SeetaTech
# Written by Ting Pan
# --------------------------------------------------------

from collections import defaultdict

_TENSOR_SCOPE = ''
_PHASE_SCOPE = ''
_DEVICE_SCOPE = ''
_ENGINE_SCOPE = ''

SEPARATOR = '/'

_CURRENT_OP_IDX = 0
_SCOPE_TENSOR_IDX = defaultdict(int)

__all__ = [
    'GetTensorIdx',
    'GetTensorName',
    'GetOperatorIdx',
    'GetOperatorName',
    'TensorScope',
    'PhaseScope',
    'DeviceScope'
]

def GetOperatorIdx():
    """Get the available operator index.

    Returns
    -------
    int
        The operator index.

    """
    global _CURRENT_OP_IDX
    _CURRENT_OP_IDX = _CURRENT_OP_IDX + 1
    return _CURRENT_OP_IDX - 1


def GetTensorIdx():
    """Get the available tensor index.

    Returns
    -------
    int
        The tensor index.

    """
    global _SCOPE_TENSOR_IDX
    _SCOPE_TENSOR_IDX[_TENSOR_SCOPE] += 1
    return _SCOPE_TENSOR_IDX[_TENSOR_SCOPE] - 1


def GetOperatorName(name=None):
    """Get the available operator name.

    Parameters
    ----------
    name : str
        The optional name to use.

    Returns
    -------
    str
        The operator name.

    """
    op_idx = GetOperatorIdx()
    if name is None:
        return op_idx, 'Op_' + str(op_idx)
    else: return op_idx, name


def GetTensorName():
    """Get the available tensor name.

    Returns
    -------
    str
        The operator name.

    """
    return 'Tensor_' + str(GetTensorIdx())


class TensorScope(object):
    """TensorScope is the basic variable scope.

    Examples
    --------
    >>> with TensorScope('conv1'): a = Tensor('weights')
    >>> a.name
    >>> conv1/weight

    >>> import dragon
    >>> with dragon.name_scope('conv1'): a = Tensor('weights')
    >>> a.name
    >>> conv1/weight

    """
    def __init__(self, prefix):
        assert isinstance(prefix, type('str')), \
            "TensorScope takes in a string as its argument."
        self.prefix = prefix + SEPARATOR

    def __enter__(self):
        global _TENSOR_SCOPE
        _TENSOR_SCOPE += self.prefix
        return self.prefix.split(SEPARATOR)[0]

    def __exit__(self, type, value, traceback):
        global _TENSOR_SCOPE
        assert _TENSOR_SCOPE.endswith(self.prefix)
        _TENSOR_SCOPE = _TENSOR_SCOPE[:-len(self.prefix)]


def set_tensor_scope(name_scope):
    global _TENSOR_SCOPE
    _TENSOR_SCOPE = name_scope


class PhaseScope(object):
    """PhaseScope is a auxiliary to assign the specific phase.

    Examples
    --------
    >>> import dragon.vm.theano as theano
    >>> a = ops.RandomUniform([2, 3])
    >>> with PhaseScope(phase='train'): f = theano.function(outputs=a)

    >>> import dragon
    >>> with dragon.phase_scope(phase='test'): f = theano.function(outputs=a)

    """
    def __init__(self, phase):
        assert isinstance(phase, type('str')), \
            "PhaseScope takes in a string as its argument."
        self.phase = phase

    def __enter__(self):
        global _PHASE_SCOPE
        _PHASE_SCOPE = self.phase

    def __exit__(self, type, value, traceback):
        global _PHASE_SCOPE
        assert _PHASE_SCOPE == self.phase
        _PHASE_SCOPE = ''


class DeviceScope(object):
    """DeviceScope is a auxiliary to assign the specific device.

    Examples
    --------
    >>> with DeviceScope(device='cpu'): a = ops.RandomUniform([2, 3])

    >>> import dragon
    >>> with dragon.device_scope(device='gpu', id=0, use_cudnn=True):  a = ops.RandomUniform([2, 3])

    """
    def __init__(self, device, id=0, use_cudnn=True):
        self.device = device.lower()
        self.engine = 'CUDNN' if use_cudnn else 'DRAGON'
        assert self.device in ['cpu', 'gpu', 'cuda']
        if self.device == 'cuda': self.device = 'gpu'
        self.id = id

    def __enter__(self):
        global _DEVICE_SCOPE, _ENGINE_SCOPE
        _DEVICE_SCOPE = '/' + self.device + ':' + str(self.id)
        _ENGINE_SCOPE = self.engine

    def __exit__(self, type, value, traceback):
        global _DEVICE_SCOPE, _ENGINE_SCOPE
        _DEVICE_SCOPE = ''
        _ENGINE_SCOPE = ''