"""Data sets."""

from aim2dat.utils.data import atomic_radii, electronegativity


__all__ = ["atomic_radii", "electronegativity"]

element_groups = {
    "H": ["non-metal"],
    "He": ["non-metal", "noble gas"],
    "Li": ["metal", "alkaline"],
    "Be": ["metal", "alkaline earth"],
    "B": ["non-metal", "metalloid"],
    "C": ["non-metal"],
    "N": ["non-metal", "pnictogen"],
    "O": ["non-metal", "chalcogen"],
    "F": ["non-metal", "halogen"],
    "Ne": ["non-metal", "noble gas"],
    "Na": ["metal", "alkaline"],
    "Mg": ["metal", "alkaline earth"],
    "Al": ["metal"],
    "Si": ["non-metal", "metalloid"],
    "P": ["non-metal", "pnictogen"],
    "S": ["non-metal", "chalcogen"],
    "Cl": ["non-metal", "halogen"],
    "Ar": ["non-metal", "noble gas"],
    "K": ["metal", "alkaline"],
    "Ca": ["metal", "alkaline earth"],
    "Sc": ["metal", "transition metal"],
    "Ti": ["metal", "transition metal"],
    "V": ["metal", "transition metal"],
    "Cr": ["metal", "transition metal"],
    "Mn": ["metal", "transition metal"],
    "Fe": ["metal", "transition metal"],
    "Co": ["metal", "transition metal"],
    "Ni": ["metal", "transition metal"],
    "Cu": ["metal", "transition metal"],
    "Zn": ["metal", "transition metal"],
    "Ga": ["metal"],
    "Ge": ["non-metal", "metalloid"],
    "As": ["non-metal", "metalloid", "pnictogen"],
    "Se": ["non-metal", "chalcogen"],
    "Br": ["non-metal", "halogen"],
    "Kr": ["non-metal", "noble gas"],
    "Rb": ["metal", "alkaline"],
    "Sr": ["metal", "alkaline earth"],
    "Y": ["metal", "transition metal"],
    "Zr": ["metal", "transition metal"],
    "Nb": ["metal", "transition metal"],
    "Mo": ["metal", "transition metal"],
    "Tc": ["metal", "transition metal"],
    "Ru": ["metal", "transition metal"],
    "Rh": ["metal", "transition metal"],
    "Pd": ["metal", "transition metal"],
    "Ag": ["metal", "transition metal"],
    "Cd": ["metal", "transition metal"],
    "In": ["metal"],
    "Sn": ["metal"],
    "Sb": ["non-metal", "metalloid", "pnictogen"],
    "Te": ["non-metal", "metalloid", "chalcogen"],
    "I": ["non-metal", "halogen"],
    "Xe": ["non-metal", "noble gas"],
    "Cs": ["metal", "alkaline"],
    "Ba": ["metal", "alkaline earth"],
    "La": ["metal", "rare earth"],
    "Pr": ["metal", "rare earth"],
    "Nd": ["metal", "rare earth"],
    "Pm": ["metal", "rare earth"],
    "Sm": ["metal", "rare earth"],
    "Eu": ["metal", "rare earth"],
    "Gd": ["metal", "rare earth"],
    "Tb": ["metal", "rare earth"],
    "Dy": ["metal", "rare earth"],
    "Ho": ["metal", "rare earth"],
    "Er": ["metal", "rare earth"],
    "Tm": ["metal", "rare earth"],
    "Yb": ["metal", "rare earth"],
    "Lu": ["metal", "rare earth"],
    "Hf": ["metal", "transition metal"],
    "Ta": ["metal", "transition metal"],
    "W": ["metal", "transition metal"],
    "Re": ["metal", "transition metal"],
    "Os": ["metal", "transition metal"],
    "Ir": ["metal", "transition metal"],
    "Pt": ["metal", "transition metal"],
    "Au": ["metal", "transition metal"],
    "Hg": ["metal", "transition metal"],
    "Tl": ["metal"],
    "Pb": ["metal"],
    "Bi": ["metal", "pnictogen"],
    "Po": ["non-metal", "metalloid", "chalcogen"],
    "At": ["non-metal", "halogen"],
    "Rn": ["non-metal", "noble gas"],
    "Ac": ["metal"],
    "Th": ["metal"],
    "Pa": ["metal"],
    "U": ["metal"],
    "Np": ["metal"],
    "Pu": ["metal"],
    "Am": ["metal"],
    "Cm": ["metal"],
    "Bk": ["metal"],
    "Cf": ["metal"],
    "Es": ["metal"],
    "Fm": ["metal"],
    "Md": ["metal"],
    "No": ["metal"],
    "Lr": ["metal"],
    "Rf": ["metal", "transition metal"],
    "Db": ["metal", "transition metal"],
    "Sg": ["metal", "transition metal"],
    "Bh": ["metal", "transition metal"],
    "Hs": ["metal", "transition metal"],
    "Mt": ["metal", "transition metal"],
    "Ds": ["metal", "transition metal"],
    "Rg": ["metal", "transition metal"],
    "Cn": ["metal", "transition metal"],
    "Nh": ["metal"],
    "Fl": ["metal"],
    "Mc": ["metal", "pnictogen"],
    "Lv": ["metal"],
    "Ts": ["non-metal", "halogen"],
    "Og": ["non-metal", "noble gas"],
}


val_electrons = {
    "H": 1,
    "He": 2,
    "Li": 1,
    "Be": 2,
    "B": 3,
    "C": 4,
    "N": 5,
    "O": 6,
    "F": 7,
    "Ne": 8,
    "Na": 1,
    "Mg": 2,
    "Al": 3,
    "Si": 4,
    "P": 5,
    "S": 6,
    "Cl": 7,
    "Ar": 8,
    "K": 1,
    "Ca": 2,
    "Sc": 3,
    "Ti": 4,
    "V": 5,
    "Cr": 6,
    "Mn": 7,
    "Fe": 8,
    "Co": 9,
    "Ni": 10,
    "Cu": 11,
    "Zn": 12,
    "Ga": 3,
    "Ge": 4,
    "As": 5,
    "Se": 6,
    "Br": 7,
    "Kr": 8,
    "Rb": 1,
    "Sr": 2,
    "Y": 3,
    "Zr": 4,
    "Nb": 5,
    "Mo": 6,
    "Tc": 7,
    "Ru": 8,
    "Rh": 9,
    "Pd": 10,
    "Ag": 11,
    "Cd": 12,
    "In": 3,
    "Sn": 4,
    "Sb": 5,
    "Te": 6,
    "I": 7,
    "Xe": 8,
    "Cs": 1,
    "Ba": 2,
    "La": 3,
    "Ce": 4,
    "Pr": 5,
    "Nd": 6,
    "Pm": 7,
    "Sm": 8,
    "Eu": 9,
    "Gd": 10,
    "Tb": 11,
    "Dy": 12,
    "Ho": 13,
    "Er": 14,
    "Tm": 15,
    "Yb": 16,
    "Lu": 3,
    "Hf": 4,
    "Ta": 5,
    "W": 6,
    "Re": 7,
    "Os": 8,
    "Ir": 9,
    "Pt": 10,
    "Au": 11,
    "Hg": 12,
    "Tl": 3,
    "Pb": 4,
    "Bi": 5,
    "Po": 6,
    "At": 7,
    "Rn": 8,
    "Fr": 1,
    "Ra": 2,
    "Ac": 3,
    "Th": 5,
    "Pa": 5,
    "U": 6,
    "Np": 7,
    "Pu": 8,
    "Am": 9,
    "Cm": 10,
    "Bk": 11,
    "Cf": 12,
    "Es": 13,
    "Fm": 14,
    "Md": 15,
    "No": 16,
    "Lr": 3,
    "Rf": 4,
    "Db": 5,
    "Sg": 6,
    "Bh": 7,
    "Hs": 8,
    "Mt": 9,
    "Ds": 10,
    "Rg": 11,
    "Cn": 12,
    "Nh": 3,
    "Fl": 4,
    "Mc": 5,
    "Lv": 6,
    "Ts": 7,
    "Og": 8,
}
