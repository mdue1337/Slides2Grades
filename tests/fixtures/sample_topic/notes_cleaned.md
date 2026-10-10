# Binary Search Trees

## Definition
A **binary search tree** is a binary tree where every node's key is greater
than all keys in its left subtree and less than all keys in its right
subtree.

- The invariant must hold at **every** node, not just the root.

## Complexity
Lookup, insert and delete are all $O(h)$ where $h$ is the height.
$$h = \Theta(\log n) \text{ if balanced}, \qquad h = \Theta(n) \text{ worst case}$$

Requires the keys to be **totally ordered** — no BST over an unordered type.

==**Height of a complete tree:**==
$$h = \lfloor \log_2 n \rfloor$$

A perfect tree of height $h$ holds ==$n = 2^{h+1}-1$== nodes, and at most
==$2^{d}$== nodes sit at depth $d$.

> **Trap:** inserting already-sorted data gives a linked list, not a tree.

## Traversal and deletion
**In-order** — left, node, right; yields the keys in sorted order.

See [[Sorting Algorithms]] for the traversal connection.

**Lookup**
```python
if key == node.key:
    return node
```

**Deletion cases**
- No child: remove the node.
- One child: splice the child in.
- Two children: replace with the in-order successor, then delete that
  successor.
- Sletning af en node med to børn er den eneste sletning der flytter en anden
  nøgle.

## Example 4.2
Insert 5, 3, 8, 1 into an empty tree:
```
     5
    / \
   3   8
  /
 1
```
Height $h = \lfloor \log_2 4 \rfloor = 2$.

![[Pasted image bst-example.png]]

## Aside
**Exam advice:** always state which balance invariant you are assuming —
claiming $O(\log n)$ without saying the tree is balanced loses marks.
