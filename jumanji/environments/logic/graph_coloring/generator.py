# Copyright 2022 InstaDeep Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
from typing import Optional

import chex
import jax
from jax import numpy as jnp


class Generator(abc.ABC):
    @property
    @abc.abstractmethod
    def num_nodes(self) -> int:
        """Number of nodes of the problem instances generated.
        Returns:
            `num_nodes` of the generated instances.
        """

    @abc.abstractmethod
    def __call__(self, key: chex.PRNGKey) -> chex.Array:
        """Generate a problem instance.

        Args:
            key: random key.

        Returns:
            An `adj_matrix` representing a problem instance.
        """


class RandomGenerator(Generator):
    """A generator for random graphs in the context of GraphColoring problems,
    based on the Erdős-Rényi model (G(n, p)).

    The adjacency matrix is generated such that the graph is undirected and loop-less.
    The graph is generated with a specified number of nodes and percentage of connectivity,
    which is used as a proxy for the edge probability in the Erdős-Rényi model.
    """

    def __init__(
        self, num_nodes: Optional[int] = None, percent_connected: Optional[float] = None
    ):
        """
        Initialize the RandomGraphColoringGenerator.

        Args:
            num_nodes: The number of nodes in the graph. The number of colors available for
                coloring is equal to the number of nodes. This means that the graph is always
                colorable with the given colors.
                The default value of `num_nodes` is 100.
            percent_connected: A float between 0 and 1 representing the percentage of connections
                in the graph compared to a fully connected graph.
                The default value of `percent_connected` is 0.8.
        """

        self._num_nodes = num_nodes or 100
        self.percent_connected = percent_connected or 0.8
        assert (
            0 < self.percent_connected < 1
        ), f"percent_connected={self.percent_connected} must be between 0 and 1."

    @property
    def num_nodes(self) -> int:
        return self._num_nodes

    def __repr__(self) -> str:
        """Returns: str: the string representation of the environment generator."""
        return (
            f"GraphColoring(number of nodes={self.num_nodes}, "
            f"percent connected={self.percent_connected * 100}% "
        )

    def __call__(self, key: chex.PRNGKey) -> chex.Array:
        """Generate a random graph adjacency matrix representing
        the edges of an undirected graph using the Erdős-Rényi model G(n, p).
        Args:
            key: A Chex PRNGKey used for random number generation.
        Returns:
            adj_matrix: A boolean array of shape (num_nodes, num_nodes) representing
                the adjacency matrix of the graph, where adj_matrix[i, j] is True if
                there is an edge between nodes i and j, and False otherwise.
        """
        key, edge_key = jax.random.split(key)

        # Generate a random adjacency matrix with probabilities of connections.
        p_matrix = jax.random.uniform(
            key=edge_key, shape=(self.num_nodes, self.num_nodes)
        )

        # Threshold the probabilities to create a boolean adjacency matrix.
        adj_matrix = p_matrix < self.percent_connected

        # Make sure the graph is undirected (symmetric) and without self-loops.
        adj_matrix = jnp.tril(adj_matrix, k=-1)  # Keep only the lower triangular part.
        # Copy the lower triangular part to the upper triangular part.
        adj_matrix += adj_matrix.T

        return adj_matrix
