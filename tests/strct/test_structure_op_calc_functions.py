"""Test calculate-functions via the StructureOperations class."""

# Standard library imports
import os

# Third party library imports
import pytest

# Internal library imports:
from aim2dat.strct import StructureCollection, StructureOperations
from aim2dat.strct.ext_analysis import (
    calculate_prdf,
    calculate_ffingerprint_order_p,
    calculate_warren_cowley_order_p,
    calculate_planes,
)
from aim2dat.io.yaml import load_yaml_file


STRUCTURES_PATH = os.path.dirname(__file__) + "/structures/"
MISC_PATH = os.path.dirname(__file__) + "/miscellaneous/"
PRDF_PATH = os.path.dirname(__file__) + "/prdf_functions/"
WC_LIKE_ORDER_PATH = os.path.dirname(__file__) + "/warren_cowley_like_order_p/"
COORDINATION_PATH = os.path.dirname(__file__) + "/coordination/"
PLANES_PATH = os.path.dirname(__file__) + "/planes/"
STABILITIES_PATH = os.path.dirname(__file__) + "/stabilities/"


def test_calculate_distance_indices_check(create_structure_collection_object):
    """Test correct error handling on site indices input."""
    strct_c, _ = create_structure_collection_object(["Benzene"])
    strct_ops = StructureOperations(strct_c)
    with pytest.raises(ValueError) as error:
        strct_ops[0].calculate_distance([1] * 3, [0, 2, 20])
    assert str(error.value) == "`site_index` needs to be smaller than the number of sites."
    with pytest.raises(TypeError) as error:
        strct_ops[0].calculate_distance([1.0] * 3, [0, 2, 3])
    assert str(error.value) == "`site_index` needs to be of type int."
    with pytest.raises(TypeError) as error:
        strct_ops[0].calculate_distance([0, 2.0, 3], [1] * 3)
    assert str(error.value) == "`site_index` needs to be of type int."


@pytest.mark.parametrize("structure, file_suffix", [("Benzene", "xyz"), ("ZIF-8", "cif")])
def test_calculate_distance(structure, file_suffix):
    """Test calculate_distance function."""
    ref_outputs = load_yaml_file(MISC_PATH + structure + "_ref.yaml")
    strct_c = StructureCollection()
    strct_c.append_from_file("test", STRUCTURES_PATH + structure + "." + file_suffix)
    strct_ops = StructureOperations(strct_c)
    dist = strct_ops["test"].calculate_distance(**ref_outputs["distance"]["function_args"])
    if isinstance(ref_outputs["distance"]["reference"], list):
        assert [
            abs(dist[(idx0, idx1)] - val) < 1e-5
            for (idx0, idx1, val) in zip(
                ref_outputs["distance"]["function_args"]["site_index1"],
                ref_outputs["distance"]["function_args"]["site_index2"],
                ref_outputs["distance"]["reference"],
            )
        ], "Wrong distance."
    else:
        assert abs(dist - ref_outputs["distance"]["reference"]) < 1e-5, "Wrong distance."


@pytest.mark.parametrize("structure, file_suffix", [("ZIF-8", "cif"), ("ScBDC", "cif")])
def test_calculate_distance_sc(structure, file_suffix):
    """Test calculate_distance function using the super cell."""
    ref_outputs = load_yaml_file(MISC_PATH + structure + "_ref.yaml")
    strct_c = StructureCollection()
    strct_c.append_from_file(
        "test",
        STRUCTURES_PATH + structure + "." + file_suffix,
        backend="internal",
        backend_kwargs={"strct_check_chem_formula": False},
    )
    strct_ops = StructureOperations(strct_c)
    dist = strct_ops[0].calculate_distance(**ref_outputs["distance_sc"]["function_args"])
    for idx0, dist_list in enumerate(ref_outputs["distance_sc"]["reference"]):
        if isinstance(dist_list, list):
            site_index1, site_index2 = (
                ref_outputs["distance_sc"]["function_args"]["site_index1"][idx0],
                ref_outputs["distance_sc"]["function_args"]["site_index2"][idx0],
            )
            for dist_idx, dist_ref in enumerate(dist_list):
                assert (
                    abs(dist[(site_index1, site_index2)][dist_idx] - dist_ref) < 1e-5
                ), f"Distance {(site_index1, site_index2)}/{dist_idx} is wrong."
        else:
            assert abs(dist[idx0] - dist_list) < 1e-5, f"Distance {idx0} is wrong."


@pytest.mark.parametrize("structure, file_suffix", [("Benzene", "xyz"), ("ZIF-8", "cif")])
def test_calculate_angle(structure, file_suffix):
    """Test calculate_angle function."""
    ref_outputs = load_yaml_file(MISC_PATH + structure + "_ref.yaml")
    strct_c = StructureCollection()
    strct_c.append_from_file("test", STRUCTURES_PATH + structure + "." + file_suffix)
    strct_ops = StructureOperations(strct_c)
    dist = strct_ops["test"].calculate_angle(**ref_outputs["angle"]["function_args"])
    assert abs(dist - ref_outputs["angle"]["reference"]) < 1e-3, "Wrong angle."


@pytest.mark.parametrize("structure, file_suffix", [("ScBDC", "cif")])
def test_calculate_dihedral_angle(structure, file_suffix):
    """Test calculate_dihedral_angle function."""
    ref_outputs = load_yaml_file(MISC_PATH + structure + "_ref.yaml")
    strct_c = StructureCollection()
    strct_c.append_from_file(
        "test",
        STRUCTURES_PATH + structure + "." + file_suffix,
        backend="internal",
        backend_kwargs={"strct_check_chem_formula": False},
    )
    strct_ops = StructureOperations(strct_c)
    dist = strct_ops[0].calculate_dihedral_angle(**ref_outputs["dihedral_angle"]["function_args"])
    assert abs(dist - ref_outputs["dihedral_angle"]["reference"]) < 1e-3, "Wrong angle."


def test_cn_analysis_error():
    """Test method validation of coordination analysis."""
    strct_collect = StructureCollection()
    strct_collect.append("test", **dict(load_yaml_file(STRUCTURES_PATH + "GaAs_216_conv.yaml")))
    strct_ops = StructureOperations(strct_collect)
    with pytest.raises(ValueError) as error:
        strct_ops["test"].calculate_coordination(method="test")
    assert (
        str(error.value)
        == "Method 'test' is not supported. Supported methods are: 'minimum_distance', "
        "'n_nearest_neighbours', 'atomic_radius', 'econ', 'voronoi'."
    )
    with pytest.raises(ValueError) as error:
        strct_ops["test"].calculate_coordination(method="voronoi", voronoi_weight_type="test")
    assert str(error.value) == "`weight_type` 'test' is not supported."


@pytest.mark.parametrize(
    "structure,ref_order_p",
    [
        ("GaAs_216_prim", (742.1268, (495.7578, 495.7578))),
        (
            "Cs2Te_62_prim",
            (
                115.6221,
                (
                    155.4298,
                    113.9550,
                    114.2768,
                    153.4972,
                    153.4300,
                    113.8181,
                    113.7066,
                    153.9680,
                    62.4293,
                    62.2036,
                    62.2604,
                    62.6054,
                ),
            ),
        ),
    ],
)
def test_ffingerprint_order_parameters(structure, ref_order_p):
    """Test order F-fingerprint order parameters."""
    strct_collect = StructureCollection()
    inputs = dict(load_yaml_file(STRUCTURES_PATH + structure + ".yaml"))
    # inputs["structure_label"] = structure
    strct_collect.append(structure, **inputs)
    strct_ops = StructureOperations(strct_collect)
    t_order_p, site_order_p = strct_ops[structure].perform_analysis(
        method=calculate_ffingerprint_order_p,
        kwargs={"r_max": 20.0, "delta_bin": 0.005, "sigma": 10.0},
    )
    assert (
        abs(t_order_p - ref_order_p[0]) < 1e-3
    ), f"Total order parameter of structure {structure} is wrong."
    assert len(site_order_p) == len(
        ref_order_p[1]
    ), f"Wrong number of site order parameters for structure {structure}."
    for idx, (site_order_p0, ref_site_order_p0) in enumerate(zip(site_order_p, ref_order_p[1])):
        assert (
            abs(site_order_p0 - ref_site_order_p0) < 1e-3
        ), f"Order parameter of site {idx} of structure {structure} is wrong."


@pytest.mark.parametrize("structure", ["Cs2Te_62_prim", "GaAs_216_conv", "GaAs_216_prim"])
def test_prdf_functions(structure, nested_dict_comparison):
    """Test partial radial distribution calculation."""
    ref = load_yaml_file(PRDF_PATH + structure + "_ref.yaml")
    strct_c = StructureCollection()
    inputs = dict(load_yaml_file(STRUCTURES_PATH + structure + ".yaml"))
    strct_c.append(structure, **inputs)
    strct_ops = StructureOperations(strct_c)
    element_prdf, atomic_prdf = strct_ops[0].perform_analysis(
        method=calculate_prdf, kwargs=ref["parameters"]
    )

    assert len(element_prdf) == len(ref["element_prdf"]), "Wrong number of el-pairs."
    for el_pair, prdf in element_prdf.items():
        assert el_pair in ref["element_prdf"], f"Element pair {el_pair} not in reference output."
        assert all(
            [
                abs(val0 - ref["element_prdf"][el_pair][idx]) < 1.0e-5
                for idx, val0 in enumerate(prdf)
            ]
        ), f"Element prdf is wrong for element pair {el_pair}."
    assert len(atomic_prdf) == len(ref["atomic_prdf"]), "Wrong number of sites."
    for site_idx, site in enumerate(atomic_prdf):
        assert len(site) == len(
            ref["atomic_prdf"][site_idx]
        ), f"Wrong number of element pairs for site {site_idx}."
        for el_pair, prdf in site.items():
            assert (
                el_pair in ref["atomic_prdf"][site_idx]
            ), f"Element pair {el_pair} not in atomic prdf."
            assert all(
                [
                    abs(val0 - ref["atomic_prdf"][site_idx][el_pair][idx]) < 1.0e-5
                    for idx, val0 in enumerate(prdf)
                ]
            ), f"Atomic prdf is wrong for element pair {el_pair} at site {site_idx}."


@pytest.mark.parametrize(
    "structure, r_max, max_shells",
    [
        ("Al_225_conv", 5.0, 3),
        ("NaCl_225_prim", 5.0, 3),
        ("Cs2Te_19_prim", 5.0, 2),
        ("Cs2Te_62_prim", 5.0, 2),
        ("GaAs_216_prim", 5.0, 3),
        ("GaAs_216_conv", 5.0, 3),
    ],
)
def test_warren_cowley_like_order_parameters(nested_dict_comparison, structure, r_max, max_shells):
    """Test calculation of warren cowley order parameters."""
    inputs = dict(load_yaml_file(STRUCTURES_PATH + structure + ".yaml"))
    ref = dict(load_yaml_file(WC_LIKE_ORDER_PATH + structure + "_ref.yaml"))
    strct_c = StructureCollection()
    strct_c.append(structure, **inputs)
    strct_ops = StructureOperations(strct_c)
    output = strct_ops[0].perform_analysis(
        method=calculate_warren_cowley_order_p,
        kwargs={"r_max": r_max, "max_shells": max_shells},
    )
    nested_dict_comparison(output, ref)


@pytest.mark.parametrize(
    "structure,file_type", [("Imidazole", "xyz"), ("ZIF-8_complex", "xyz"), ("ZIF-8", "cif")]
)
def test_planes(structure, file_type):
    """
    Test finding planes.
    """
    ref = load_yaml_file(PLANES_PATH + structure + "_ref.yaml")
    strct_collect = StructureCollection()
    strct_collect.append_from_file("structure", STRUCTURES_PATH + structure + "." + file_type)
    strct_ops = StructureOperations(strct_collect)
    planes = strct_ops["structure"].perform_analysis(
        method=calculate_planes, kwargs=ref["parameters"]
    )

    for plane, ref_plane in zip(planes, ref["reference"]):
        assert len(plane["site_indices"]) == len(
            ref_plane["site_indices"]
        ), "Number of site indices do not match."
        for site_idx in ref_plane["site_indices"]:
            assert site_idx in plane["site_indices"], f"Site index {site_idx} not found."
        for vect, ref_vect in zip(plane["plane"], ref_plane["plane"]):
            for coord, ref_coord in zip(vect, ref_vect):
                assert abs(coord - ref_coord) < 1e-4, "Vectors do not match."
        for proj_pos, ref_proj_pos in zip(plane["proj_positions"], ref_plane["proj_positions"]):
            assert (
                proj_pos["label"] == ref_proj_pos["label"]
            ), "Wrong label for projected position."
            for coord in "xy":
                assert (
                    abs(proj_pos[coord] - ref_proj_pos[coord]) < 1e-4
                ), "Coordinates of projected positions is wrong."


def test_stabilities(create_structure_collection_object):
    """Test calculate_stabilities function."""
    ref = load_yaml_file(STABILITIES_PATH + "MOFs_ref.yaml")
    strct_c, _ = create_structure_collection_object(["GaAs_216_conv"])
    for idx0, strct in enumerate(ref["input"]):
        strct_c.append("test_" + str(idx0), **strct)
    strct_ops = StructureOperations(strct_c)
    f_e, st = strct_ops.calculate_stabilities(unit="eV")
    f_e = f_e[1:]
    st = st[1:]
    assert all(
        abs(val - ref_val) < 1.0e-4 for val, ref_val in zip(f_e, ref["ref"]["formation_energies"])
    ), "Formation energies are wrong."
    assert all(
        abs(val - ref_val) < 1.0e-4 for val, ref_val in zip(st, ref["ref"]["stabilities"])
    ), "Stabilities are wrong."
