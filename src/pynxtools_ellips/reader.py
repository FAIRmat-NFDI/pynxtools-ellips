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
"""MultiFormatReader-based reader for ellipsometry data."""

import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import yaml
from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import FlattenSettings, flatten_and_replace

from pynxtools_ellips.parsers.base import _EllipsParser
from pynxtools_ellips.parsers.sentech import SentechParser
from pynxtools_ellips.parsers.woollam import WoollamParser

logger = logging.getLogger("pynxtools")

CONVERT_DICT = {
    "unit": "@units",
    "detector": "detector_TYPE[detector_ccd]",
    "Data": "data_collection",
    "derived_parameters": "derived_parameters",
    "environment": "environment_conditions",
    "instrument": "INSTRUMENT[instrument]",
    "sample": "SAMPLE[sample]",
    "sample_stage": "sample_stage",
    "user": "USER[user]",
    "instrument/angle_of_incidence": "INSTRUMENT[instrument]/angle_of_incidence",
    "instrument/angle_of_incidence/unit": "INSTRUMENT[instrument]/angle_of_incidence/@units",
    "data_software": "data_software/program",
    "experiment_identifier/identifier": "IDENTIFIER[experiment_identifier]/IDENTIFIER[identifier]",
    "experiment_identifier/is_persistent": "IDENTIFIER[experiment_identifier]/IS_PERSISTENT[is_persistent]",
    "software_RC2": "software_TYPE[software_RC2]/program",
    "software_RC2/@url": "software_TYPE[software_RC2]/program/@url",
    "software_RC2/@version": "software_TYPE[software_RC2]/program/@version",
    "instrument_calibration_RC2": "instrument_calibration_DEVICE[instrument_calibration_RC2]",
    "instrument_calibration_RC2/calibration_status": "instrument_calibration_DEVICE[instrument_calibration_RC2]/calibration_status",
    "environment": "ENVIRONMENT[environment_sample]",
    "notes": "NOTE[notes]",
    "light_source": "source_TYPE[source_light]",
    "source_type": "type",
    "rotating_element/unit": "rotating_element/revolutions/@units",
    "beam_source": "beam_TYPE[beam_source]",
}

# Keys that are parser configuration (column layout, plot/derived-parameter
# naming) rather than NeXus content - excluded from the ELN flattening below,
# read directly from the raw ELN dict by WoollamParser instead.
_CONFIG_KEYS = [
    "colnames",
    "derived_parameter_type",
    "err-var",
    "filename",
    "parameters",
    "plot_name",
    "sep",
    "skip",
    "spectrum_type",
    "spectrum_unit",
]

REPLACE_NESTED = {
    "Inc_Det_Angles": "INSTRUMENT[instrument]",
    "Instrument": "INSTRUMENT[instrument]",
}


class EllipsometryReader(MultiFormatReader):
    """Reads ellipsometry vendor exports (J.A. Woollam VASE/CompleteEASE,
    and - structurally, not yet verified against a real export - Sentech
    SpectraRay) plus an ELN yaml into a NeXus template.
    """

    supported_nxdls = ["NXellipsometry"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The Woollam .dat file's column layout is declared in the ELN yaml
        # (colnames/sep/skip/filename), so the ELN must be read first. The
        # Sentech .csv format is self-describing and doesn't need this.
        self.processing_order = [".yaml", ".yml", ".dat", ".csv"]
        self.extensions = {
            ".yaml": self.handle_eln_file,
            ".yml": self.handle_eln_file,
            ".dat": self.handle_dat_file,
            ".csv": self.handle_csv_file,
            ".json": self.set_config_file,
        }
        self.config_file = str(Path(__file__).parent / "config" / "config_woollam.json")

        self._eln_config: dict[str, Any] = {}
        self.parser: _EllipsParser | None = None

    def set_config_file(self, file_path: Path) -> dict[str, Any]:
        if self.config_file is not None:
            logger.info(
                f"Config file already set. Replaced by the new file {file_path}."
            )
        self.config_file = file_path
        return {}

    def handle_eln_file(self, file_path: str) -> dict[str, Any]:
        """Reads the ELN yaml for two purposes: flattening it into NeXus
        template entries (via CONVERT_DICT/REPLACE_NESTED, same as any
        pynxtools ELN), and exposing the raw dict as parser configuration
        (colnames/sep/skip/filename) that WoollamParser needs to read the
        vendor .dat file - see _CONFIG_KEYS above.
        """
        with open(file_path, encoding="utf8") as file:
            self._eln_config = yaml.safe_load(file)

        eln_data_dict = flatten_and_replace(
            FlattenSettings(
                dic=dict(self._eln_config),
                convert_dict=CONVERT_DICT,
                replace_nested=REPLACE_NESTED,
                ignore_keys=_CONFIG_KEYS,
            )
        )
        self.eln_data = eln_data_dict
        return eln_data_dict

    def handle_dat_file(self, file_path: str) -> dict[str, Any]:
        if not self._eln_config:
            raise OSError(
                "The ELN yaml (with colnames/sep/skip configuration) must be "
                "provided alongside the vendor .dat file."
            )
        if not WoollamParser.is_mainfile(file_path):
            logger.warning(
                f"{file_path} does not look like a Woollam VASE/CompleteEASE "
                "export; skipping."
            )
            return {}

        parser = WoollamParser()
        parser.parse(file_path, header_config=self._eln_config)
        self.parser = parser
        self.data = parser.data
        return {}

    def handle_csv_file(self, file_path: str) -> dict[str, Any]:
        if not SentechParser.is_mainfile(file_path):
            logger.warning(
                f"{file_path} does not look like a Sentech SpectraRay export; skipping."
            )
            return {}

        parser = SentechParser()
        parser.parse(file_path)
        self.parser = parser
        self.data = parser.data
        return {}

    def get_data(self, key: str, path: str) -> Any:
        return self.data.get(path or key)

    def get_data_dims(self, key: str, path: str) -> list[str]:
        if self.parser is None:
            return []
        return self.parser.data_labels

    def setup_template(self) -> dict[str, Any]:
        entries = {
            "/ENTRY[entry]/INSTRUMENT[instrument]/software_TYPE[software_NeXus]/program": "pynxtools",
            "/ENTRY[entry]/INSTRUMENT[instrument]/software_TYPE[software_NeXus]/program/@url": "https://github.com/FAIRmat-NFDI/pynxtools",
        }
        try:
            entries[
                "/ENTRY[entry]/INSTRUMENT[instrument]/software_TYPE[software_NeXus]/program/@version"
            ] = version("pynxtools")
        except PackageNotFoundError:
            pass
        return entries

    def post_process(self) -> dict[str, Any]:
        if self.parser is None:
            return {}

        self.parser.post_process(self.eln_data)

        spectrum_type = self.parser.spectrum_type
        entries: dict[str, Any] = {
            f"/ENTRY[entry]/data_collection/NAME_spectrum[{spectrum_type}_spectrum]": self.parser.data[
                f"{spectrum_type}_spectrum"
            ],
            f"/ENTRY[entry]/data_collection/AXISNAME[{spectrum_type}]": {
                "link": f"/entry/data_collection/{spectrum_type}_spectrum"
            },
            f"/ENTRY[entry]/data_collection/NAME_spectrum[{spectrum_type}_spectrum]/@units": self.parser.spectrum_unit,
            "/@default": "entry",
            "/ENTRY[entry]/@default": "data_collection",
            "/ENTRY[entry]/data_collection/@signal": self.parser.data_labels[0],
            "/ENTRY[entry]/data_collection/@axes": spectrum_type,
            "/ENTRY[entry]/data_collection/title": self.parser.plot_name,
            "/ENTRY[entry]/data_collection/@auxiliary_signals": self.parser.data_labels[
                1:
            ],
        }
        return entries


READER = EllipsometryReader
