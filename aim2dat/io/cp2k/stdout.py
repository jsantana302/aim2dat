"""Functions to read the standard output file of CP2K."""

# Internal library imports
from aim2dat.io.base_parser import transform_str_value, parse_block_function, _BaseDataBlock


class CP2KBlock(_BaseDataBlock):
    """CP2K| data block."""

    start_str = "CP2K|"
    use_once = True

    def _parse_line(self, line):
        if "version string:" in line:
            self.current_data["cp2k_version"] = " ".join(line.split()[5:])


class GlobalBlock(_BaseDataBlock):
    """GLOBAL| data block."""

    start_str = "GLOBAL|"
    use_once = True

    def _parse_line(self, line):
        if "Run type" in line:
            self.current_data["run_type"] = " ".join(line.split()[3:])


class BrillouinBlock(_BaseDataBlock):
    """BRILLOUIN| data block."""

    start_str = "BRILLOUIN|"
    end_str = "***"
    use_once = True

    def __init__(self):
        """Initialize class."""
        _BaseDataBlock.__init__(self)
        self.in_kpoint_block = False

    def _parse_line(self, line):
        if "K-point scheme" in line:
            self.current_data["kpoint_scheme"] = line.split()[-1]
        elif "K-Point grid" in line:
            line_sp = line.split()
            self.current_data["kpoint_grid"] = [
                int(line_sp[-3]),
                int(line_sp[-2]),
                int(line_sp[-1]),
            ]
        elif "Number" in line and "Weight" in line:
            self.in_kpoint_block = True
            self.current_data["kpoints"] = []
        elif self.in_kpoint_block:
            if self.end_str in line:
                self.in_kpoint_block = False
                return None
            line_sp = line.split()
            self.current_data["kpoints"].append(
                {
                    "idx": int(line_sp[1]),
                    "weight": float(line_sp[2]),
                    "kpoint": [float(line_sp[3]), float(line_sp[4]), float(line_sp[5])],
                }
            )


class DFTBlock(_BaseDataBlock):
    """DFT| data block."""

    start_str = "DFT|"
    use_once = True

    def _parse_line(self, line):
        if "Kohn-Sham" in line:
            self.current_data["dft_type"] = line.split()[-1]
        elif "Multiplicity" in line:
            self.current_data["multiplicity"] = int(line.split()[-1])
        elif "Charge" in line:
            self.current_data["charge"] = float(line.split()[-1])


class FunctionalBlock(_BaseDataBlock):
    """FUNCTIONAL| data block."""

    start_str = "FUNCTIONAL|"
    use_once = True

    def _parse_line(self, line):
        xc_info = self.current_data.setdefault("xc", {})
        if line.endswith(":\n"):
            new_value = line[13:-2]
            fct = xc_info.pop("functional", None)
            if fct is None:
                fct = new_value
            elif isinstance(fct, str):
                fct = [fct, new_value]
            else:
                fct.append(new_value)
            xc_info["functional"] = fct


class VdWBlock(_BaseDataBlock):
    """vdW POTENTIAL| data block."""

    start_str = "vdW POTENTIAL|"
    use_once = True

    def _parse_line(self, line):
        # Get first and second line:
        xc_info = self.current_data.setdefault("xc", {})
        if len(xc_info) == 0:
            xc_info["vdw_type"] = " ".join(line.split()[2:])
        elif len(xc_info) == 1:
            xc_info["vdw_method"] = line.split()[2]


class MDParBlock(_BaseDataBlock):
    """MD_PAR| data block."""

    start_str = "MD_PAR|"
    use_once = True

    def _parse_line(self, line):
        if "Ensemble type" in line:
            self.current_data["md_ensemble"] = line.split()[-1]


class MDIniBlock(_BaseDataBlock):
    """MD_INI| data block."""

    _pattern_mapping = [
        ("Potential energy", "potential_energy"),
        ("Kinetic energy", "kinetic_energy"),
        ("Temperature", "temperature"),
    ]
    start_str = "MD_INI|"
    use_once = True

    def _parse_line(self, line):
        md_ini = self.current_data.setdefault(
            "md_ini", {"step_nr": 0, "time_fs": 0.0, "index": self.line_indices[0]}
        )
        for pattern, key in self._pattern_mapping:
            if pattern in line:
                md_ini[key] = float(line.split()[-1])


class MDBlock(_BaseDataBlock):
    """MD| data block."""

    _pattern_mapping = [
        ("Energy drift per atom", "energy_drift_p_atom"),
        ("Potential energy", "potential_energy"),
        ("Kinetic energy", "kinetic_energy"),
        ("Temperature", "temperature"),
    ]
    start_str = "MD|"

    def _parse_line(self, line):
        if "Step number" in line:
            self.current_data["step_nr"] = int(line.split()[-1])
        elif "Time [fs]" in line:
            self.current_data["time_fs"] = float(line.split()[-1])
        for pattern, key in self._pattern_mapping:
            if pattern in line:
                self.current_data[key] = float(line.split()[-2])

    def _process_output(self):
        if len(self.line_indices) > 0:
            return {"md_steps": self.all_data, "motion_indices": self.line_indices}


class NumbersBlock(_BaseDataBlock):
    """Numbers data block."""

    start_str = "TOTAL NUMBERS AND MAXIMUM NUMBERS"
    end_str = "SCF PARAMETERS"
    use_once = True

    def _parse_line(self, line):
        if "Atoms:" in line:
            self.current_data["natoms"] = int(line.split()[-1])


class KindInfoBlock(_BaseDataBlock):
    """Kind info data block."""

    start_str = "ATOMIC COORDINATES IN"
    end_str = "SCF PARAMETERS"
    use_once = True

    def _parse_line(self, line):
        line = line.strip()
        if line == "" or line.startswith(("Atom", "SCF", "MODULE")):
            return None

        ki_list = self.current_data.setdefault("kind_info", [])
        line_sp = line.split()
        ki_list.append(
            {
                "kind": int(line_sp[1]),
                "element": line_sp[2],
                "atomic_nr": int(line_sp[3]),
                "core_electrons": int(int(line_sp[3]) - float(line_sp[7])),
                "valence_electrons": int(float(line_sp[7])),
                "mass": float(line_sp[8]),
            }
        )


class SCFParametersBlock(_BaseDataBlock):
    """SCF parameters data block."""

    start_str = "SCF PARAMETERS"

    def _parse_line(self, line):
        if "added MOs" in line:
            line_sp = line.split()
            if line_sp[-1] != "0":
                self.current_data["nr_unocc_orbitals"] = [int(line_sp[-2]), int(line_sp[-1])]
            else:
                self.current_data["nr_unocc_orbitals"] = int(line_sp[-2])


class SPGRBlock(_BaseDataBlock):
    """SPGR| data block."""

    _pattern_mapping = [
        ("SPACE GROUP NUMBER:", "sg_number"),
        ("INTERNATIONAL SYMBOL:", "int_symbol"),
        ("POINT GROUP SYMBOL:", "point_group_symbol"),
        ("SCHOENFLIES SYMBOL:", "schoenflies_symbol"),
    ]
    start_str = "SPGR|"

    def _parse_line(self, line):
        sg_info = self.current_data.setdefault("spgr_info", {})
        for pattern, key in self._pattern_mapping:
            if pattern in line:
                sg_info[key] = line.split()[-1]
        if "sg_number" in sg_info:
            sg_info["sg_number"] = int(sg_info["sg_number"])


class SCFBlock(_BaseDataBlock):
    """SCF cycles data block."""

    _pattern_mapping = [
        ("Number of electrons:", "nelectrons"),
        ("Number of occupied orbitals:", "nr_occ_orbitals"),
    ]
    _all_keys = [
        "nelectrons",
        "nr_occ_orbitals",
        "scf_converged",
        "energy_scf",
        "energy",
        "energy_units",
    ]  # , "nr_scf_steps"
    start_str = "Number of electrons:"
    end_str = "ENERGY| Total FORCE_EVAL"

    def _parse_line(self, line):
        for pattern, key in self._pattern_mapping:
            if pattern in line:
                self.current_data.setdefault(key, []).append(int(line.split()[-1]))
                return None

        if "SCF run converged in" in line:
            self.current_data["nr_scf_steps"] = int(line.split()[-3])
            self.current_data["scf_converged"] = True
            return True
        elif "Leaving inner SCF loop after" in line:
            self.current_data["nr_scf_steps"] = int(line.split()[-2])
            self.current_data["scf_converged"] = False
            return True
        elif "outer SCF loop converged in" in line:
            self.current_data["nr_scf_steps"] = int(line.split()[-2])
            self.current_data["scf_converged"] = True
            return True
        elif "outer SCF loop FAILED to converge after" in line:
            self.current_data["nr_scf_steps"] = int(line.split()[-2])
            self.current_data["scf_converged"] = False
            return True
        elif "Total energy:" in line:
            self.current_data["energy_scf"] = float(line.split()[-1])
            return True
        elif "ENERGY| Total FORCE_EVAL" in line:
            self.current_data["energy"] = float(line.split()[-1])
            line = line.replace("]", "[")
            self.current_data["energy_units"] = line.split("[")[1]

    def _process_output(self):
        for scf_step in self.all_data:
            for _, key in self._pattern_mapping:
                val = scf_step.get(key, [])
                if len(val) == 1:
                    scf_step[key] = val[0]
        output = {"scf_steps": self.all_data, "scf_indices": self.line_indices}

        # Adds the last complete SCF-step here:
        c0 = len(self.all_data) - 1
        while c0 > -1:
            if all(key in self.all_data[c0] for key in self._all_keys):
                for key in self._all_keys:
                    output[key] = self.all_data[c0][key]
                break
            c0 -= 1
        return output


class MullikenBlock(_BaseDataBlock):
    """Mulliken charges data block."""

    start_str = "Mulliken Population Analysis"
    end_str = "# Total charge"
    current_data_type = list

    def _parse_line(self, line):
        line = line.strip()
        if line == "" or line.startswith("#") or line.startswith("Mulliken"):
            return None

        line_sp = line.split()
        pc_dict = {
            "kind": int(line_sp[2]),
            "element": line_sp[1],
        }
        if len(line_sp) == 7:
            pc_dict["population"] = [float(line_sp[3]), float(line_sp[4])]
            pc_dict["charge"] = float(line_sp[5])
        else:
            pc_dict["population"] = float(line_sp[3])
            pc_dict["charge"] = float(line_sp[4])
        self.current_data.append(pc_dict)

    def _process_output(self):
        return {"mulliken": self.all_data}


class HirshfeldBlock(_BaseDataBlock):
    """Hirshfeld charges data block."""

    start_str = "Hirshfeld Charges"
    end_str = "Total Charge"
    current_data_type = list

    def _parse_line(self, line):
        line = line.strip()
        if (
            line == ""
            or line.startswith("#")
            or line.startswith("Hirshfeld")
            or line.startswith("Total")
        ):
            return None
        line_sp = line.split()
        pc_dict = {
            "kind": int(line_sp[2]),
            "element": line_sp[1],
        }
        if len(line_sp) == 8:
            pc_dict["population"] = [float(line_sp[4]), float(line_sp[5])]
            pc_dict["charge"] = float(line_sp[7])
        else:
            pc_dict["population"] = float(line_sp[4])
            pc_dict["charge"] = float(line_sp[5])
        self.current_data.append(pc_dict)

    def _process_output(self):
        return {"hirshfeld": self.all_data}


class OptStepBlock(_BaseDataBlock):
    """Optimization step data block."""

    start_str = "OPTIMIZATION STEP:"
    end_str = "--------------------------"
    current_data_type = list

    def _parse_line(self, line):
        pass

    def _process_output(self):
        if len(self.line_indices) > 0:
            return {"motion_indices": self.line_indices}


class StepInformationBlock(_BaseDataBlock):
    """Opt step information data block."""

    start_str = "--------  Informations at step ="
    end_str = "---------------------------------------------------"

    def _parse_line(self, line):
        line_sp = line.split("=")
        if len(line_sp) < 2:
            return None

        if "---" in line_sp[0]:
            self.current_data["nr_steps"] = int(line_sp[1].split()[0])
        else:
            value = transform_str_value(line_sp[1])
            self.current_data["_".join(line_sp[0].split()).lower()] = value

    def _process_output(self):
        if len(self.all_data) > 0:
            return {"nr_steps": self.all_data[-1]["nr_steps"], "motion_steps": self.all_data}


class OptSuccessBlock(_BaseDataBlock):
    """Opt success data block."""

    start_str = "GEOMETRY OPTIMIZATION COMPLETED"
    end_str = "***"
    use_once = True

    def _parse_line(self, line):
        if self.start_str in line:
            self.current_data["geo_converged"] = self.line_indices[-1]


class MaxOptStepsBlock(_BaseDataBlock):
    """Opt max steps reched data block."""

    start_str = "MAXIMUM NUMBER OF OPTIMIZATION STEPS REACHED"
    end_str = "EXITING GEOMETRY OPTIMIZATION"
    use_once = True

    def _parse_line(self, line):
        if self.start_str in line:
            self.current_data["geo_not_converged"] = True


class WalltimeBlock(_BaseDataBlock):
    """Walltime exceeded data block."""

    start_str = "GEO run terminated - exceeded requested execution time:"
    use_once = True

    def _parse_line(self, line):
        if self.start_str in line:
            self.current_data["exceeded_walltime"] = True


class BandsBlock(_BaseDataBlock):
    """Band structure data block."""

    start_str = "Band Structure Calculation"
    end_str = "ENERGY|"

    def _parse_line(self, line):
        line_sp = line.split()
        if "KPOINTS|" in line:
            if "Special point" in line:
                if "not specifi" in line:
                    self.current_data.setdefault("labels", []).append(None)
                else:
                    self.current_data.setdefault("labels", []).append(line_sp[4])
            elif "Number of k-points in set" in line:
                self.current_data.setdefault("label_pos", []).append(int(line_sp[-1]))
        elif line.startswith("#"):
            if line_sp[2] == "Energy":
                self.current_data["bands_unit"] = line_sp[3][1:-1]
            elif line_sp[4] == "1:":
                self.current_data.setdefault("kpoints", []).append(
                    [float(line_sp[5]), float(line_sp[6]), float(line_sp[7])]
                )
                for idx in range(2):
                    self.current_data.setdefault("bands", [[], []])[idx].append([])
                    self.current_data.setdefault("occupations", [[], []])[idx].append([])
                self.current_data["spin"] = 0
            elif line_sp[4] == "2:":
                self.current_data["spin"] = 1
        elif len(line_sp) < 3:
            return None
        elif line_sp[0].isdigit():
            self.current_data["bands"][self.current_data["spin"]][-1].append(float(line_sp[1]))
            self.current_data["occupations"][self.current_data["spin"]][-1].append(
                float(line_sp[2])
            )

    def _process_output(self):
        if len(self.all_data) > 0 and len(self.all_data[0]) > 0:
            kpt_data = self.all_data[0]
            if kpt_data.pop("spin") == 0:
                kpt_data["bands"] = kpt_data["bands"][0]
                kpt_data["occupations"] = kpt_data["occupations"][0]
            label_pos = kpt_data.pop("label_pos")
            labels = kpt_data.pop("labels")
            last_pos = -1
            labels_w_pos = []
            for idx, pos in enumerate(label_pos):
                labels_w_pos.append([last_pos + 1, labels[idx * 2]])
                last_pos += pos
                labels_w_pos.append([last_pos, labels[idx * 2 + 1]])
            kpt_data["labels"] = labels_w_pos
            return {"kpoint_data": kpt_data}


class EigenvaluesBlock(_BaseDataBlock):
    """Eigenvalues data block."""

    start_str = "EIGENVALUES AND"
    end_str = ["Fermi energy:", "E(Fermi):"]

    def _parse_line(self, line):
        line_sp = line.split()
        if len(line_sp) < 3:
            return None

        if "EIGENVALUES" in line:
            self.current_data["idx"] = int(line_sp[-1]) if "POINT" in line else 0
            self.current_data["alpha"] = "ALPHA" in line
            self.current_data["beta"] = "BETA" in line
        elif line_sp[1].isdigit() or line_sp[0].isdigit():
            energies = self.current_data.setdefault("energies", [])
            occupations = self.current_data.setdefault("occupations", [])
            if "MO|" in line:
                energy = float(line_sp[-3])
            else:
                energy = float(line_sp[-2])
            occ = float(line_sp[-1])
            if occ >= 0.5:
                self.current_data["vbm"] = energy
            elif "cbm" not in self.current_data:
                self.current_data["cbm"] = energy
            energies.append(energy)
            occupations.append(occ)

        elif "E(Fermi):" in line or "Fermi energy:" in line:
            self.current_data["fermi_energy"] = float(line_sp[2])

    def _process_output(self):
        ev_output = {"eigenvalues": []}
        gap_keys = ["vbm", "cbm", "gap"]
        gap_info = {key: [[], []] for key in gap_keys}
        fermi_energy = None
        for ev_data in self.all_data:
            ev_data["gap"] = ev_data["cbm"] - ev_data["vbm"]
            gap_info0 = {key: ev_data[key] for key in gap_keys}
            del ev_data["vbm"]
            del ev_data["cbm"]
            idx = 0
            if ev_data.pop("beta", False):
                # Double-check that k-points are in right order:
                if ev_data["idx"] != ev_output["eigenvalues"][-1]["idx"]:
                    raise ValueError("Wrong order of k-points.")
                idx = 1
                for key in ["energies", "occupations", "gap"]:
                    ev_output["eigenvalues"][-1][key].append(ev_data[key])
            else:
                if ev_data.pop("alpha", False):
                    for key in ["energies", "occupations", "gap"]:
                        ev_data[key] = [ev_data[key]]
                ev_output["eigenvalues"].append(ev_data)
            for key, val in gap_info0.items():
                gap_info[key][idx].append(val)
            fermi_energy = ev_data.pop("fermi_energy")
        if len(gap_info["cbm"][0]) > 0:
            if len(gap_info["vbm"][1]) > 0:
                ev_output["gap"] = min(
                    [
                        max(min(gap_info["cbm"][idx]) - max(gap_info["vbm"][idx]), 0.0)
                        for idx in range(2)
                    ]
                )
                ev_output["direct_gap"] = min(
                    [max(min(gap_info["gap"][idx]), 0.0) for idx in range(2)]
                )
            else:
                ev_output["gap"] = max(min(gap_info["cbm"][0]) - max(gap_info["vbm"][0]), 0.0)
                ev_output["direct_gap"] = max(min(gap_info["gap"][0]), 0.0)
        if len(ev_output["eigenvalues"]) > 0:
            return {"fermi_energy": fermi_energy, "eigenvalues_info": ev_output}


class RuntimeBlock(_BaseDataBlock):
    """Runtime data block."""

    start_str = "T I M I N G"
    end_str = "The number of warnings for this run is"
    use_once = True

    def _parse_line(self, line):
        if "CP2K" in line:
            self.current_data["runtime"] = float(line.split()[-1])


class WarningBlock(_BaseDataBlock):
    """Warning data block."""

    start_str = "*** WARNING"

    def _parse_line(self, line):
        line_sp = line.split()
        if self.start_str in line:
            file_name, line_number = line_sp[3].split(":")
            self.current_data["file_name"] = file_name
            self.current_data["line_number"] = line_number
            self.current_data["message"] = " ".join(line_sp[5:-1])
        elif len(line_sp) > 1:
            self.current_data["message"] += " " + " ".join(line_sp[1:-1])

    def _process_output(self):
        output = {"warnings": self.all_data}
        if len(self.all_data) > 0:
            output["nwarnings"] = len(self.all_data)
        return output


class ErrorBlock(_BaseDataBlock):
    """Error data block."""

    start_str = "[ABORT]"
    end_str = "* / \\"
    use_once = True

    def _parse_line(self, line):
        if self.start_str in line:
            self.current_data["message"] = ""
        elif self.end_str in line:
            file_name, line_number = line.split()[3].split(":")
            self.current_data["file_name"] = file_name
            self.current_data["line_number"] = line_number
        else:
            message = " ".join(line[12:78].split())
            if self.current_data["message"] != "" and len(message) > 0:
                self.current_data["message"] += " "
            self.current_data["message"] += message

    def _process_output(self):
        if len(self.all_data) > 0:
            return {"errors": self.all_data, "aborted": True}


_BLOCKS = {
    "standard": [
        CP2KBlock,
        GlobalBlock,
        BrillouinBlock,
        DFTBlock,
        FunctionalBlock,
        VdWBlock,
        MDParBlock,
        NumbersBlock,
        SCFParametersBlock,
        SPGRBlock,
        RuntimeBlock,
        SCFBlock,
        StepInformationBlock,
        MaxOptStepsBlock,
        BandsBlock,
        EigenvaluesBlock,
        WalltimeBlock,
        WarningBlock,
        ErrorBlock,
    ],
    "trajectory": [
        CP2KBlock,
        GlobalBlock,
        BrillouinBlock,
        DFTBlock,
        FunctionalBlock,
        VdWBlock,
        MDParBlock,
        NumbersBlock,
        KindInfoBlock,
        SCFParametersBlock,
        SPGRBlock,
        RuntimeBlock,
        SCFBlock,
        MullikenBlock,
        HirshfeldBlock,
        OptStepBlock,
        StepInformationBlock,
        OptSuccessBlock,
        MaxOptStepsBlock,
        MDIniBlock,
        MDBlock,
        WalltimeBlock,
        WarningBlock,
        ErrorBlock,
    ],
    "partial_charges": [
        CP2KBlock,
        GlobalBlock,
        BrillouinBlock,
        DFTBlock,
        FunctionalBlock,
        VdWBlock,
        MDParBlock,
        NumbersBlock,
        KindInfoBlock,
        SCFParametersBlock,
        SPGRBlock,
        RuntimeBlock,
        SCFBlock,
        MullikenBlock,
        HirshfeldBlock,
        StepInformationBlock,
        MaxOptStepsBlock,
        WalltimeBlock,
        WarningBlock,
        ErrorBlock,
    ],
}


_WARNING_MAPPING = [
    ("Using a non-square number of", "Using a non-square number of MPI ranks."),
    ("SCF run NOT converged", "One or more SCF run did not converge."),
    ("Specific L-BFGS convergence criteria", "LBFGS converged with specific criteria."),
    ("Add more MOs for proper smearing", "Add more MOs for proper smearing."),
]

_ERROR_MAPPING = [
    ("exceeded requested execution time", "exceeded_walltime"),
    ("Use the LSD option for an odd number of electrons", "odd_nr_electrons"),
    ("Extra MOs (ADDED_MOS) are required for smearing", "need_added_mos"),
    ("exceeded requested execution time", "exceeded_walltime"),
    ("Cholesky decompose failed", "cholesky_decompose_failed"),
    ("Bad condition number R_COND", "bad_condition_number"),
]

_MOTION_STEP_MAPPING = {
    "max._step_size": "max_step",
    "rms_step_size": "rms_step",
    "max._gradient": "max_grad",
    "rms_gradient": "rms_grad",
    "internal_pressure_[bar]": "pressure",
    "potential_energy": "potential_energy",
    "kinetic_energy": "kinetic_energy",
    "temperature": "temperature",
    "energy_drift_p_atom": "energy_drift_p_atom",
    "step_nr": "step_nr",
    "time_fs": "time_fs",
}


def read_stdout(file_name: str, parser_type: str = "standard") -> dict:
    """
    Read standard output file of CP2K.

    Parameters
    ----------
    file_name : str
        Path to the output file.
    parser_type : str
        Defines the quantities that are being parsed. Supported options are ``'standard'``,
        ``'partial_charges'`` and ``'trajectory'``.

    Returns
    -------
    dict
        Dictionary containing the parsed values.
    """
    output, n_lines = parse_block_function(file_name, _BLOCKS[parser_type])
    output["cp2k_version"] = float(output["cp2k_version"])
    if "exceeded_walltime" not in output:
        output["exceeded_walltime"] = False
    if "md_ensemble" in output:
        output["run_type"] += "-" + output.pop("md_ensemble")
    if "runtime" not in output:
        output.pop("nwarnings", None)
        output["energy_units"] = "a.u."
        output["interrupted"] = True

    warnings = []
    for warn0 in output.get("warnings", []):
        for warn1 in _WARNING_MAPPING:
            if warn1[0] in warn0["message"]:
                warnings.append(warn1[1])
    output["warnings"] = warnings

    errors = output.pop("errors", [])
    for err0 in errors:
        if "SCF run NOT converged." in err0["message"]:
            output["scf_converged"] = False
        for err1 in _ERROR_MAPPING:
            if err1[0] in err0["message"]:
                output[err1[1]] = True

    kpoints = output.pop("kpoints", [])
    if "eigenvalues_info" in output:
        for ev in output["eigenvalues_info"]["eigenvalues"]:
            if len(kpoints) > 0:
                for idx, kpt in enumerate(kpoints):
                    if kpt["idx"] == ev["idx"]:
                        break
                ev["weight"] = kpt["weight"]
                ev["kpoint"] = kpt["kpoint"]
                del kpoints[idx]
            del ev["idx"]

    motion_steps = output.pop("motion_steps", [])
    motion_indices = output.pop("motion_indices", [])
    if "geo_converged" in output:
        motion_indices.append(output.pop("geo_converged"))
    motion_indices.append(n_lines)
    if "md_ini" in output:
        md_ini = output.pop("md_ini")
        motion_indices = [md_ini.pop("index")] + motion_indices[:-1]
        motion_steps = [md_ini] + output.pop("md_steps", [])
    scf_steps = output.pop("scf_steps", [])
    scf_indices = output.pop("scf_indices", [])
    pc = {}
    for pc_type in ["mulliken", "hirshfeld"]:
        if pc_type in output and len(output[pc_type]) > 0:
            pc[pc_type] = output.pop(pc_type)
            if parser_type == "partial_charges":
                output[pc_type] = pc[pc_type][-1]

    if parser_type == "trajectory":
        output["motion_step_info"] = []
        c_scf_steps = 0
        for step_idx, line_idx in enumerate(motion_indices):
            m_step = {"scf_steps": []}
            if step_idx < len(motion_steps):
                for key, val in motion_steps[step_idx].items():
                    if key in _MOTION_STEP_MAPPING:
                        m_step[_MOTION_STEP_MAPPING[key]] = val

            while c_scf_steps < len(scf_steps):
                if scf_indices[c_scf_steps] > line_idx:
                    break

                scf_step = {}
                for key in ["nr_scf_steps", "scf_converged", "energy"]:
                    if key in scf_steps[c_scf_steps]:
                        scf_step[key] = scf_steps[c_scf_steps][key]
                for pc_type, values in pc.items():
                    if c_scf_steps < len(values):
                        scf_step[pc_type] = values[c_scf_steps]
                m_step["scf_steps"].append(scf_step)
                c_scf_steps += 1

            if len(m_step["scf_steps"]) == 1:
                m_step.update(m_step.pop("scf_steps")[0])
            elif len(m_step["scf_steps"]) == 0:
                del m_step["scf_steps"]
            output["motion_step_info"].append(m_step)
    else:
        output.pop("motion_step_info", None)
    return output
