import numpy as np

try:
    import torch
    from torch import Tensor as TorchTensor
except ImportError:

    class TorchTensor:
        pass


UNKNOWN_ARRAY_TYPE = (
    "unknown array type, only numpy arrays and torch tensors are supported"
)


def norm(array, axis=None):
    """Compute the 2-norm (Frobenius norm for matrices) of the input array.

    This calls the equivalent of ``np.linalg.norm(array, axis=axis)``, see this
    function for more documentation.
    """
    if isinstance(array, np.ndarray):
        return np.linalg.norm(array, axis=axis)
    elif isinstance(array, TorchTensor):
        return torch.linalg.norm(array, dim=axis)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def dot(array1, array2):
    """Compute dot product of two arrays.
    This function has the equivalent bheaviour of  ``np.dot(array1,array2.T)``.
    For numpy array, it check if the arrays are 2D, in which case it uses the matmul,
    which is preferred according to the doc.
    For torch it uses ``torch.dot``
    if the arrays are 1D, ``torch.matmul`` is used otherwise.
    """
    if isinstance(array1, np.ndarray) and isinstance(array2, np.ndarray):
        shape1 = array1.shape
        shape2 = array2.shape
        if len(shape1) == 2 and len(shape2) == 2:
            return array1 @ array2.T
        else:
            return np.dot(array1, array2.T)
    elif isinstance(array1, TorchTensor) and isinstance(array2, TorchTensor):
        shape1 = array1.size()
        shape2 = array2.size()
        if len(shape1) == 1 and len(shape2) == 1:
            return torch.dot(array1, array2.T)
        else:
            return torch.matmul(array1, torch.Traspose(array2))
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def linalg_inv(array, detach=False):
    """Compute the (multiplicative) inverse of a matrix.
    This function has the equivalent bheaviour of  ``numpy.linalg.inv(array)``.
    """
    if isinstance(array, np.ndarray):
        return np.linalg.inv(array)
    elif isinstance(array, torch.Tensor):
        result = torch.linalg.inv(array)
        if detach:
            result = result.detach()
        return result
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def solve(array1, array2):
    """Computes the solution of a square system of linear equations
    with a unique solution.
    This function has the equivalent
    behaviour of  ``numpy.linalg.solve(array1,array2)``.
    """
    if isinstance(array1, np.ndarray) and isinstance(array2, np.ndarray):
        return np.linalg.solve(array1, array2)
    elif isinstance(array1, TorchTensor) and isinstance(array2, TorchTensor):
        result = torch.linalg.solve(array1, array2)
        return result
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def lstsq(array1, array2, rcond=None):
    """
    Computes a solution to the least squares problem
    of a system of linear equations.
    Computes the vector x that approximately
    solves the equation ``array1 @ x = array2``.
    This function has the equivalent
    behaviour of ``numpy.linalg.lstsq(array1,array2)``.
    """
    if isinstance(array1, np.ndarray) and isinstance(array2, np.ndarray):
        return np.linalg.lstsq(array1, array2, rcond=rcond)[0]
    elif isinstance(array1, TorchTensor) and isinstance(array2, TorchTensor):
        result = torch.linalg.lstsq(array1, array2, rcond=rcond)[0]
        return result
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def vstack(arrays):
    """Stack vertically a group of arrays.
    This function has the equivalent
    behaviour of ``numpy.vstack(arrays)``.

    Args:
        arrays : sequence of arrays

    Returns:
        array : vertical-stacked array
    """
    if isinstance(arrays[0], np.ndarray):
        return np.vstack(arrays)
    elif isinstance(arrays[0], TorchTensor):
        return torch.vstack(arrays)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)
