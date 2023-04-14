import numpy as np

from equistore.core import TensorBlock, TensorMap

from . import _dispatch
from ._utils import _check_blocks, _check_same_gradients, _check_same_keys
from .equal import NotEqualError


def allclose(
    tensor_1: TensorMap,
    tensor_2: TensorMap,
    rtol=1e-13,
    atol=1e-12,
    equal_nan=False,
) -> bool:
    """
    Compare two :py:class:`TensorMap`.

    This function returns :py:obj:`True` if the two tensors have the same keys
    (potentially in different order) and all the :py:class:`TensorBlock` have
    the same (and in the same order) samples, components, properties, and their
    values matrices pass the numpy-like ``allclose`` test with the provided
    ``rtol``, and ``atol``.

    The :py:class:`TensorMap` contains gradient data, then this function only
    returns :py:obj:`True` if all the gradients also have the same samples,
    components, properties and their data matrices pass the numpy-like
    ``allclose`` test with the provided ``rtol``, and ``atol``.

    In practice this function calls :py:func:`allclose_raise`, returning
    :py:obj:`True` if no exception is raised, :py:obj:`False` otherwise.

    :param tensor_1: first :py:class:`TensorMap`
    :param tensor_2: second :py:class:`TensorMap`
    :param rtol: relative tolerance for ``allclose``
    :param atol: absolute tolerance for ``allclose``
    :param equal_nan: should two ``NaN`` be considered equal?


    >>> from equistore import Labels
    >>> # Create simple block
    >>> block_1 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["properties"], np.array([[0], [1], [2]])),
    ... )
    >>> # Create a second block that is equivalent to block_1
    >>> block_2 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["properties"], np.array([[0], [1], [2]])),
    ... )
    >>> # Create tensors from blocks, using keys with different names
    >>> keys1 = Labels(names=["key1"], values=np.array([[0]]))
    >>> keys2 = Labels(names=["key2"], values=np.array([[0]]))
    >>> tensor_1 = TensorMap(keys1, [block_1])
    >>> tensor_2 = TensorMap(keys2, [block_2])
    >>> # Call allclose, which should fail as the blocks have different keys
    >>> # associated with them
    >>> allclose(tensor_1, tensor_2)
    False
    >>> # Create a third tensor, which differs from tensor_1 only by 1e-5 in a
    >>> # single block value
    >>> block3 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1 + 1e-5, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["properties"], np.array([[0], [1], [2]])),
    ... )
    >>> # Create tensors from blocks, using key with same name as block_1
    >>> keys3 = Labels(names=["key1"], values=np.array([[0]]))
    >>> tensor3 = TensorMap(keys3, [block3])
    >>> # Call allclose, which should return False because the default rtol
    >>> # is 1e-13, and the difference in the first value between the blocks
    >>> # of the two tensors is 1e-5
    >>> allclose(tensor_1, tensor3)
    False
    >>> # Calling allclose again with the optional argument rtol=1e-5 should
    >>> # return True, as the difference in the first value between the blocks
    >>> # of the two tensors is within the tolerance limit
    >>> allclose(tensor_1, tensor3, rtol=1e-5)
    True
    """
    try:
        allclose_raise(
            tensor_1=tensor_1,
            tensor_2=tensor_2,
            rtol=rtol,
            atol=atol,
            equal_nan=equal_nan,
        )
        return True
    except NotEqualError:
        return False


def allclose_raise(
    tensor_1: TensorMap,
    tensor_2: TensorMap,
    rtol=1e-13,
    atol=1e-12,
    equal_nan=False,
):
    """
    Compare two :py:class:`TensorMap`, raising :py:class:`NotEqualError` if they
    are not the same.

    The message associated with the exception will contain more information on
    where the two :py:class:`TensorMap` differ. See :py:func:`allclose` for more
    information on which :py:class:`TensorMap` are considered equal.

    :raises: :py:class:`NotEqualError` if the blocks are different

    :param tensor_1: first :py:class:`TensorMap`
    :param tensor_2: second :py:class:`TensorMap`
    :param rtol: relative tolerance for ``allclose``
    :param atol: absolute tolerance for ``allclose``
    :param equal_nan: should two ``NaN`` be considered equal?

    >>> import equistore
    >>> from equistore import Labels
    >>> # Create simple block, with one np.nan value
    >>> block_1 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, np.nan],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["properties"], np.array([[0], [1], [2]])),
    ... )
    >>> # Create a second block that differs from block_1 by 1e-5 in its
    >>> # first value
    >>> block_2 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1 + 1e-5, 2, 4],
    ...             [3, 5, np.nan],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["properties"], np.array([[0], [1], [2]])),
    ... )
    >>> # Create tensors from blocks, using same keys
    >>> keys = Labels(names=["key"], values=np.array([[0]]))
    >>> tensor_1 = TensorMap(keys, [block_1])
    >>> tensor_2 = TensorMap(keys, [block_2])
    >>> # Call allclose_raise, which should raise NotEqualError because:
    >>> # 1. The two NaNs are not considered equal,
    >>> # 2. The difference between the first value in the blocks
    >>> # is greater than the default rtol of 1e-13
    >>> # If this is executed yourself, you will see a nested exception
    >>> # explaining that the values of the two blocks are not allclose
    >>> try:
    ...     allclose_raise(tensor_1, tensor_2)
    ... except equistore.NotEqualError as e:
    ...     print(f"got an exception: {e}")
    ...
    got an exception: blocks for key '(0,)' are different
    >>> # call allclose_raise again, but use equal_nan=True and rtol=1e-5
    >>> # This passes, as the two NaNs are now considered equal, and the
    >>> # difference between the first values of the blocks of the two tensors
    >>> # is within the rtol limit of 1e-5
    >>> allclose_raise(tensor_1, tensor_2, equal_nan=True, rtol=1e-5)
    """
    try:
        _check_same_keys(tensor_1, tensor_2, "allclose")
    except NotEqualError as e:
        raise NotEqualError("the tensor maps have different keys") from e

    for key, block_1 in tensor_1:
        try:
            allclose_block_raise(
                block_1,
                tensor_2.block(key),
                rtol=rtol,
                atol=atol,
                equal_nan=equal_nan,
            )
        except NotEqualError as e:
            raise NotEqualError(f"blocks for key '{key}' are different") from e


def allclose_block(
    block_1: TensorBlock,
    block_2: TensorBlock,
    rtol=1e-13,
    atol=1e-12,
    equal_nan=False,
) -> bool:
    """
    Compare two :py:class:`TensorBlock`.

    This function returns :py:obj:`True` if the two :py:class:`TensorBlock` have the
    same samples, components, properties and their values matrices must pass the
    numpy-like ``allclose`` test with the provided ``rtol``, and ``atol``.

    If the :py:class:`TensorBlock` contains gradients, then the gradient must
    also have same (and in the same order) samples, components, properties
    and their data matrices must pass the numpy-like ``allclose`` test with the
    provided ``rtol``, and ``atol``.

    In practice this function calls :py:func:`allclose_block_raise`, returning
    :py:obj:`True` if no exception is raised, :py:obj:`False` otherwise.

    :param block_1: first :py:class:`TensorBlock`
    :param block_2: second :py:class:`TensorBlock`
    :param rtol: relative tolerance for ``allclose``
    :param atol: absolute tolerance for ``allclose``
    :param equal_nan: should two ``NaN`` be considered equal?


    >>> from equistore import Labels
    >>> # Create simple block
    >>> block_1 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["property_1"], np.array([[0], [1], [2]])),
    ... )
    >>> # Recreate block_1, but change first value in the block from 1 to 1.00001
    >>> block_2 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1 + 1e-5, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["property_1"], np.array([[0], [1], [2]])),
    ... )
    >>> # Call allclose_block, which should return False because the default
    >>> # rtol is 1e-13, and the difference in the first value between the
    >>> # two blocks is 1e-5
    >>> allclose_block(block_1, block_2)
    False
    >>> # Calling allclose_block with the optional argument rtol=1e-5 should
    >>> # return True, as the difference in the first value between the two
    >>> # blocks is within the tolerance limit
    >>> allclose_block(block_1, block_2, rtol=1e-5)
    True
    """
    try:
        allclose_block_raise(
            block_1=block_1,
            block_2=block_2,
            rtol=rtol,
            atol=atol,
            equal_nan=equal_nan,
        )
        return True
    except NotEqualError:
        return False


def allclose_block_raise(
    block_1: TensorBlock,
    block_2: TensorBlock,
    rtol=1e-13,
    atol=1e-12,
    equal_nan=False,
):
    """
    Compare two :py:class:`TensorBlock`, raising :py:class:`NotEqualError` if
    they are not the same.

    The message associated with the exception will contain more information on
    where the two :py:class:`TensorBlock` differ. See :py:func:`allclose_block`
    for more information on which :py:class:`TensorBlock` are considered equal.

    :raises: :py:class:`NotEqualError` if the blocks are different

    :param block_1: first :py:class:`TensorBlock`
    :param block_2: second :py:class:`TensorBlock`
    :param rtol: relative tolerance for ``allclose``
    :param atol: absolute tolerance for ``allclose``
    :param equal_nan: should two ``NaN`` be considered equal?

    >>> import equistore
    >>> from equistore import Labels
    >>> # Create simple block
    >>> block_1 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["property_1"], np.array([[0], [1], [2]])),
    ... )
    >>> # Recreate block_1, but rename properties label 'property_1' to 'property_2'
    >>> block_2 = TensorBlock(
    ...     values=np.array(
    ...         [
    ...             [1, 2, 4],
    ...             [3, 5, 6],
    ...         ]
    ...     ),
    ...     samples=Labels(
    ...         ["structure", "center"],
    ...         np.array(
    ...             [
    ...                 [0, 0],
    ...                 [0, 1],
    ...             ]
    ...         ),
    ...     ),
    ...     components=[],
    ...     properties=Labels(["property_2"], np.array([[0], [1], [2]])),
    ... )
    >>> # Call allclose_block_raise, which should raise NotEqualError because the
    >>> # properties of the two blocks are not equal
    >>> try:
    ...     allclose_block_raise(block_1, block_2)
    ... except equistore.NotEqualError as e:
    ...     print(f"got an exception: {e}")
    ...
    got an exception: inputs to 'allclose' should have the same properties:
    properties names are not the same or not in the same order
    """

    if not np.all(block_1.values.shape == block_2.values.shape):
        raise NotEqualError("values shapes are different")

    if not _dispatch.allclose(
        block_1.values,
        block_2.values,
        rtol=rtol,
        atol=atol,
        equal_nan=equal_nan,
    ):
        raise NotEqualError("values are not allclose")

    try:
        _check_blocks(
            block_1,
            block_2,
            props=["samples", "properties", "components"],
            fname="allclose",
        )
    except ValueError as e:
        raise NotEqualError(str(e))

    _check_same_gradients(
        block_1,
        block_2,
        props=["samples", "properties", "components"],
        fname="allclose",
    )

    for parameter, gradient1 in block_1.gradients():
        gradient2 = block_2.gradient(parameter)

        if not _dispatch.allclose(
            gradient1.values,
            gradient2.values,
            rtol=rtol,
            atol=atol,
            equal_nan=equal_nan,
        ):
            raise NotEqualError(f"gradient '{parameter}' values are not allclose")