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
"""Parses Sentech SpectraRay tabular ellipsometry exports.

Ported from a pre-restructure reader (``reader_sentech.py``, predating both
the ``src/`` layout and ``MultiFormatReader``) onto the current
``_EllipsParser`` contract, without a real SpectraRay sample file to verify
against - kept structurally consistent with ``WoollamParser``, but the
extension, ``matches_file`` sniff, and units below are best-effort guesses
from the old code, not confirmed. Needs a real export to validate before
this is more than a structural placeholder.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from pynxtools_ellips.parsers.base import _EllipsParser

__all__ = ["SentechParser"]


def _columns_as_angles(columns: pd.Index) -> list[float]:
    """SpectraRay's angle-of-incidence column headers use a German-locale
    decimal comma, e.g. "50,0"."""
    return [float(str(col).replace(",", ".")) for col in columns]


class SentechParser(_EllipsParser):
    """
    Parses a Sentech SpectraRay tabular Psi/Delta export: a whitespace-
    separated table with wavelength as the row index and one *pair* of
    columns (Psi, Delta) per angle of incidence - unlike Woollam's export,
    the angle values are the column headers, not a data column, and the
    file is self-describing (no accompanying column-layout config needed).

    The old implementation also supported grouping multiple such files by an
    arbitrary axis via a JSON sidecar file's "measurement_set" key - that
    was never finished (it discarded the parsed data without writing it to
    a template) and isn't ported here; only the single-file case is.
    """

    supported_file_extensions = (".csv",)
    supported_vendor = "Sentech"

    def matches_file(self, file: Path) -> bool:
        """Best-effort, unverified: SpectraRay's own header row is the
        angle-of-incidence values themselves (German-locale decimal comma),
        so a real file's first line should parse entirely as such."""
        try:
            with open(file, encoding="utf-8") as sentech_file:
                header_line = sentech_file.readline()
            tokens = header_line.split()
            if len(tokens) < 3:
                return False
            _columns_as_angles(pd.Index(tokens[1:]))
        except (OSError, ValueError):
            return False
        return True

    def _parse(self, file: Path, **kwargs) -> None:
        frame = pd.read_csv(file, decimal=",", sep=r"\s+", index_col=0)
        n_wavelengths, n_columns = frame.shape
        if n_columns % 2 != 0:
            raise ValueError(
                f"Expected an even number of Psi/Delta column pairs in "
                f"'{file.name}', got {n_columns} columns."
            )

        angles = _columns_as_angles(frame.columns[::2])
        n_angles = len(angles)

        measured_data = np.empty((n_angles, 2, n_wavelengths))
        measured_data[:, 0, :] = frame.iloc[:, ::2].to_numpy().T
        measured_data[:, 1, :] = frame.iloc[:, 1::2].to_numpy().T
        self.data["measured_data"] = measured_data
        # SpectraRay's Psi/Delta export doesn't carry an uncertainty column
        # per value, unlike Woollam's - no measured_data_errors to report.

        self.data["angle_of_incidence"] = np.array(angles)
        self.data["angle_of_detection"] = np.array(angles)

        # TODO: unverified - SpectraRay conventionally exports wavelength in
        # nm, but this isn't confirmed against a real file.
        self.spectrum_type = "wavelength"
        self.spectrum_unit = "nm"
        self.data[f"{self.spectrum_type}_spectrum"] = frame.index.to_numpy().astype(
            "float64"
        )

        self.plot_name = "Psi and Delta"
        labels: dict[str, list[str]] = {"Psi": [], "Delta": []}
        for angle in angles:
            labels["Psi"].append(f"Psi_{angle:g}deg")
            labels["Delta"].append(f"Delta_{angle:g}deg")

        data_list = list(labels.values())
        self.data_labels = [key for val in data_list for key in val]
        for dindx, val in enumerate(data_list):
            for index, key in enumerate(val):
                self.data[key] = {
                    "link": "/entry/data_collection/measured_data",
                    "shape": np.index_exp[index, dindx, :],
                }
                if dindx == 0 and index == 0:
                    self.data[f"{key}_long_name"] = f"{self.plot_name} (degree)"
