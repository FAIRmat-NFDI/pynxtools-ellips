#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Parses J.A. Woollam VASE/CompleteEASE tabular ellipsometry exports."""

import math
import os
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
from pynxtools.dataconverter.helpers import extract_atom_types

from pynxtools_ellips.parsers.base import _EllipsParser

__all__ = ["WoollamParser"]

DEFAULT_HEADER = {"sep": "\t", "skip": 0}


class WoollamParser(_EllipsParser):
    """
    Parses a J.A. Woollam VASE/CompleteEASE tabular export (e.g. RC2
    ellipsometer data): a flat column-per-signal table with one row per
    (angle of incidence, wavelength) pair, repeated per angle in blocks.

    Unlike most pynxtools-plugin parsers, the *column layout* of the export
    (column names, separator, header lines to skip) is not self-describing -
    it is declared in the accompanying ELN yaml (``colnames``/``sep``/``skip``/
    ``filename``), which is why ``_parse`` takes that raw ELN dict as
    ``header_config`` rather than relying on ``self.data`` alone.
    """

    supported_file_extensions = (".dat",)
    supported_vendor = "J.A. Woollam Co."

    def __init__(self) -> None:
        super().__init__()
        self.data_labels: list[str] = []
        self.plot_name: str = ""
        self.spectrum_type: str = ""
        self.spectrum_unit: str = ""

    def matches_file(self, file: Path) -> bool:
        """A VASE/CompleteEASE export declares its acquisition method on the
        second line, e.g. ``VASEmethod[EllipsometerType=4, ...]``."""
        try:
            with open(file, encoding="utf-8") as woollam_file:
                head = "".join(line for _, line in zip(range(5), woollam_file))
        except OSError:
            return False
        return "VASEmethod[" in head

    def _parse(self, file: Path, **kwargs) -> None:
        header_config = cast(dict[str, Any] | None, kwargs.get("header_config"))
        if header_config is None:
            raise ValueError("header_config is required")

        header = dict(DEFAULT_HEADER)
        header.update(header_config)
        if "sep" in header_config:
            header["sep"] = (
                header_config["sep"].encode("utf-8").decode("unicode_escape")
            )

        whole_data = _load_as_pandas_array(file, header)

        unique_angles, counts = _data_set_dims(whole_data)
        labels = _header_labels(header, unique_angles)

        measured_data, measured_data_errors = _data_array(
            whole_data, unique_angles, counts, labels
        )
        self.data["measured_data"] = measured_data
        self.data["measured_data_errors"] = measured_data_errors

        derived_parameter_type = cast(str, header["derived_parameter_type"])

        self.data[derived_parameter_type] = _parameter_array(
            whole_data, header, unique_angles, counts
        )

        header_data = cast(dict[str, Any], header["Data"])

        spectrum_type = cast(str, header_data["spectrum_type"])
        spectrum_unit = cast(str, header_data["spectrum_unit"])
        colnames = cast(list[str], header["colnames"])

        if spectrum_type not in colnames:
            raise ValueError(f"spectrum type '{spectrum_type}' not found in 'colnames'")

        self.spectrum_type = spectrum_type
        self.spectrum_unit = (
            "angstrom" if spectrum_unit == "Angstroms" else spectrum_unit
        )
        self.data[f"{spectrum_type}_spectrum"] = (
            whole_data[spectrum_type].to_numpy()[0 : counts[0]].astype("float64")
        )

        self.data["angle_of_detection"] = unique_angles
        self.data["angle_of_incidence"] = unique_angles

        self.plot_name = cast(str, header["plot_name"])
        data_list = list(labels.values())
        self.data_labels = [key for val in data_list for key in val]
        for dindx, val in enumerate(data_list):
            for index, key in enumerate(val):
                self.data[key] = {
                    "link": "/entry/data_collection/measured_data",
                    "shape": np.index_exp[index, dindx, :],
                }
                self.data[f"{key}_errors"] = {
                    "link": "/entry/data_collection/measured_data_errors",
                    "shape": np.index_exp[index, dindx, :],
                }
                if dindx == 0 and index == 0:
                    self.data[f"{key}_long_name"] = f"{self.plot_name} (degree)"

    def post_process(self, eln_data: dict[str, Any]) -> None:
        atom_types_key = "/ENTRY[entry]/SAMPLE[sample]/atom_types"
        formula_key = "/ENTRY[entry]/SAMPLE[sample]/chemical_formula"
        if atom_types_key not in eln_data and formula_key in eln_data:
            self.data["atom_types"] = extract_atom_types(eln_data[formula_key])


def _load_as_pandas_array(my_file, header):
    """Load a CSV output file using the header dict.
    Use the fields: colnames, skip and sep from the header
    to instruct the csv reader about:
    colnames    -- column names
    skip        -- how many lines to skip
    sep         -- separator character in the file
    """
    required_parameters = ("colnames", "skip", "sep")
    for required_parameter in required_parameters:
        if required_parameter not in header:
            raise ValueError("colnames, skip and sep are required header parameters!")

    if not os.path.isfile(my_file):
        raise OSError(f"File not found error: {my_file}")

    return pd.read_csv(
        my_file,
        # use header = None and names to define custom column names
        header=None,
        names=header["colnames"],
        skiprows=header["skip"],
        delimiter=header["sep"],
    )


def _header_labels(header, unique_angles):
    """Define data labels (column names)"""

    if header["Data"]["data_type"] == "Psi/Delta":
        labels = {"Psi": [], "Delta": []}
    elif header["Data"]["data_type"] == "tan(Psi)/cos(Delta)":
        labels = {"tan(Psi)": [], "cos(Delta)": []}
    else:
        labels = {}
        for i in range(1, 5):
            for j in range(1, 5):
                labels.update({f"m{i}{j}": []})

    for angle in enumerate(unique_angles):
        for key, val in labels.items():
            val.append(f"{key}_{int(angle[1])}deg")

    return labels


def _data_set_dims(whole_data):
    """User defined variables to produce slices of the whole data set"""
    energy = whole_data["type"].astype(str).values.tolist().count("E")
    unique_angles, counts = np.unique(
        whole_data["angle_of_incidence"].to_numpy()[0:energy].astype("int64"),
        return_counts=True,
    )

    return unique_angles, counts


def _parameter_array(whole_data, header, unique_angles, counts):
    """User defined variables to produce slices of the whole data set"""
    my_data_array = np.empty([len(unique_angles), 1, counts[0]])

    block_idx = [np.int64(0)]
    index = 0
    while index < len(whole_data):
        index += counts[0]
        block_idx.append(index)

    # derived parameters:
    # takes last but one column from the right (skips empty columns):
    data_index = 1
    temp = (
        whole_data[header["colnames"][-data_index]]
        .to_numpy()[block_idx[-1] - 1]
        .astype("float64")
    )

    while math.isnan(temp):
        temp = (
            whole_data[header["colnames"][-data_index]]
            .to_numpy()[block_idx[-1] - 1]
            .astype("float64")
        )
        data_index += 1

    for index in range(len(unique_angles)):
        my_data_array[index, 0, :] = (
            whole_data[header["colnames"][-data_index]]
            .to_numpy()[block_idx[index + 6] : block_idx[index + 7]]
            .astype("float64")
        )

    return my_data_array


def _data_array(whole_data, unique_angles, counts, labels):
    """User defined variables to produce slices of the whole data set"""

    my_data_array = np.empty([len(unique_angles), len(labels), counts[0]])
    my_error_array = np.empty([len(unique_angles), len(labels), counts[0]])

    block_idx = [np.int64(0)]
    index = 0
    while index < len(whole_data):
        index += counts[0]
        block_idx.append(index)

    data_index = 0
    for key, val in labels.items():
        for index in range(len(val)):
            my_data_array[index, data_index, :] = (
                whole_data[key]
                .to_numpy()[block_idx[index] : block_idx[index + 1]]
                .astype("float64")
            )
        data_index += 1

    data_index = 0
    for key, val in labels.items():
        for index in range(len(val)):
            my_error_array[index, data_index, :] = (
                whole_data[f"err.{key}"]
                .to_numpy()[block_idx[index] : block_idx[index + 1]]
                .astype("float64")
            )
        data_index += 1

    return my_data_array, my_error_array
