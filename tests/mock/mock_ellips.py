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

"""Randomizes a real, already-parsed WoollamParser's angle count and data
type in place, for property-testing that the reader's shape/VDS handling
(parsers/woollam.py's per-label {"link": ..., "shape": ...} entries) stays
internally consistent across configurations that aren't covered by the one
real example file (tests/data/test-data.dat: 3 angles, Psi/Delta).
"""

import random

import numpy as np

from pynxtools_ellips.parsers.woollam import WoollamParser

__all__ = ["MockEllips"]

ANGLE_POOL = [40, 45, 50, 55, 60, 65, 70, 75, 80]
DATA_TYPES = ["Psi/Delta", "tan(Psi)/cos(Delta)", "Mueller matrix"]


def _labels_for(data_type: str, angles: list[int]) -> dict[str, list[str]]:
    """Mirrors parsers.woollam._header_labels's label-naming convention."""
    if data_type == "Psi/Delta":
        names = ["Psi", "Delta"]
    elif data_type == "tan(Psi)/cos(Delta)":
        names = ["tan(Psi)", "cos(Delta)"]
    else:
        names = [f"m{i}{j}" for i in range(1, 5) for j in range(1, 5)]

    labels: dict[str, list[str]] = {name: [] for name in names}
    for angle in angles:
        for name in names:
            labels[name].append(f"{name}_{angle}deg")
    return labels


class MockEllips:
    """Rebuilds a real WoollamParser's measured_data/data_labels/per-label
    VDS entries for a randomized angle count and data type, keeping shapes
    internally consistent - same spectrum length as the real parse, but a
    different (angles x observables) grid.
    """

    def __init__(self, parser: WoollamParser) -> None:
        self.parser = parser
        self.n_spectrum = parser.data["measured_data"].shape[2]

    def mock(self, n_angles: int | None = None, data_type: str | None = None) -> None:
        """Rebuild self.parser.data/data_labels in place for a randomized
        (or given) angle count and data type."""
        n_angles = n_angles or random.randint(1, 4)
        data_type = data_type or random.choice(DATA_TYPES)
        angles = sorted(random.sample(ANGLE_POOL, n_angles))
        labels = _labels_for(data_type, angles)

        n_observables = len(labels)
        shape = (n_angles, n_observables, self.n_spectrum)
        self.parser.data["measured_data"] = np.random.uniform(0, 180, shape)
        self.parser.data["measured_data_errors"] = np.random.uniform(0, 1, shape)
        self.parser.data["angle_of_incidence"] = np.array(angles)
        self.parser.data["angle_of_detection"] = np.array(angles)

        data_list = list(labels.values())
        self.parser.data_labels = [key for val in data_list for key in val]
        for dindx, val in enumerate(data_list):
            for index, key in enumerate(val):
                self.parser.data[key] = {
                    "link": "/entry/data_collection/measured_data",
                    "shape": np.index_exp[index, dindx, :],
                }
                self.parser.data[f"{key}_errors"] = {
                    "link": "/entry/data_collection/measured_data_errors",
                    "shape": np.index_exp[index, dindx, :],
                }
                if dindx == 0 and index == 0:
                    self.parser.data[f"{key}_long_name"] = "mock plot (degree)"
