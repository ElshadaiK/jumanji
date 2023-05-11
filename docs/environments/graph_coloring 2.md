# Graph Coloring Environment

<p align="center">
    <img src="../env_img/graph_coloring.png" width="500"/>
</p>

We provide here a Jax JIT-able implementation of the Graph Coloring environment.

Graph Coloring is a combinatorial optimization problem where the objective is to assign a color to each vertex of a graph in such a way that no two adjacent vertices share the same color. The problem is usually formulated as minimizing the number of colors used. The Graph Coloring environment is an episodic, single-agent setting that allows for the exploration of graph coloring algorithms and reinforcement learning methods.

## Observation

The observation in the GraphColoring environment includes information about the graph, the colors assigned to the vertices, the action mask, and the current node index.

- `graph`: jax array (bool) of shape (num_nodes, num_nodes), representing the adjacency matrix of the graph.
  - For example, a random observation of the graph adjacency matrix:

        ```[[False,  True, False,  True],
        [ True, False,  True, False],
        [False,  True, False,  True],
        [ True, False,  True, False]]```

- `colors`: jax array (int32) of shape (num_nodes,), representing the current color assignments for the vertices. Initially, all elements are set to -1, indicating that no colors have been assigned yet.
  - For example, an initial color assignment:
    ```[-1, -1, -1, -1]```

- `action_mask`: jax array (bool) of shape (num_colors,), indicating which actions are valid in the current state of the environment. The valid actions are represented by True, while invalid actions are represented by False.
  - For example, for 4 number of colors available:
    ```[True, False, True, False]```

- `current_node_index`: integer representing the current node being colored.
  - For example, an initial current_node_index might be 0.

## Action

The action space is a DiscreteArray of integer values in [0, 1, ..., num_colors - 1]. Each action corresponds to assigning a color to the current node.

## Reward

The reward in the Graph Coloring environment is given as follows:

- `sparse reward`: a reward is provided at the end of the episode and equals the negative of the number of unique colors used to color all vertices in the graph.

The agent's goal is to find a valid coloring using as few colors as possible while avoiding conflicts with adjacent nodes.

## Episode Termination

An episode terminates when all nodes in the graph have been assigned a color. The goal of the agent is to find a valid coloring using as few colors as possible.

## Registered Versions 📖

- `GraphColoring-v0`: The default settings for the `GraphColoring` problem with a configurable number of nodes and connectivity.
