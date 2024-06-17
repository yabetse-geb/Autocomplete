"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    PrefixTree class where each node has a value and dictionary of
    children that are connected by edges to other PrefixTree nodes
    """

    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        curr = self
        if key == "":
            curr.value = value

        for i, letter in enumerate(key):
            if i == len(key) - 1:  # if last letter set with value
                if letter in curr.children:
                    curr.children[letter].value = value  # just change value
                else:  # add a new node
                    curr.children[letter] = PrefixTree()
                    curr.children[letter].value = (
                        value  # add the value since init doesn't
                    )
            else:
                if (
                    letter in curr.children
                ):  # if it's already there point curr to it
                    # and go to next iteration and don't make a new instance
                    curr = curr.children[letter]
                    continue
                curr.children[letter] = PrefixTree()  # add a child node
                curr = curr.children[letter]  # update curr to be the child node
        #self.reduce_rep_func(key, "set", value)

    def reduce_rep_func(self, key, functionality, value=0):
        """
        To reduce repition for get, del, increment, get_node, contains functions
        """
        if not isinstance(key, str):
            raise TypeError("Key should be a string")

        curr = self

        for i, letter in enumerate(key):
            if (
                functionality != "set" and letter not in curr.children
            ):
                raise KeyError("Key not found")
            elif i == len(key) - 1:  # if last letter return value
                if functionality == "get node":
                    return curr.children[letter]
            else:
                curr = curr.children[letter]

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> t= PrefixTree()
        >>> t['bat']= 7
        >>> t['bark']= ':)'
        >>> t['bar']= 3
        >>> t['bark']
        ':)'
        """
        try:
            node=self.reduce_rep_func(key, "get node")
        except TypeError:
            raise TypeError
        except KeyError:
            raise KeyError
        return node.value

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> t= PrefixTree()
        >>> t['bat']= 7
        >>> t['bark']= ':)'
        >>> t['bar']= 3
        >>> t['bark']
        >>> del t['bark']
        >>> t['bark']
        KeyError
        """
        try:
            node= self.reduce_rep_func(key, "get node")
        except TypeError:
            raise TypeError

        if node.value is None:
            raise KeyError
        node.value=None

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        try:
            node= self.reduce_rep_func(key, "get node")
        except TypeError:
            raise TypeError
        except KeyError:
            return False
        if node is None:
            return False
        return node.value is not None


    def __iter__(self, key=""):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        if self.children is None:  # leaf node
            if self.value is not None:
                yield (key, self.value)
        elif self.value is not None:  # has a value there
            yield (key, self.value)
        if self.children is not None:
            for i, j in self.children.items():
                yield from j.__iter__(key + i)

    def increment(self, key):
        """
        Helper funciton to increment witout traversing twice
        """
        node=self.reduce_rep_func(key, "get node")
        node.value += 1

    def get_node(self, key):
        """
        Returns actual PrefixTree Node
        """
        return self.reduce_rep_func(key, "get node")


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    tree = PrefixTree()
    history = set()
    for sentence in tokenize_sentences(text):
        for word in sentence.split(" "):
            if word in history:
                tree.increment(word)
            else:
                history.add(word)
                tree[word] = 1  # first time seeing word
    return tree


def autocomplete(tree, prefix, max_count=None, return_tuple=False):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    if max_count == 0:
        return []

    curr = tree  # checking if prefix is not in the prefex tree
    try:
        prefix_root = tree.get_node(prefix)
    except KeyError:
        return []

    result_tuple = []
    result_str = []

    # check if prefix is an empty string everything works
    if prefix == "":
        all_results = sorted(list(tree), key=lambda x: x[1], reverse=True)
        if max_count is not None:
            return [all_results[i][0] for i in range(max_count)]
        else:
            return [freq[0] for freq in all_results]

    for child_val in prefix_root:
        result_tuple.append((prefix + child_val[0], child_val[1]))
        result_str.append(prefix + child_val[0])

    if max_count is None:
        if return_tuple:
            return result_tuple
        return result_str
    else:
        result_tuple = sorted(result_tuple, key=lambda x: x[1], reverse=True)
        only_needed = result_tuple[:max_count]
        if return_tuple:
            return only_needed
        return [word[0] for word in only_needed]


# HELPER add to edit results
def add_valid_edit(history, tree, updated_str, tuple_results, str_results):
    """
    if valid edit it will add as a result
    """
    if updated_str not in history and updated_str in tree:
        # if updated_prefix_string in tree:
        tuple_results.append((updated_str, tree[updated_str]))
        str_results.append(updated_str)

        history.add(updated_str)


# helper adding edit
def add_letters(prefix, letter, pos):
    """
    adds a letter to a prefix and return result
    """
    prefix_list = list(prefix)
    prefix_list.insert(pos, letter)
    return "".join(prefix_list)


# helper character replacement
def char_replacement(prefix, letter, pos):
    prefix_list = list(prefix)
    prefix_list[pos] = letter
    return "".join(prefix_list)


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    # first see if autcomplete gives enough
    autocomplete_result = autocomplete(tree, prefix, max_count)
    autocomplete_result_tuple = autocomplete(tree, prefix, max_count, True)
    if max_count is not None and len(autocomplete_result) == max_count:
        return autocomplete_result
    # edits have to be made
    edit_results_tuple = []
    edit_results_str = []
    new_max_count = (
        max_count - len(autocomplete_result) if max_count is not None else None
    )

    curr_tree = tree
    history_prefixes = {prefix}
    for pos in range(
        len(prefix)
    ):  # each location word can be added, deleted, replaced, swapped
        # first adding any valid character at pos
        for child in curr_tree.children:
            updated_prefix_string = add_letters(prefix, child, pos)
            add_valid_edit(
                history_prefixes,
                tree,
                updated_prefix_string,
                edit_results_tuple,
                edit_results_str,
            )

            # next single-character replacement
            updated_prefix_string = char_replacement(prefix, child, pos)
            add_valid_edit(
                history_prefixes,
                tree,
                updated_prefix_string,
                edit_results_tuple,
                edit_results_str,
            )

        # next delete the word at that position
        prefix_list = list(prefix)
        updated_prefix_list = prefix_list[:pos] + prefix_list[pos + 1 :]
        updated_prefix_string = "".join(updated_prefix_list)
        add_valid_edit(
            history_prefixes,
            tree,
            updated_prefix_string,
            edit_results_tuple,
            edit_results_str,
        )

        # next two-character transpose
        prefix_list = list(prefix)
        if pos < len(prefix) - 1:
            prefix_list[pos], prefix_list[pos + 1] = (
                prefix_list[pos + 1],
                prefix_list[pos],
            )
            updated_prefix_string = "".join(prefix_list)  # was first updated inside
            add_valid_edit(
                history_prefixes,
                tree,
                updated_prefix_string,
                edit_results_tuple,
                edit_results_str,
            )

        # updated curr_tree
        curr_tree = tree.get_node(prefix[: pos + 1])

    new_result = autocomplete_result_tuple + edit_results_tuple
    result = []
    words = set()
    if max_count is None:
        for word in new_result:
            if word[0] not in words:
                result.append(word[0])
                words.add(word[0])
    else:
        result = autocomplete_result
        edit_results_tuple_sorted = sorted(
            edit_results_tuple, key=lambda x: x[1], reverse=True
        )  # sort based on frequencies
        edit_results = edit_results_tuple_sorted[
            :new_max_count
        ]  # get the amount of elements needed
        edit_results = [word[0] for word in edit_results]  # only need strings
        result += edit_results
        return list(set(result))
    return result


# HELPER FUNCTION APPEND TO ALL TUPLES
def add_to_all_tuples(tup, added_val):
    for i, val in enumerate(tup):  # append child to all tuples
        tup[i] = (added_val + val[0], val[1])


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    def word_filter_rec(tree, pattern):
        if len(pattern) == 0:  # base case
            if tree.value is None:
                return []
            return [("", tree.value)]

        if (
            pattern[0] != "?" and pattern[0] != "*" and pattern[0] in tree.children
        ):  # just a letter
            rec_result = word_filter_rec(tree.children[pattern[0]], pattern[1:])
            add_to_all_tuples(rec_result, pattern[0])
            return rec_result
        elif pattern[0] == "?":
            all_possible_results = []
            for child in tree.children:
                rec_result = word_filter_rec(tree.children[child], pattern[1:])
                add_to_all_tuples(rec_result, child)
                all_possible_results.extend(rec_result)
            return all_possible_results
        elif pattern[0] == "*":
            all_possible_results = []
            # first just ignore it
            rec_call_1 = word_filter_rec(tree, pattern[1:])
            all_possible_results.extend(rec_call_1)

            # now call it with the star staying there
            for child in tree.children:
                rec_result = word_filter_rec(tree.children[child], pattern)
                add_to_all_tuples(rec_result, child)
                all_possible_results.extend(rec_result)
            return all_possible_results

        return []

    result = word_filter_rec(tree, pattern)
    result_set = set(result)
    return list(result_set)


# test cases to show code examples
if __name__ == "__main__":
    # doctest.testmod()
    #Test case 1
    with open("Meta.txt", encoding="utf-8") as f:
        text = f.read()
    word_freq= word_frequencies(text)
    result= autocomplete(word_freq, "gre",6, return_tuple=False)
    print("Autocomplete 'gre' from Meta.txt:", result, "\n\n")

    #Test case 2- testing word filter
    print("Filter words in Meta.txt with 'c*h':", word_filter(word_freq, 'c*h'), "\n\n")

    #Test case 3- testing word filter
    with open("Two Cities.txt", encoding="utf-8") as f:
        text2 = f.read()
    word_freq2= word_frequencies(text2)
    print("Filter words in Two Cities.txt with 'r?c*t':", word_filter(word_freq2, 'r?c*t'), "\n\n")

    #Test case 4- testing autocorrect
    with open("Alice.txt", encoding="utf-8") as f:
        text3 = f.read()
    word_freq3= word_frequencies(text3)
    print("Autocorrect 'hear' from Alice.txt:", autocorrect(word_freq3, 'hear', 12), "\n\n")

    #Test case 5- testing autocorrect
    with open("Pride and Prejudice.txt", encoding="utf-8") as f:
        text4 = f.read()
    word_freq4= word_frequencies(text4)
    print("Autocorrect 'hear' from Pride and Prejudice.txt:", autocorrect(word_freq4, 'hear'))
    pass
