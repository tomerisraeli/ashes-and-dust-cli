import os
import rich
from rich.tree import Tree

from utils import constants


def __build_tree_dict(paths, tree_dict):
    for path in paths:
        current_dict = tree_dict
        for section in path.split(os.sep):
            if section not in current_dict.keys():
                current_dict[section] = {}
            current_dict = current_dict[section]
    return tree_dict


def __build_tree(tree_dict, tree):
    if not tree_dict:
        return

    for section in tree_dict:
        __build_tree(tree_dict[section],
                     tree.add(section)
                     )


def __get_files(root_path):
    for handler in constants.LOCAL_HANDLERS + constants.DOWNLOAD_HANDLERS:
        yield from handler.get_required_files_list(root_path)


def list_dir():
    """
    list all the files needed to run the download command
    :return: None
    """

    rich.print("[bold]structure of root directory")
    root_path = "<root path>"
    tree_dict = __build_tree_dict(__get_files(root_path), {})
    tree = Tree(label=root_path)
    __build_tree(tree_dict[root_path], tree)
    rich.print(tree)
