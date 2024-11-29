"""
Functions to read the restart file of CP2K.
"""

# Standard library imports
from typing import List, Union
import re

# Third party library imports
import numpy as np

# Internal library imports
from aim2dat.io.base_parser import parse_pattern_function, _BasePattern
from aim2dat.io.utils import read_multiple


class _CellPattern(_BasePattern):
    pattern = r"^\s*&CELL\n(.*\n)*?\s*&END\sCELL"
    _dir_mapping = {"A": 0, "B": 1, "C": 2}

    def process_data(self, output: dict, matches: List[re.Match]):
        output["pbc"] = [True, True, True]
        cell = [None, None, None]
        cell_factors = [1.0, 1.0, 1.0]
        m = matches[-1]
        for line in m.string[m.start() : m.end()].splitlines()[1:-1]:
            line_sp = line.split()
            label = line_sp[0].upper()
            if label in self._dir_mapping:
                cell[self._dir_mapping[label]] = np.array([float(val) for val in line_sp[1:]])
            elif label == "PERIODIC":
                output["pbc"] = [(dir_st in line_sp[1]) for dir_st in ["X", "Y", "Z"]]
            elif label == "MULTIPLE_UNIT_CELL":
                cell_factors = [float(val) for val in line_sp[1:]]
        if all(c0 is not None for c0 in cell):
            output["cell"] = [(c_f * v0).tolist() for c_f, v0 in zip(cell_factors, cell)]


class _CoordPattern(_BasePattern):
    pattern = r"^\s*&COORD\n(.*\n)*?\s*&END\sCOORD"

    def process_data(self, output: dict, matches: List[re.Match]):
        output["kinds"] = []
        output["positions"] = []
        m = matches[-1]
        for line in m.string[m.start() : m.end()].splitlines()[1:-1]:
            line_sp = line.split()
            output["kinds"].append(line_sp[0])
            pos = []
            for val in line_sp[1:]:
                try:
                    pos.append(float(val))
                except ValueError:
                    pos.append(0.0)
            output["positions"].append(pos)


class _KindPattern(_BasePattern):
    pattern = r"\s*&KIND\s(?P<kind>\S+)\n(.*\n)*?\s*&END\sKIND"

    def process_data(self, output: dict, matches: List[re.Match]):
        output["kind_info"] = {}
        for m in matches:
            kind = m.groupdict()["kind"]
            element = kind
            for line in m.string[m.start() : m.end()].splitlines()[1:-1]:
                line_sp = line.split()
                if line_sp[0].upper() == "ELEMENT":
                    element = line_sp[1]
                    break
            output["kind_info"][kind] = element


def read_optimized_structure(folder_path: str) -> Union[dict, List[dict]]:
    """
    Read optimized structures from 'restart'-files.

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the CP2K ouput-files.

    Returns
    -------
    dict or list
        Dictionary containing the structural information. In case of a farming job a list of
        dictionaries is returned. In case several calculations have been run in the same folder a
        nested dictionary is returned.
    """
    from warnings import warn

    warn(
        "This function will be removed, please use `read_restart_structure` instead.",
        DeprecationWarning,
        2,
    )

    structures = read_restart_structure(folder_path)
    if isinstance(structures, list):
        for strct in structures:
            strct["symbols"] = strct.pop("elements")
    else:
        structures["symbols"] = structures.pop("elements")
    return structures


@read_multiple(r".*-1\.restart$", is_read_strct_method=True)
def read_restart_structure(folder_path: str) -> Union[dict, List[dict]]:
    """
    Read structures from 'restart'-files.

    Parameters
    ----------
    folder_path : str
        Path to the folder containing the CP2K ouput-files.

    Returns
    -------
    dict or list
        Dictionary or list of dictionaries containing the structural information. In case of a
        farming job or several calculations have been run in the same folder, a list of
        dictionaries is returned.
    """
    structures = []
    for file_p, file_n in zip(folder_path["file"], folder_path["file_name"]):
        proj = file_n.rsplit("-", 1)[0]
        output = parse_pattern_function(file_p, [_CellPattern, _CoordPattern, _KindPattern])
        kind_info = output.pop("kind_info")
        output["elements"] = [kind_info[kind] for kind in output["kinds"]]
        output["label"] = proj
        structures.append(output)
    return structures[0] if len(structures) == 1 else structures
