# BST Lecture - Raw Transcript

so today we're going to talk about binary search trees um so a BST is
basically defined by the invariant that for every node the left subtree is
smaller and the right subtree is bigger okay um one thing i didn't put in
the slides is that if you insert values in sorted order into a BST it
degenerates into a linked list and your operations become O(n) instead of
O(log n), that's why we care about self-balancing trees like AVL and
red-black trees um yeah so that's the main gotcha with plain BSTs
