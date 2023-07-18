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

import chex
import jax
import jax.numpy as jnp

from jumanji.environments.logic.sliding_tile_puzzle import SlidingTilePuzzle
from jumanji.environments.logic.sliding_tile_puzzle.types import State
from jumanji.testing.env_not_smoke import check_env_does_not_smoke
from jumanji.testing.pytrees import assert_is_jax_array_tree
from jumanji.types import TimeStep


def test_sliding_tile_puzzle_reset_jit(sliding_tile_puzzle: SlidingTilePuzzle) -> None:
    """Confirm that the reset method is only compiled once when jitted."""
    chex.clear_trace_counter()
    reset_fn = jax.jit(chex.assert_max_traces(sliding_tile_puzzle.reset, n=1))
    key = jax.random.PRNGKey(0)
    state, timestep = reset_fn(key)

    # Verify the data type of the output.
    assert isinstance(timestep, TimeStep)
    assert isinstance(state, State)

    # Check that the state is made of DeviceArrays, this is false for the non-jitted.
    assert_is_jax_array_tree(state.puzzle)
    assert_is_jax_array_tree(state.empty_tile_position)

    # Call again to check it does not compile twice.
    state, timestep = reset_fn(key)
    assert isinstance(timestep, TimeStep)
    assert isinstance(state, State)


def test_sliding_tile_puzzle_step_jit(sliding_tile_puzzle: SlidingTilePuzzle) -> None:
    """Confirm that the step is only compiled once when jitted."""
    key = jax.random.PRNGKey(0)
    state, timestep = jax.jit(sliding_tile_puzzle.reset)(key)
    action = jnp.array(0)

    chex.clear_trace_counter()
    step_fn = jax.jit(chex.assert_max_traces(sliding_tile_puzzle.step, n=1))

    new_state, next_timestep = step_fn(state, action)

    # Check that the state has changed.
    assert not jnp.array_equal(new_state.puzzle, state.puzzle)

    # Check that the state is made of DeviceArrays, this is false for the non-jitted.
    assert_is_jax_array_tree(new_state)

    # New step
    state = new_state
    new_state, next_timestep = step_fn(state, action)

    # Check that the state has changed
    assert not jnp.array_equal(new_state.puzzle, state.puzzle)


def test_sliding_tile_puzzle_get_action_mask(
    sliding_tile_puzzle: SlidingTilePuzzle,
) -> None:
    """Verify that the action mask generated by `_get_valid_actions` is correct."""
    key = jax.random.PRNGKey(0)
    state, _ = sliding_tile_puzzle.reset(key)
    get_valid_actions_fn = jax.jit(sliding_tile_puzzle._get_valid_actions)
    action_mask = get_valid_actions_fn(state.empty_tile_position)

    # Check that the action mask is a boolean array with the correct shape.
    assert action_mask.dtype == jnp.bool_
    assert action_mask.shape == (4,)


def test_sliding_tile_puzzle_does_not_smoke(
    sliding_tile_puzzle: SlidingTilePuzzle,
) -> None:
    """Test that we can run an episode without any errors."""
    check_env_does_not_smoke(sliding_tile_puzzle)


def test_env_one_move_to_solve(sliding_tile_puzzle: SlidingTilePuzzle) -> None:
    """Test that the environment correctly handles a situation
    where the puzzle is one move away from being solved."""
    # Set up a state that is one move away from being solved.
    solved_puzzle = jnp.array([[1, 2], [3, 0]])
    one_move_away = jnp.array([[1, 0], [3, 2]])
    empty_tile_position = jnp.array([0, 1])
    state = State(
        puzzle=one_move_away,
        empty_tile_position=empty_tile_position,
        key=jax.random.PRNGKey(0),
    )

    # The correct action to solve the puzzle is to move the empty tile to the right (action=3).
    action = jnp.array(3)
    next_state, timestep = sliding_tile_puzzle.step(state, action)

    assert jnp.array_equal(next_state.puzzle, solved_puzzle)
    assert timestep.step_type == 2  # 2 denotes the last step
    assert timestep.discount == 0.0


def test_env_illegal_move_does_not_change_board(
    sliding_tile_puzzle: SlidingTilePuzzle,
) -> None:
    """Test that an illegal move does not change the board."""
    # Set up an arbitrary state.
    puzzle = jnp.array([[1, 2], [0, 3]])
    empty_tile_position = jnp.array([1, 0])
    state = State(
        puzzle=puzzle,
        empty_tile_position=empty_tile_position,
        key=jax.random.PRNGKey(0),
    )

    # An illegal move is to move the empty tile down (action=1) from its current position.
    action = jnp.array(1)
    next_state, _ = sliding_tile_puzzle.step(state, action)

    assert jnp.array_equal(next_state.puzzle, state.puzzle)


def test_env_legal_move_changes_board_as_expected(
    sliding_tile_puzzle: SlidingTilePuzzle,
) -> None:
    """Test that a legal move changes the board as expected."""
    # Set up an arbitrary state.
    puzzle = jnp.array([[1, 2], [0, 3]])
    empty_tile_position = jnp.array([1, 0])
    state = State(
        puzzle=puzzle,
        empty_tile_position=empty_tile_position,
        key=jax.random.PRNGKey(0),
    )

    # A legal move is to move the empty tile up (action=0).
    action = jnp.array(0)
    next_state, _ = sliding_tile_puzzle.step(state, action)

    # After the action, the board should look like this.
    expected_puzzle = jnp.array([[0, 2], [1, 3]])

    assert jnp.array_equal(next_state.puzzle, expected_puzzle)
