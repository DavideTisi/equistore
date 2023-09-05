from typing import List, Optional, Union

import numpy as np

from ._classes import torch_jit_is_scripting


try:
    import torch
    from torch import Tensor as TorchTensor

    torch_dtype = torch.dtype
    torch_device = torch.device

except ImportError:

    class TorchTensor:
        pass

    class torch_dtype:
        pass

    class torch_device:
        pass


UNKNOWN_ARRAY_TYPE = (
    "unknown array type, only numpy arrays and torch tensors are supported"
)


def _check_all_torch_tensor(arrays: List[TorchTensor]):
    for array in arrays:
        if not isinstance(array, TorchTensor):
            raise TypeError(
                f"expected argument to be a torch.Tensor, but got {type(array)}"
            )


def _check_all_np_ndarray(arrays):
    for array in arrays:
        if not isinstance(array, np.ndarray):
            raise TypeError(
                f"expected argument to be a np.ndarray, but got {type(array)}"
            )


def all(a, axis: Optional[int] = None):
    """Test whether all array elements along a given axis evaluate to True.

    This function has the same behavior as
    ``np.all(array,axis=axis)``.
    """
    if isinstance(a, TorchTensor):
        # torch.all has two implementation, and picks one depending if more than one
        # parameter is given. The second one does not supports setting dim to `None`
        if axis is None:
            return torch.all(input=a)
        else:
            return torch.all(input=a, dim=axis)
    elif isinstance(a, np.ndarray):
        return np.all(a=a, axis=axis)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def allclose(
    a: TorchTensor, b: TorchTensor, rtol: float, atol: float, equal_nan: bool = False
):
    """Compare two arrays using ``allclose``

    This function has the same behavior as
    ``np.allclose(array1, array2, rtol, atol, equal_nan)``.
    """
    if isinstance(a, TorchTensor):
        _check_all_torch_tensor([b])
        return torch.allclose(
            input=a, other=b, rtol=rtol, atol=atol, equal_nan=equal_nan
        )
    elif isinstance(a, np.ndarray):
        _check_all_np_ndarray([b])
        return np.allclose(a=a, b=b, rtol=rtol, atol=atol, equal_nan=equal_nan)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def bincount(input, weights: Optional[TorchTensor] = None, minlength: int = 0):
    """Count number of occurrences of each value in array of non-negative ints.
    Equivalent of ``numpy.bitcount(input, weights, minlength)``

    Args:
        input (array_like): Input array.
        weights (array_like, optional): Weights, array of the same shape as input.
                                        Defaults to None.
        minlength (int, optional): A minimum number of bins for the output array.
                                        Defaults to 0.
    Note:
        In the main code this function is only used with ``np.ndarray`` as an input,
        since the indexes comes from labels which are always ``np.ndarray``. If you
        want to use the result of ``bincount`` to operate with ``TorchTensor``, you
        should follow this with a call to `_dispatch.array_like_data` to transform it
        in a ``TorchTensor`` with the desired properties.
    """
    if isinstance(input, TorchTensor):
        if weights is not None:
            _check_all_torch_tensor([weights])
        return torch.bincount(input, weights=weights, minlength=minlength)
    elif isinstance(input, np.ndarray):
        if weights is not None:
            _check_all_np_ndarray([weights])
        return np.bincount(input, weights=weights, minlength=minlength)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def copy(array):
    """Returns a copy of ``array``.
    The new data is not shared with the original array"""
    if isinstance(array, TorchTensor):
        return array.clone()
    elif isinstance(array, np.ndarray):
        return array.copy()
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def eye_like(array, size: int):
    """
    Create an identity matrix with the given ``size``, and the same
    dtype and device as ``array``.
    """

    if isinstance(array, TorchTensor):
        return torch.eye(size).to(array.dtype).to(array.device)
    elif isinstance(array, np.ndarray):
        return np.eye(size, dtype=array.dtype)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def list_to_array(array, data: Union[List[int], List[List[int]]]):
    """Create an object from data with the same type as ``array``."""
    if isinstance(array, TorchTensor):
        return torch.tensor(data).to(array.dtype).to(array.device)
    elif isinstance(array, np.ndarray):
        return np.array(data)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def norm(array, axis=None):
    """Compute the 2-norm (Frobenius norm for matrices) of the input array.

    This calls the equivalent of ``np.linalg.norm(array, axis=axis)``, see this
    function for more documentation.
    """
    if isinstance(array, TorchTensor):
        return np.linalg.norm(array, axis=axis)
    elif isinstance(array, np.ndarray):
        return torch.linalg.norm(array, dim=axis)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def dot(A, B):
    """Compute dot product of two arrays.

    This function has the same behavior as  ``np.dot(A, B.T)``, and assumes the
    second array is 2-dimensional.
    """
    if isinstance(A, TorchTensor):
        _check_all_torch_tensor([B])
        assert len(B.shape) == 2
        return A @ B.T
    elif isinstance(A, np.ndarray):
        _check_all_np_ndarray([B])
        shape1 = A.shape
        assert len(B.shape) == 2
        # Using matmul/@ is the recommended way in numpy docs for 2-dimensional
        # matrices
        if len(shape1) == 2:
            return A @ B.T
        else:
            return np.dot(A, B.T)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def solve(X, Y):
    """
    Computes the solution of a square system of linear equations with a unique
    solution.

    This function has the same behavior as ``numpy.linalg.solve(X, Y)``.
    """
    if isinstance(X, TorchTensor):
        _check_all_torch_tensor([Y])
        result = torch.linalg.solve(X, Y)
        return result
    elif isinstance(X, np.ndarray):
        _check_all_np_ndarray([Y])
        return np.linalg.solve(X, Y)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def sqrt(array):
    """Compute the square root  of the input array.

    This calls the equivalent of ``np.sqrt(array)``, see this
    function for more documentation.
    """
    if isinstance(array, TorchTensor):
        return torch.sqrt(array)
    elif isinstance(array, np.ndarray):
        return np.sqrt(array)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def lstsq(X, Y, rcond: Optional[float], driver: Optional[str] = None):
    """
    Computes a solution to the least squares problem of a system of linear
    equations.

    Computes the vector x that approximately solves the equation ``array1 @ x =
    array2``. This function has the same behavior as ``numpy.linalg.lstsq(X,
    Y)``.

    :param rcond: Cut-off ratio for small singular values of a.
        WARNING: the default rcond=None for numpy and torch is different
        numpy -> rcond is the machine precision times max(M, N).
                with M, N being the dimensions of array1
        torch -> rcond is the machine precision,
                to have this behavior in numpy use
                rcond=-1

    :param driver: Used only in torch (ignored if numpy is used).
            Chooses the LAPACK/MAGMA function that will be used.
            Possible values: for CPU 'gels', 'gelsy', 'gelsd', 'gelss'.
                             for GPU  the only valid driver is 'gels',
                             which assumes that A is full-rank
            see https://pytorch.org/docs/stable/generated/torch.linalg.lstsq.html
            for a full description
            If None, 'gelsy' is used for CPU inputs
            and 'gels' for CUDA inputs. Default: None
    """
    if isinstance(X, TorchTensor):
        _check_all_torch_tensor([Y])
        return torch.linalg.lstsq(X, Y, rcond=rcond, driver=driver)[0]
    elif isinstance(X, np.ndarray):
        _check_all_np_ndarray([Y])
        return np.linalg.lstsq(X, Y, rcond=rcond)[0]
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def nan_to_num(
    X, nan: float = 0.0, posinf: Optional[float] = None, neginf: Optional[float] = None
):
    """Equivalent to np.nan_to_num(X, nan, posinf, neginf)"""
    if isinstance(X, TorchTensor):
        return torch.nan_to_num(X, nan=nan, posinf=posinf, neginf=neginf)
    elif isinstance(X, np.ndarray):
        return np.nan_to_num(X, nan=nan, posinf=posinf, neginf=neginf)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def concatenate(arrays: List[TorchTensor], axis: int):
    """
    Concatenate a group of arrays along a given axis.

    This function has the same behavior as ``numpy.concatenate(arrays, axis)``
    and ``torch.concatenate(arrays, axis)``.

    Passing `axis` as ``0`` is equivalent to :py:func:`numpy.vstack`, ``1`` to
    :py:func:`numpy.hstack`, and ``2`` to :py:func:`numpy.dstack`, though any
    axis index > 0 is valid.
    """
    if isinstance(arrays[0], TorchTensor):
        _check_all_torch_tensor(arrays)
        return torch.concatenate(arrays, axis)
    elif isinstance(arrays[0], np.ndarray):
        _check_all_np_ndarray(arrays)
        return np.concatenate(arrays, axis)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def index_add(output_array, input_array, index):
    """Accumulates in `output_array`
    the elements of `array`
    by adding to the indices in the order given in index.

    it is equivalent of torch's:

    output_array.index_add_(0, torch.tensor(index),input_array)

    """
    index = to_index_array(index)
    if isinstance(input_array, TorchTensor):
        _check_all_torch_tensor([output_array, input_array, index])
        output_array.index_add_(0, index, input_array)
    elif isinstance(input_array, np.ndarray):
        _check_all_np_ndarray([output_array, input_array, index])
        np.add.at(output_array, index, input_array)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def zeros_like(array, shape: Optional[List[int]] = None, requires_grad: bool = False):
    """
    Create an array filled with zeros, with the given ``shape``, and similar
    dtype, device and other options as ``array``.

    If ``shape`` is :py:obj:`None`, the array shape is used instead.
    ``requires_grad`` is only used for torch tensors, and set the corresponding
    value on the returned array.

    This is the equivalent to ``np.zeros_like(array, shape=shape)``.
    """
    if isinstance(array, TorchTensor):
        if shape is None:
            shape = array.size()

        return torch.zeros(
            shape,
            dtype=array.dtype,
            layout=array.layout,
            device=array.device,
        ).requires_grad_(requires_grad)
    elif isinstance(array, np.ndarray):
        return np.zeros_like(array, shape=shape, subok=False)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def ones_like(array, shape: Optional[List[int]] = None, requires_grad: bool = False):
    """
    Create an array filled with ones, with the given ``shape``, and similar
    dtype, device and other options as ``array``.

    If ``shape`` is :py:obj:`None`, the array shape is used instead.
    ``requires_grad`` is only used for torch tensors, and set the corresponding
    value on the returned array.

    This is the equivalent to ``np.ones_like(array, shape=shape)``.
    """

    if isinstance(array, TorchTensor):
        if shape is None:
            shape = array.size()
        return torch.ones(
            shape,
            dtype=array.dtype,
            layout=array.layout,
            device=array.device,
        ).requires_grad_(requires_grad)
    elif isinstance(array, np.ndarray):
        return np.ones_like(array, shape=shape, subok=False)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def empty_like(array, shape: Optional[List[int]] = None, requires_grad: bool = False):
    """
    Create an uninitialized array, with the given ``shape``, and similar dtype,
    device and other options as ``array``.

    If ``shape`` is :py:obj:`None`, the array shape is used instead.
    ``requires_grad`` is only used for torch tensors, and set the corresponding
    value on the returned array.

    This is the equivalent to ``np.empty_like(array, shape=shape)``.
    """
    if isinstance(array, TorchTensor):
        if shape is None:
            shape = array.size()
        return torch.empty(
            shape,
            dtype=array.dtype,
            layout=array.layout,
            device=array.device,
        ).requires_grad_(requires_grad)
    elif isinstance(array, np.ndarray):
        return np.empty_like(array, shape=shape, subok=False)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def abs(array):
    """
    Returns the absolute value of the elements in the array.

    It is equivalent of np.abs(array) and torch.abs(tensor)
    """
    if isinstance(array, TorchTensor):
        return torch.abs(array)
    elif isinstance(array, np.ndarray):
        return np.abs(array)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def sign(array):
    """
    Returns an indication of the sign of the elements in the array.

    It is equivalent of np.sign(array) and torch.sign(tensor)
    """
    if isinstance(array, TorchTensor):
        return torch.sign(array)
    elif isinstance(array, np.ndarray):
        return np.sign(array)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def rand_like(array, shape: Optional[List[int]] = None, requires_grad: bool = False):
    """
    Create an array with values randomly sampled from the uniform distribution
    in the ``[0, 1)`` interval, with the given ``shape``, and similar dtype,
    device and other options as ``array``.

    If ``shape`` is :py:obj:`None`, the array shape is used instead.
    ``requires_grad`` is only used for torch tensors, and set the corresponding
    value on the returned array.
    """

    if isinstance(array, TorchTensor):
        if shape is None:
            shape = array.shape
        return torch.rand(
            shape,
            dtype=array.dtype,
            layout=array.layout,
            device=array.device,
        ).requires_grad_(requires_grad)
    elif isinstance(array, np.ndarray):
        if shape is None:
            shape = array.shape
        return np.random.rand(*shape).astype(array.dtype)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def to(
    array,
    backend: Optional[str] = None,
    dtype: Optional[torch.dtype] = None,
    device: Optional[Union[str, torch.device]] = None,
    requires_grad: Optional[bool] = None,
):
    """Convert the array to the specified backend."""

    # Convert torch Tensor
    if isinstance(array, torch.Tensor):
        if backend is None:  # Infer the target backend
            backend = "torch"
        if dtype is None:
            dtype = array.dtype
        if device is None:
            device = array.device
        if isinstance(device, str):
            device = torch.device(device)

        # Perform the conversion
        if backend == "torch":
            # We need this to keep gradients of the tensor
            new_array = array.to(dtype=dtype).to(device=device)
            if requires_grad is not None:
                new_array.requires_grad_(requires_grad)
            return new_array

        elif backend == "numpy":
            if torch_jit_is_scripting():
                raise ValueError("cannot call numpy conversion when torch-scripting")
            else:
                return array.detach().cpu().numpy()

        else:
            raise ValueError(f"Unknown backend: {backend}")

    # Convert numpy array
    elif isinstance(array, np.ndarray):
        if backend is None:  # Infer the target backend
            backend = "numpy"

        # Perform the conversion
        if backend == "numpy":
            return np.array(array, dtype=dtype)

        elif backend == "torch":
            # If requires_grad is None, it is set to False by torch here
            new_array = torch.tensor(array, dtype=dtype, device=device)
            if requires_grad is not None:
                new_array.requires_grad = requires_grad
            return new_array
        else:
            raise ValueError(f"Unknown backend: {backend}")

    else:
        # Only numpy and torch arrays currently supported
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def to_index_array(array):
    """Returns an array that is suitable for indexing a dimension of
    a different array.

    After a few checks (int, 1D), this operation will convert the dtype to
    torch.long (which is, in some torch versions, the only acceptable type
    of index tensor). Numpy arrays are left unchanged.
    """
    if len(array.shape) != 1:
        raise ValueError("Index arrays must be 1D")

    if isinstance(array, TorchTensor):
        if torch.is_floating_point(array):
            raise ValueError("Index arrays must be integers")
        return array.to(torch.long)
    elif isinstance(array, np.ndarray):
        if not np.issubdtype(array.dtype, np.integer):
            raise ValueError("Index arrays must be integers")
        return array
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def unique(array, axis: Optional[int] = None):
    """Find the unique elements of an array."""
    if isinstance(array, TorchTensor):
        return torch.unique(array, dim=axis)
    elif isinstance(array, np.ndarray):
        return np.unique(array, axis=axis)


def unique_with_inverse(array, axis: Optional[int] = None):
    """Return the unique entries of `array`, along with inverse indices.

    Specifying return_inverse=True explicitly seems to be necessary, as
    there is apparently no way to mark something as a compile-time constant
    in torchscript.
    """
    if isinstance(array, TorchTensor):
        return torch.unique(array, return_inverse=True, dim=axis)
    elif isinstance(array, np.ndarray):
        return np.unique(array, return_inverse=True, axis=axis)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)


def where(array):
    """Return the indices where `array` is True.

    This function has the same behavior as
    ``np.where(array)``.
    """
    if isinstance(array, TorchTensor):
        return torch.where(array)
    elif isinstance(array, np.ndarray):
        return np.where(array)
    else:
        raise TypeError(UNKNOWN_ARRAY_TYPE)
