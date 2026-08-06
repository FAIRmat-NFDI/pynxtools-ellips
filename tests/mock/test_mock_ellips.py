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
"""Property test: for randomized angle counts and data types, WoollamParser's
per-label VDS {"link": ..., "shape": ...} entries must stay internally
consistent with measured_data's actual shape.
"""

import os
import random
from pathlib import Path

import pytest
import yaml
from mock_ellips import DATA_TYPES, MockEllips

from pynxtools_ellips.parsers.woollam import WoollamParser

TEST_DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def parsed_woollam() -> WoollamParser:
    with open(os.path.join(TEST_DATA_DIR, "eln_data.yaml"), encoding="utf8") as file:
        header_config = yaml.safe_load(file)

    parser = WoollamParser()
    parser.parse(
        os.path.join(TEST_DATA_DIR, "test-data.dat"), header_config=header_config
    )
    return parser


@pytest.mark.parametrize("seed", range(10))
def test_mock_shape_consistency(parsed_woollam: WoollamParser, seed: int) -> None:
    random.seed(seed)
    MockEllips(parsed_woollam).mock()

    data = parsed_woollam.data
    measured_data = data["measured_data"]
    n_angles, n_observables, n_spectrum = measured_data.shape

    assert data["measured_data_errors"].shape == measured_data.shape
    assert n_spectrum == len(data[f"{parsed_woollam.spectrum_type}_spectrum"])
    assert len(data["angle_of_incidence"]) == n_angles
    assert len(data["angle_of_detection"]) == n_angles
    assert len(parsed_woollam.data_labels) == n_angles * n_observables
    assert len(set(parsed_woollam.data_labels)) == len(parsed_woollam.data_labels)

    seen_indices = set()
    for label in parsed_woollam.data_labels:
        entry = data[label]
        assert entry["link"] == "/entry/data_collection/measured_data"
        angle_idx, obs_idx, spectrum_slice = entry["shape"]
        assert 0 <= angle_idx < n_angles
        assert 0 <= obs_idx < n_observables
        assert spectrum_slice == slice(None)
        seen_indices.add((angle_idx, obs_idx))

        errors_entry = data[f"{label}_errors"]
        assert errors_entry["link"] == "/entry/data_collection/measured_data_errors"
        assert errors_entry["shape"] == entry["shape"]

    # Every (angle, observable) combination is covered exactly once - no
    # missing or duplicate slice, which is what an off-by-one in the
    # label/index bookkeeping would produce.
    assert seen_indices == {
        (a, o) for a in range(n_angles) for o in range(n_observables)
    }


@pytest.mark.parametrize("data_type", DATA_TYPES)
def test_mock_covers_each_data_type(
    parsed_woollam: WoollamParser, data_type: str
) -> None:
    expected_observables = {
        "Psi/Delta": 2,
        "tan(Psi)/cos(Delta)": 2,
        "Mueller matrix": 16,
    }
    MockEllips(parsed_woollam).mock(n_angles=2, data_type=data_type)

    n_angles, n_observables, _ = parsed_woollam.data["measured_data"].shape
    assert n_angles == 2
    assert n_observables == expected_observables[data_type]
