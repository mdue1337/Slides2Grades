___
Glossary for [[Binary Search Trees]]. Terms in the order they matter, not
alphabetical.

# Core
**Tree** — acyclic connected graph with one designated root.
**Height** — longest root-to-leaf path, counted in edges.
**Invariant** — a property every operation must restore before it returns.

# Traversal
**In-order** — left, node, right. On a BST it yields the keys sorted.
**Pre-order** — node, left, right. Serialises the shape.

## Binary Search Trees

### Binary search tree
**Definition**: A binary tree where every node's key is above every key in its
left subtree and below every key in its right subtree.
**Why it matters**: Turns lookup into one walk down a root-to-leaf path.
**Source**: [[Binary Search Trees]]

### Rotation
**Definition**: A local restructuring that changes height while preserving
in-order order.
**Why it matters**: The primitive every balanced-BST scheme is built from.
**Source**: [[Binary Search Trees]]
