from pypd import Tree
import unittest


class TestSimpleTree(unittest.TestCase):

    def _make_tree(self, rootval, num_depth_nodes):
        """Return a tuple of a tree and a list of nodes created at each depth.

        rootval is expected to be an integer and num_depth_nodes is a list
        containing the number of nodes to create under each node at each
        depth.  So [2, 3, 4] would have 1 root node which has 2 child
        nodes, which each have 3 child nodes each, which each have 4 child
        nodes each, i.e.  1 + 2 + (2 * 3) + ((2*3) * 4) = 33 nodes

        The root node has the value given in rootval. All children have
        values of the format:
            nodenum-parentname
        where n is an increasing integer starting a rootval + 1.
        """

        # Below we will interate through each tree depth, adding a number of
        # nodes based on num_depth_nodes.
        t = Tree(value=rootval)

        # cur_depth_nodes will contain the list of nodes created at each
        # depth.
        cur_depth_nodes = [t]

        # All nodes created are returned to the caller.
        all_nodes = [cur_depth_nodes]
        node_num = rootval + 1

        # Nodes are inserted breadth first, which results in the node numbers
        # of each node being in increasing order. This is not tree for
        # nodes of different depths however.

        for depth, n in enumerate(num_depth_nodes):
            depth += 1
            next_depth_nodes = []
            for node in cur_depth_nodes:
                for i in range(n):
                    child = node.add('%d-%s' % (node_num, node.value))
                    next_depth_nodes.append(child)
                    node_num += 1

            all_nodes.append(next_depth_nodes)
            cur_depth_nodes = next_depth_nodes

        return t, all_nodes

    def test_init(self):
        # empty tree
        t, all_nodes = self._make_tree(0, [])
        self.assertTrue(t == all_nodes[0][0])
        self.assertFalse(t)
        self.assertFalse(len(t))

        # 1 node tree
        t, all_nodes = self._make_tree(0, [1])
        self.assertTrue(t == all_nodes[0][0])
        self.assertTrue(t[0] == all_nodes[1][0])
        self.assertTrue(len(t) == 1)

        # depth = 1 tree
        t, all_nodes = self._make_tree(0, [50])
        for node, depth in t:
            all_nodes[depth].remove(node)
        # The remaining contents of all nodes should be a few empty lists
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]

        # depth = 2 tree
        t, all_nodes = self._make_tree(0, [50, 50])
        for node, depth in t:
            all_nodes[depth].remove(node)
        # The remaining contents of all nodes should be a few empty lists
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]

    def test_add(self):
        num_depth_nodes = [2, 5, 5, 5, 2, 3, 5]

        # root value is None
        t, all_nodes = self._make_tree(0, num_depth_nodes)

        for node, depth in t:
            all_nodes[depth].remove(node)
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]

    def test_add_children(self):
        num_depth_nodes = [2, 5, 5]
        num_new_children = [2]

        # root value is None
        t, all_nodes = self._make_tree(0, num_depth_nodes)
        # make another tree so we can use its children to test addChildren.
        tchild, tchild_nodes = self._make_tree(0, num_new_children)

        children = t.addChildren([child.value for child in tchild._children])

        # the new children added
        all_nodes[1].extend(tchild_nodes[1])

        for node, depth in t:
            all_nodes[depth].remove(node)
        for node in all_nodes:
            self.assertFalse(node)

    def test_len(self):
        # root value is None
        num_depth_nodes = [2, 5, 5, 5, 2]
        t, all_nodes = self._make_tree(0, num_depth_nodes)

        depth_nodes = [t]
        for n in num_depth_nodes:
            # Check the length of each node at the current depth
            for node in depth_nodes:
                self.assertTrue(len(node) == n)

            # Make a list of all nodes at the next depth.
            # The following would give us a list of list of nodes:
            #     LL = [node[:n] for node in depth_nodes]
            # This can be flattened with:
            #     [i for sublist in LL for i in sublist]
            depth_nodes = [i for sublist in
                           [node[:n] for node in depth_nodes] for i in sublist]

    def test_getitem(self):
        # root value is None
        num_depth_nodes = [2, 5, 5, 4]
        t, all_nodes = self._make_tree(0, num_depth_nodes)

        depth_nodes = [t]
        for depth, n in enumerate(num_depth_nodes):
            # Check the length of each node at the current depth
            for node in depth_nodes:
                for i in range(n):
                    all_nodes[depth + 1].remove(node[i])

            # Make a list of all nodes at the next depth. This gives a list
            # of list of nodes
            new_nodes = [node[:n] for node in depth_nodes]
            # Flatten the list of lists into a single list
            depth_nodes = [node for sublist in new_nodes for node in sublist]

        # All nodes still contains the root node
        self.assertTrue(all_nodes[0] == [t])
        del all_nodes[0]

        # The remaining contents of all nodes should be a few empty lists
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]

    def test_addBranch(self):
        num_depth_nodes = [3]
        # root value is None
        t, all_nodes = self._make_tree(0, num_depth_nodes)

        # Make three new trees and add them as branches to t
        node_num = len(t) + 1
        branch1, branch1_nodes = self._make_tree(node_num, [2])
        node_num += 1
        branch2, branch2_nodes = self._make_tree(node_num, [2])
        node_num += 1
        branch3, branch3_nodes = self._make_tree(node_num, [2])
        t[0].addBranch(branch1)
        t[1].addBranch(branch2)
        t[2].addBranch(branch3)

        # Add the branch nodes to all_nodes - each index into all_nodes is
        # the depth of the nodes at that index.
        all_nodes.append(branch1_nodes[0])
        all_nodes[2].extend(branch2_nodes[0])
        all_nodes[2].extend(branch3_nodes[0])
        all_nodes.append(branch1_nodes[1])
        all_nodes[3].extend(branch2_nodes[1])
        all_nodes[3].extend(branch3_nodes[1])

        for node, depth in t:
            all_nodes[depth].remove(node)
        # Remove the root
        del all_nodes[0]
        # The remaining contents of all nodes should be a few empty lists
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]

    @staticmethod
    def get_node_num(node):
        nums = node.value.split('-')
        return int(nums[0])

    def test_iter(self):
        num_depth_nodes = [2, 2, 1]
        t, all_nodes = self._make_tree(0, num_depth_nodes)
        root_node = all_nodes[0][0]

        # The correct iteration order is depth first, in the order added.
        # For the tree, we've created with [2,2,1] the correct order is:
        #  0
        #    1-0
        #      3-1-0
        #        7-3-1-0
        #      4-1-0
        #        8-4-1-0
        #    2-0
        #      5-2-0
        #        9-5-2-0
        #      6-2-0
        #        10-6-2-0
        # To test that we iterate in the correct order:
        # - check that for every node given by the iter we have previously
        #   seen its parent
        # - check that for every node we get back at each depth the first
        # number in its node name always increases from previously seen values
        # at that same depth, i.e. siblings node number always increases

        # first node values at each depth
        depth_node_nums = []
        for node, depth in t:
            if node == root_node:
                node_num = 0
            else:
                self.assertTrue(node.parent.seen)
                node_num = self.get_node_num(node)
            node.seen = True

            if len(depth_node_nums) < (depth + 1):
                depth_node_nums.append([node_num])
            else:
                self.assertTrue(node_num < reduce(max, depth_node_nums))
                depth_node_nums[depth].append(node.value)

    def test_eq_neq(self):
        # test empty tree
        t1, _ = self._make_tree(0, [])
        t2, _ = self._make_tree(0, [])
        self.assertTrue(t1 == t2)

        # test trees of various depths
        for i in range(1, 9):
            num_depth_nodes = range(1, 4)
            t1, all_nodes1 = self._make_tree(0, num_depth_nodes)
            t2, all_nodes2 = self._make_tree(0, num_depth_nodes)
            self.assertTrue(t1 == t2)

            # Add a leaf to one tree and assert that they not equal
            node_num = len(all_nodes1) + 1
            all_nodes1[-1][-1].add(node_num)
            self.assertTrue(t1 != t2)

            # Add the same leaf to second tree. Assert they are equal again.
            all_nodes2[-1][-1].add(node_num)
            self.assertFalse(t1 != t2)

            # Add another node to the root. Assert unequal
            node_num += 1
            t1.add(node_num)
            self.assertTrue(t1 != t2)

            # Add same node to second tree. Assert they are equal again
            t2.add(node_num)
            self.assertFalse(t1 != t2)

    def test_leaf(self):
        num_depth_nodes = [2, 3, 4, 5]
        max_depth = 4
        t, all_nodes = self._make_tree(0, num_depth_nodes)

        for node, depth in t:
            if depth == max_depth:
                self.assertTrue(node.leaf())
            else:
                self.assertFalse(node.leaf())

    def test_apply(self):
        num_depth_nodes = [2, 3, 4, 5]
        t, all_nodes = self._make_tree(0, num_depth_nodes)
        t.apply(lambda node, depth: all_nodes[depth].remove(node))

        # The remaining contents of all nodes should be a few empty lists
        while len(all_nodes):
            self.assertFalse(all_nodes[0])
            del all_nodes[0]
