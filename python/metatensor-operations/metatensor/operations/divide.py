from typing import List, Union

from . import _dispatch
from ._classes import TensorBlock, TensorMap, check_isinstance, torch_jit_is_scripting
from ._utils import (
    _check_blocks_raise,
    _check_same_gradients_raise,
    _check_same_keys_raise,
)


def divide(A: TensorMap, B: Union[float, int, TensorMap]) -> TensorMap:
    r"""Return a new :class:`TensorMap` with the values being the element-wise
    division of ``A`` and ``B``.

    If ``B`` is a :py:class:`TensorMap` it has to have the same metadata as ``A``.

    If gradients are present in ``A``:

    *  ``B`` is a scalar then:

       .. math::
            \nabla(A / B) =  \nabla A / B

    *  ``B`` is a :py:class:`TensorMap` with the same metadata of ``A``.
        The multiplication is performed with the rule of the derivatives:

       .. math::
            \nabla(A / B) =(B*\nabla A-A*\nabla B)/B^2

    :param A: First :py:class:`TensorMap` for the division.
    :param B: Second instance for the division. Parameter can be a scalar
            or a :py:class:`TensorMap`. In the latter case ``B`` must have the same
            metadata of ``A``.

    :return: New :py:class:`TensorMap` with the same metadata as ``A``.
    """

    blocks: List[TensorBlock] = []
    if torch_jit_is_scripting():
        is_tensor_map = isinstance(B, TensorMap)
    else:
        is_tensor_map = check_isinstance(B, TensorMap)

    if isinstance(B, (float, int)):
        B = float(B)
        for block_A in A.blocks():
            blocks.append(_divide_block_constant(block=block_A, constant=B))
    elif is_tensor_map:
        _check_same_keys_raise(A, B, "divide")
        for key, block_A in A.items():
            block_B = B.block(key)
            _check_blocks_raise(
                block_A,
                block_B,
                fname="divide",
            )
            _check_same_gradients_raise(
                block_A,
                block_B,
                fname="divide",
            )
            blocks.append(_divide_block_block(block_1=block_A, block_2=block_B))
    else:
        raise TypeError("B should be a TensorMap or a scalar value")

    return TensorMap(A.keys, blocks)


def _divide_block_constant(block: TensorBlock, constant: float) -> TensorBlock:
    values = block.values / constant

    result_block = TensorBlock(
        values=values,
        samples=block.samples,
        components=block.components,
        properties=block.properties,
    )

    for parameter, gradient in block.gradients():
        if len(gradient.gradients_list()) != 0:
            raise NotImplementedError("gradients of gradients are not supported")

        result_block.add_gradient(
            parameter=parameter,
            gradient=TensorBlock(
                values=gradient.values / constant,
                samples=gradient.samples,
                components=gradient.components,
                properties=gradient.properties,
            ),
        )

    return result_block


def _divide_block_block(block_1: TensorBlock, block_2: TensorBlock) -> TensorBlock:
    values = block_1.values / block_2.values

    result_block = TensorBlock(
        values=values,
        samples=block_1.samples,
        components=block_1.components,
        properties=block_1.properties,
    )

    for parameter_1, gradient_1 in block_1.gradients():
        gradient_2 = block_2.gradient(parameter_1)

        if len(gradient_1.gradients_list()) != 0:
            raise NotImplementedError("gradients of gradients are not supported")

        if len(gradient_2.gradients_list()) != 0:
            raise NotImplementedError("gradients of gradients are not supported")

        values_grad = []
        for i_sample in range(len(block_1.samples)):
            i_sample_grad_1 = _dispatch.where(
                gradient_1.samples.column("sample") == i_sample
            )[0]
            i_sample_grad_2 = _dispatch.where(
                gradient_2.samples.column("sample") == i_sample
            )[0]

            value_grad = (
                -block_1.values[i_sample]
                * gradient_2.values[i_sample_grad_2]
                / block_2.values[i_sample] ** 2
            )
            value_grad += gradient_1.values[i_sample_grad_1] / block_2.values[i_sample]
            values_grad.append(value_grad)

        values_grad = _dispatch.concatenate(values_grad, axis=0)

        result_block.add_gradient(
            parameter=parameter_1,
            gradient=TensorBlock(
                values=values_grad,
                samples=gradient_1.samples,
                components=gradient_1.components,
                properties=gradient_1.properties,
            ),
        )

    return result_block