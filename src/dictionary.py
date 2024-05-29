"""A Dictionary reimplemented in simple Python for educational purposes.
Copyright Zeth 2024.
Feel free to submit improvements or implement more methods.
"""

from typing import Any
from collections.abc import Hashable


# pylint: disable=too-few-public-methods
class DictEntry:
    """If you think of a dictionary as an SQL table,
    each row has the hash as the "primary key".
    It also contains the key and (a pointer to) the value.
    If you don't know what a pointer is,
    it doesn't matter right now, ignore the brackets.
    Each entry has the hash, the key and the value.
    """

    def __init__(self, key: Hashable, value: Any) -> None:
        self.hash = hash(key)
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return str(self.key)


DUMMY = DictEntry("Dummy123", "Nothing")


class Dictionary:
    """A Dictionary emulating the built in (C) dictionary."""

    # The current number of items in the dictionary
    _used: int = 0

    # The maximum allowed items under the current memory allocation
    _fill: int = 8

    # Pretending to be stack memory
    _small_table: list[DictEntry] = []

    # Prentending to be heap memory
    _table: list[DictEntry] = []

    @property
    def table(self) -> list[DictEntry]:
        """
        C started on the 1970 PDP-11 computer, with bare metal memory,
        where the "stack" was a fast CPU cache
        and the "heap" was much slower external RAM.

        The difference is more maginal now as modern computers have
        managed virtual memory with each program quarantined to its
        own memory assignment.

        Python dictionaries start with a small 8 slot table on the stack,
        then if needed, it uses malloc to assign memory on the heap."""
        if self._fill <= 8:
            return self._small_table
        return self._table

    def __len__(self) -> int:
        return self._used

    def _update_table_size(self) -> None:
        """Python makes sure that the dictionary always has space to grow.
        If the dictionary uses more than two-thirds of its memory allocation,
        it doubles the allocation."""
        self._used += 1
        if self._used > (self._fill * (2 / 3)):
            self._expand()

    def _expand(self) -> None:
        """The first time that the Python dictionary expands,
        it moves the items from the stack to heap memory.
        It then doubles its heap allocation whenever needed."""
        if self._fill == 8:
            for entry in self._small_table:
                self._table.append(entry)
            self._small_table = []
        self._fill *= 2

    def __getitem__(self, key: Hashable, default: Any = None) -> Any:
        for entry in self.table:
            if entry.hash == hash(key):
                return entry.value
        if default:
            return default
        raise KeyError(key)

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Return the value for key if key is in the dictionary,
        else default."""
        # pylint: disable=unnecessary-dunder-call
        return self.__getitem__(key, default)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """The Python dictionary manages its memory when a new
        item is added."""
        # Update if key is already there
        for entry in self.table:
            if entry.hash == hash(key):
                entry.value = value
                return

        # Make a new entry
        new_entry = DictEntry(key, value)

        # Recyle space if there is spare
        for index, entry in enumerate(self.table):
            if entry == DUMMY:
                self.table[index] = new_entry
                self._update_table_size()
                return

        # Add new the entry to the end
        self.table.append(new_entry)
        self._update_table_size()

    def __delitem__(self, key: Hashable) -> None:
        """Deleting an item does not make a dictionary smaller.
        Instead, Python replaces the table entry with a dummy
        and resues the space later."""
        for index, entry in enumerate(self.table):
            if entry.hash == hash(key):
                self.table[index] = DUMMY
                self._used -= 1
                return
        raise KeyError(key)

    def __str__(self) -> str:
        output = "{"
        for entry in self.table:
            output += f"{repr(entry.key)}: {repr(entry.value)}, "
        return output[:-2] + "}"

    def clear(self) -> None:
        """Remove all items from the dictionary."""
        self._table = []
        self._small_table = []
        self._fill = 8
        self._used = 0


def test_dictionary() -> None:
    """Simple example of how to use the dictionary.
    Run directly or using Pytest."""
    # pylint: disable=protected-access
    sauces = Dictionary()
    sauces["Cod"] = "Tartar"
    sauces["Chips"] = "Brown"
    sauces["Sausage"] = "Mustard"
    sauces["Beef"] = "Mushroom"
    sauces["Turkey"] = "Cranberry"
    assert len(sauces) == 5

    assert sauces["Beef"] == "Mushroom"
    sauces["Beef"] = "Peppercorn"
    assert sauces["Beef"] == "Peppercorn"
    assert len(sauces) == 5
    del sauces["Beef"]
    assert len(sauces) == 4
    assert sauces.get("Beef", "Ketchup") == "Ketchup"
    assert sauces.get("Chips", "Ketchup") == "Brown"

    sauces["Duck"] = "Ginger"
    sauces["Duck"] = "Honey"
    assert len(sauces) == 5

    # Up to 5 items, we use the small table
    assert sauces.table == sauces._small_table
    assert sauces._fill == 8

    sauces["Lamb"] = "Mint"
    assert len(sauces) == 6

    # 6 is items is over two thirds of 8, so the heap table is used,
    # and the maximum number of items doubles.
    assert sauces.table == sauces._table
    assert sauces._fill == 16

    sauces.clear()
    assert len(sauces) == 0


if __name__ == "__main__":
    test_dictionary()
