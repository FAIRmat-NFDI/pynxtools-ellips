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
"""Abstract base class for ellipsometry vendor file-format parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

from pynxtools.dataconverter.helpers import extract_atom_types

__all__: list[str] = []


class _EllipsParser(ABC):
    """
    Base class every ellipsometry vendor-format parser subclasses.

    A parser populates ``self.data`` while parsing a vendor measurement file:
    measurement arrays, VDS ``{"link": ..., "shape": ...}`` field requests, and
    any scalar values needed by the reader's config file via the ``@data:``
    token. ``EllipsometryReader`` reads ELN metadata separately and passes it
    to ``post_process`` for any values that depend on it.

    ``data_labels``/``plot_name``/``spectrum_type``/``spectrum_unit`` are part
    of the contract (not just ``self.data`` content) because
    ``EllipsometryReader.get_data_dims``/``post_process`` read them directly,
    regardless of which vendor parser produced them.
    """

    supported_file_extensions: ClassVar[tuple[str, ...]] = ()
    supported_vendor: ClassVar[str | None] = None

    def __init__(self) -> None:
        self.file: Path | None = None
        self.data: dict[str, Any] = {}
        self.data_labels: list[str] = []
        self.plot_name: str = ""
        self.spectrum_type: str = ""
        self.spectrum_unit: str = ""

    @classmethod
    def is_extension_supported(cls, file: Path) -> bool:
        suffix = file.suffix.lower()
        return any(suffix == ext.lower() for ext in cls.supported_file_extensions)

    @abstractmethod
    def matches_file(self, file: Path) -> bool:
        """
        Return True if `file` structurally matches this parser's format.

        Implementations must perform positive identification - not just an
        extension check. Keep it cheap (read at most a few KB), and always
        catch exceptions internally and return False rather than raising.
        """

    def _is_mainfile(self, file: Path) -> None:
        """Raise ValueError with a specific reason if `file` isn't supported
        by this parser; return normally if it is."""
        if not self.is_extension_supported(file):
            allowed = ", ".join(self.supported_file_extensions) or "<none>"
            raise ValueError(
                f"Cannot process file '{file.name}' (extension "
                f"'{file.suffix or '<none>'}'). {type(self).__name__} only "
                f"supports: {allowed}."
            )
        if not self.matches_file(file):
            raise ValueError(
                f"File '{file.name}' does not match the expected format "
                f"for {type(self).__name__}."
            )

    @classmethod
    def is_mainfile(cls, file: str | Path) -> bool:
        """
        Safe, non-raising check: does this parser support `file`?

        Call this before `parse()` to decide whether to parse a file at
        all - a file that fails this check must not be parsed.
        """
        try:
            cls()._is_mainfile(Path(file))
            return True
        except ValueError:
            return False

    def parse(self, file: str | Path, **kwargs) -> None:
        """Parse `file`, populating self.data in place. Raises ValueError if
        `file` doesn't match this parser - callers should normally already
        have checked `is_mainfile()` first."""
        file = Path(file)
        self.file = file
        self._is_mainfile(file)
        self._parse(file, **kwargs)

    @abstractmethod
    def _parse(self, file: Path, **kwargs) -> None:
        """Populate self.data. Implemented by subclasses."""

    def post_process(self, eln_data: dict[str, Any]) -> None:
        """Derive fields that need ELN context, after the ELN file has been
        read. Default: fill in atom_types from the ELN's chemical_formula if
        the ELN didn't already provide one - vendor-agnostic, so every
        parser gets it for free; override per-parser for anything more
        specific. Mutates self.data in place."""
        atom_types_key = "/ENTRY[entry]/SAMPLE[sample]/atom_types"
        formula_key = "/ENTRY[entry]/SAMPLE[sample]/chemical_formula"
        if atom_types_key not in eln_data and formula_key in eln_data:
            self.data["atom_types"] = extract_atom_types(eln_data[formula_key])
