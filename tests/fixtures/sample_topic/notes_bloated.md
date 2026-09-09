# Binary Search Trees

## Motivation
The binary search tree was one of the great ideas of early computer science.
In the 1960s, as memory became cheap enough to hold large collections in
core, researchers looked for a structure that would give the lookup speed of
a sorted array without the insertion cost. The BST was the answer, and it
remains the mental model behind most ordered containers today. Think of it
as the data-structure equivalent of binary search itself, made persistent.

## Definition
A **binary search tree** is a binary tree where every node's key is greater
than all keys in its left subtree and less than all keys in its right
subtree.

- [FROM LECTURE] The invariant must hold for **every** node, not just the
  root. A tree that satisfies it only at the root is not a BST.

## Complexity
Lookup, insert and delete are all $O(h)$ where $h$ is the height.
$$h = \Theta(\log n) \text{ if balanced}, \qquad h = \Theta(n) \text{ worst case}$$

Requires the keys to be **totally ordered** — no BST over an unordered type.

> **Trap:** the worst case is not exotic. Inserting already-sorted data gives
> a linked list, not a tree.

## Proof that in-order traversal is sorted
We argue by induction on the height of the tree. For the base case, a tree of
height 0 is empty and the empty sequence is trivially sorted. For the
inductive step, assume the claim holds for all trees of height less than $h$
and consider a tree of height $h$ with root $r$. By the inductive hypothesis
the traversal of the left subtree is sorted, and every key in it is less than
$r$ by the BST invariant. The same argument applies on the right. Therefore
the concatenation is sorted, which completes the induction.

## Example 4.2
Insert 5, 3, 8, 1 into an empty tree.
First we insert 5, which becomes the root because the tree is empty. Then we
insert 3; we compare it against 5, find it smaller, and go left, where we
find an empty slot. Then 8, which is larger than 5, so it goes right. Then 1,
which is smaller than 5 and then smaller than 3, so it ends up as the left
child of 3. The resulting tree has height 2.
```
     5
    / \
   3   8
  /
 1
```

## Aside
This was the part of the lecture where the projector failed, so the last ten
minutes ran over into the break. The exercise sheet is on the course page and
is due Friday.

**Exam advice:** always state which balance invariant you are assuming. Half
the marks lost on this topic come from claiming $O(\log n)$ without saying
the tree is balanced.

## Complexity again
As noted above, lookup is $O(h)$, which is $\Theta(\log n)$ when the tree is
balanced and $\Theta(n)$ in the worst case.

See [[Sorting Algorithms]] for the traversal connection.

![[Pasted image bst-example.png]]
