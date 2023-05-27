import os
import rich
from rich.tree import Tree

from utils import constants


class __TreeNode:
    """
    a support class to generate the paths tree
    """

    def __init__(self, value):
        """
        init a new __TreeNode object with the given value
        :param value:
        """
        self.__value = value
        self.__paths = set()
        self.__next = []

    def __contains__(self, item):
        """
        check if the item itself or one if its next nodes is holding the given value
        :param item:    the value to look for
        :return:        bool
        """
        return item == self.__value or item in [node.__value for node in self.__next]

    def __str__(self):
        """
        get the value of the node as str
        :return:    str
        """
        return f"{self.__value}"

    def __getitem__(self, value):
        """
        get the item holding the given value
        :param value:   the value to look for
        :return:        __TreeNode object
        :raise:         IndexError if value doesnt exists
        """
        if value == self.__value:
            return self

        for node in self.__next:
            if node.__value == value:
                return node

        raise IndexError(f"{value} doesnt exists")

    def add_source(self, path):
        """
        add a new source to node, source is a path that leads to that node
        :param path:    the new source
        :return:        None
        """
        self.__paths.add(path)

    def add_next(self, node):
        """
        add a new "next" node
        :param node:    the node to add
        :return:        None
        """
        self.__next.append(node)

    def build_rich_tree(self, missing_paths, tree=None):
        """
        build the rich tree object of the tree
        :param missing_paths:   a set of paths to mark in red
        :param tree:            the rich tree built until that call, used for recuperation
        :return:                the generated tree
        """
        fmt = "[red]" if not self.__paths.isdisjoint(missing_paths) and not self.has_next() else ""
        tree = Tree(f"{fmt}{self}") if not tree else tree.add(f"{fmt}{self}")
        for node in self.__next:
            node.build_rich_tree(missing_paths, tree)
        return tree

    def has_next(self):
        """
        check if the node has next values
        :return:    bool
        """
        return len(self.__next) > 0


def __build_tree(paths, root, root_path):
    """
    build the __TreeNode tree from paths
    :param paths:   list of paths to insert
    :param root:    the root of the tree
    :return:        None
    """
    for path in paths:
        current_node = root
        for section in path.removeprefix(root_path).strip(os.sep).split(os.sep):
            if section not in current_node:
                current_node.add_next(__TreeNode(section))
            current_node = current_node[section]
            current_node.add_source(path)


def __get_files(root_path):
    """
    get all required files from handlers
    :param root_path:   the path to root directory
    :return:            generator of files
    """
    for handler in constants.LOCAL_HANDLERS + constants.DOWNLOAD_HANDLERS:
        yield from handler.get_required_files_list(root_path)


def list_dir(root_path="<root path>", missing_files=None):
    """
    list all the files needed to run the download command
    :param root_path:       the path to root dir. if not given, a placeholder is taken
    :param missing_files:   a set of files to mark in red, empty array as default
    :return:                None
    """

    if missing_files is None:
        missing_files = {}

    tree = __TreeNode(root_path)
    __build_tree(__get_files(root_path), tree, root_path)
    rich_tree = tree.build_rich_tree(missing_files)
    rich.print(rich_tree)
