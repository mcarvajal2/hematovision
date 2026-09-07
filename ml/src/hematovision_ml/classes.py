"""Canonical class order shared with the published web application."""

CLASS_NAMES = (
    "Basófilos",
    "Eosinófilos",
    "Eritroblastos",
    "Linfoblastos",
    "Linfocitos",
    "Mieloblastos",
    "Monocitos",
    "Neutrófilos",
    "Plaquetas",
)


def class_index(name: str) -> int:
    """Return the canonical class index, raising ValueError for an unknown class."""
    return CLASS_NAMES.index(name)


def class_name(index: int) -> str:
    """Return the canonical class name, raising IndexError for an invalid index."""
    return CLASS_NAMES[index]
