import os

import numpy as np
import pytest

import equistore
from equistore import Labels, NotEqualError, TensorBlock, TensorMap


DATA_ROOT = os.path.join(os.path.dirname(__file__), "data")


def test_equal_no_gradient():
    block_1 = TensorBlock(
        values=np.array([[1, 2], [3, 5]], dtype=np.float64),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels.arange("p", 2),
    )
    block_2 = TensorBlock(
        values=np.array([[1, 2], [3, 4], [5, 6], [1, 2], [3, 4], [5, 6]]),
        samples=Labels.arange("s", 6),
        components=[],
        properties=Labels.arange("p", 2),
    )

    block_3 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_4 = TensorBlock(
        values=np.array([[23], [53], [83]]),
        samples=Labels(["s"], np.array([[0], [2], [7]])),
        components=[],
        properties=Labels(["p"], np.array([[6]])),
    )
    keys = Labels(names=["key_1", "key_2"], values=np.array([[0, 0], [1, 0]]))
    X = TensorMap(keys, [block_1, block_2])
    assert equistore.equal(X, X)

    Y = TensorMap(keys, [block_3, block_4])
    assert not equistore.equal(X, Y)

    message = r"blocks for key '\(0, 0\)' are different"
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_raise(X, Y)

    block_1_c = TensorBlock(
        values=np.array(
            [
                [
                    [[1, 0.5], [4, 2], [1.5, 6.5]],
                    [[2, 1], [6, 3], [6.1, 3.5]],
                    [[9, 9], [9, 9.8], [10, 10.5]],
                ],
                [
                    [[3, 1.5], [7, 3.5], [3.7, 1.5]],
                    [[5, 2.5], [8, 4], [6.3, 1.5]],
                    [[5, 7.1], [8, 4.8], [6.3, 14.466]],
                ],
            ],
            dtype=np.float64,
        ),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[
            Labels.arange("c1", 3),
            Labels.arange("c2", 3),
        ],
        properties=Labels.arange("p", 2),
    )
    block_1_c_copy = TensorBlock(
        values=block_1_c.values + 0.1e-6,
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[
            Labels.arange("c1", 3),
            Labels.arange("c2", 3),
        ],
        properties=Labels.arange("p", 2),
    )

    block_2_c = TensorBlock(
        values=np.array(
            [
                [[[1, 2], [6.8, 2.8]], [[4.1, 6.2], [66.8, 62.8]]],
                [[[3, 4], [36, 6.4]], [[83, 84], [73.76, 76.74]]],
                [[[5, 6], [58, 68]], [[23.4, 5643.3], [234.5, 3247.6]]],
                [[[5.6, 6.6], [5.68, 668]], [[55.6, 676.76], [775.68, 0.668]]],
                [[[1, 2], [17.7, 27.7]], [[77.1, 22.2], [1.11, 3.42]]],
            ]
        ),
        samples=Labels.arange("s", 5),
        components=[
            Labels(["c1"], np.array([[3], [5]])),
            Labels(["c2"], np.array([[6], [8]])),
        ],
        properties=Labels.arange("p", 2),
    )
    block_2_c_copy = TensorBlock(
        values=block_2_c.values + 0.1e-6,
        samples=Labels.arange("s", 5),
        components=[
            Labels(["c1"], np.array([[3], [5]])),
            Labels(["c2"], np.array([[6], [8]])),
        ],
        properties=Labels.arange("p", 2),
    )
    X_c = TensorMap(keys, [block_1_c, block_2_c])
    X_c_copy = TensorMap(keys, [block_1_c_copy, block_2_c_copy])
    assert not equistore.equal(X, X_c)

    assert equistore.equal(X_c, X_c)
    assert not equistore.equal(X_c, X_c_copy)


def test_self_equal_grad():
    tensor1 = equistore.load(
        os.path.join(DATA_ROOT, "qm7-spherical-expansion.npz"),
        use_numpy=True,
    )
    blocks = []
    blocks_e6 = []
    for _, block in tensor1:
        blocks.append(block.copy())
        be6 = block.copy()
        be6.values[:] += 1e-6
        blocks_e6.append(be6)

    tensor1_copy = TensorMap(tensor1.keys, blocks)
    tensor1_e6 = TensorMap(tensor1.keys, blocks_e6)
    assert equistore.equal(tensor1, tensor1_copy)
    assert not equistore.equal(tensor1, tensor1_e6)

    message = r"blocks for key '\(0, 1, 1\)' are different"
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_raise(tensor1, tensor1_e6)

    with pytest.raises(NotEqualError, match="values are not equal"):
        equistore.equal_block_raise(tensor1.block(0), tensor1_e6.block(0))


def test_self_equal_exceptions():
    block_1 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_2 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["other_s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_3 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [6]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_4 = TensorBlock(
        values=np.array([[[1], [4]], [[44], [2]]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[
            Labels(["c"], np.array([[0], [6]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_5 = TensorBlock(
        values=np.array([[[1], [4]], [[44], [2]]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[
            Labels(["other_c"], np.array([[0], [6]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_6 = TensorBlock(
        values=np.array([[[1], [4]], [[44], [2]]]),
        samples=Labels(["s"], np.array([[2], [0]])),
        components=[
            Labels(["c"], np.array([[0], [6]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )

    assert not equistore.equal_block(block_1, block_2)

    message = (
        "inputs to 'equal' should have the same samples:\n"
        "samples names are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_1, block_2)

    message = (
        "inputs to 'equal' should have the same samples:\n"
        "samples are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_1, block_3)

    with pytest.raises(NotEqualError, match="values shapes are different"):
        equistore.equal_block_raise(block_1, block_4)

    message = (
        "inputs to 'equal' should have the same components:\n"
        "components names are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_5, block_4)

    message = (
        "inputs to 'equal' should have the same samples:\n"
        "samples are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_6, block_4)

    block_7 = TensorBlock(
        values=np.ones((2, 2, 4, 1)),
        samples=Labels(["s"], np.array([[2], [0]])),
        components=[
            Labels(["c_1"], np.array([[0], [6]])),
            Labels(["c_2"], np.array([[0], [1], [2], [7]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_8 = TensorBlock(
        values=np.ones((2, 2, 4, 1)),
        samples=Labels(["s"], np.array([[2], [0]])),
        components=[
            Labels(["c_1"], np.array([[0], [6]])),
            Labels(["c_2"], np.array([[0], [8], [6], [7]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )
    block_9 = TensorBlock(
        values=np.ones((2, 2, 4, 1)) * 3,
        samples=Labels(["s"], np.array([[2], [0]])),
        components=[
            Labels(["c_1"], np.array([[0], [6]])),
            Labels(["c_2"], np.array([[0], [8], [6], [7]])),
        ],
        properties=Labels(["p"], np.array([[0]])),
    )

    assert not equistore.equal_block(block_7, block_8)

    assert not equistore.equal_block(block_8, block_9)

    message = (
        "inputs to 'equal' should have the same components:\n"
        "components are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_7, block_8)

    with pytest.raises(NotEqualError, match="values are not equal"):
        equistore.equal_block_raise(block_8, block_9)


def test_self_equal_exceptions_gradient():
    block_1 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_1.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 1), 11.0),
            samples=Labels(["sample", "g"], np.array([[0, -2], [2, 3]])),
            components=[],
            properties=block_1.properties,
        ),
    )

    block_2 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_2.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 1), 11.0),
            samples=Labels(["sample", "other_g"], np.array([[0, -2], [2, 3]])),
            components=[],
            properties=block_2.properties,
        ),
    )

    message = (
        "inputs to equal should have the same gradients:\n"
        "gradient 'g' samples names are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_1, block_2)

    block_3 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_3.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 1), 1.0),
            samples=Labels(["sample", "g"], np.array([[0, -2], [2, 3]])),
            components=[],
            properties=block_3.properties,
        ),
    )

    with pytest.raises(NotEqualError, match="gradient 'g' values are not equal"):
        equistore.equal_block_raise(block_1, block_3)

    block_4 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_4.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 3, 1), 1.0),
            samples=Labels(["sample", "g"], np.array([[0, -2], [2, 3]])),
            components=[Labels.arange("c_1", -1, 2)],
            properties=block_4.properties,
        ),
    )

    block_5 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_5.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 3, 1), 1.0),
            samples=Labels(["sample", "g"], np.array([[0, -2], [2, 3]])),
            components=[Labels(["c_1"], np.array([[-1], [6], [1]]))],
            properties=block_5.properties,
        ),
    )

    message = (
        "inputs to equal should have the same gradients:\n"
        "gradient 'g' components are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_5, block_4)

    block_6 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_6.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 3, 1), 1.0),
            samples=Labels(["sample", "other_g"], np.array([[0, -2], [2, 3]])),
            components=[Labels(["c_1"], np.array([[-1], [6], [1]]))],
            properties=block_6.properties,
        ),
    )

    message = (
        "inputs to equal should have the same gradients:\n"
        "gradient 'g' samples names are not the same or not in the same order"
    )
    with pytest.raises(NotEqualError, match=message):
        equistore.equal_block_raise(block_5, block_6)

    block_7 = TensorBlock(
        values=np.array([[1], [2]]),
        samples=Labels(["s"], np.array([[0], [2]])),
        components=[],
        properties=Labels(["p"], np.array([[0]])),
    )

    block_7.add_gradient(
        parameter="g",
        gradient=TensorBlock(
            values=np.full((2, 3, 1), 5.0),
            samples=Labels(["sample", "other_g"], np.array([[0, -2], [2, 3]])),
            components=[Labels(["c_1"], np.array([[-1], [6], [1]]))],
            properties=block_7.properties,
        ),
    )
    assert not equistore.equal_block(block_6, block_7)

    with pytest.raises(NotEqualError, match="gradient 'g' values are not equal"):
        equistore.equal_block_raise(block_6, block_7)


# TODO: add tests with torch & torch scripting/tracing