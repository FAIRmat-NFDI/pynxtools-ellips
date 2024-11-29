"""
Basic example based test for the Ellips reader
"""

import os

import pytest
from pynxtools.testing.nexus_conversion import ReaderTest

module_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "nxdl,reader_name,files_or_dir",
    [
        ("NXellipsometry", "ellips", f"{module_dir}/data"),
    ],
)
def test_ellips_reader(nxdl, reader_name, files_or_dir, tmp_path, caplog):
    "Generic test from pynxtools."
    # This ignores the software_TYPE/@version attribute
    ignore_sections: Dict[str, List[str]] = {
        "===== ATTRS (//entry/instrument/software_NeXuS/program@version)": [
            "DEBUG - value:"
        ],
    }

    test = ReaderTest(nxdl, reader_name, files_or_dir, tmp_path, caplog)
    test.convert_to_nexus(caplog_level="ERROR", ignore_undocumented=True)
    test.check_reproducibility_of_nexus(ignore_sections=ignore_sections)
