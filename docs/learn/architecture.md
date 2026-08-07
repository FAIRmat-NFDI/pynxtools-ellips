# Reader architecture

`pynxtools-ellips` is a `pynxtools` reader plugin, built on `pynxtools`'s [`MultiFormatReader`](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html){:target="_blank" rel="noopener"}. This page explains how the pieces fit together and, more importantly, where a new vendor format would go.

## One reader, dispatched by file extension

`EllipsometryReader` (`src/pynxtools_ellips/reader.py`) registers as the `ellips` entry point. It routes input files by extension:

| Extension | Handler | What it does |
| --------- | ------- | ------------- |
| `.yaml` / `.yml` | `handle_eln_file` | Reads the ELN metadata file — both for NeXus template content (flattened via `CONVERT_DICT`/`REPLACE_NESTED`, kept on the reader unchanged from earlier versions of this plugin) and for the parser configuration (`colnames`/`sep`/`skip`/`filename`) the `.dat` file needs to be read at all. |
| `.dat` | `handle_dat_file` | Parses a J.A. Woollam VASE/CompleteEASE export via `WoollamParser`. |

The ELN must be processed first — `self.processing_order = [".yaml", ".yml", ".dat"]` guarantees that regardless of the order files are passed on the command line, since the `.dat` file's column layout isn't self-describing and has to come from the ELN.

## How the ELN is handled

Most `pynxtools` plugins route *all* NeXus content — ELN-sourced and instrument-file-sourced alike — through the config file's `@eln`/`@attrs`/`@data` tokens, with every path spelled out explicitly. `pynxtools-ellips` only does that for the handful of paths that come from the parsed `.dat` file (see below); the ELN's own content is written directly by `handle_eln_file` via the existing `flatten_and_replace`/`CONVERT_DICT` mechanism.

## The config file and wildcards

`config/config_woollam.json` only covers what the ELN's own structure can't: the parsed measurement data, and the repeated per-angle/per-observable fields (`Psi_50deg`, `Delta_60deg`, ...). The repeated fields are added using `MultiFormatReader`'s wildcard mechanism:

```json
"/ENTRY[entry]/data_collection/DATA[*]": "@data:*",
"/ENTRY[entry]/data_collection/DATA[*]/@units": "degree",
"/ENTRY[entry]/data_collection/FIELDNAME_errors[*_errors]": "@data:*_errors"
```

`EllipsometryReader.get_data_dims()` returns the parser's list of field labels (`["Psi_50deg", "Psi_60deg", ..., "Delta_70deg"]`); for each label, `pynxtools` expands `*` in both the key and the value, so `DATA[*]` becomes one concrete template entry per label.

## The parser

`WoollamParser` (`src/pynxtools_ellips/parsers/woollam.py`) subclasses a small shared base, `_EllipsParser` (`parsers/base.py`):

- `matches_file(file)` — a cheap structural check (the acquisition-method marker `VASEmethod[` near the top of the file), not just an extension check.
- `_parse(file, header_config=...)` — populates `self.data` with the measurement arrays and, for each per-angle/per-observable field, a `{"link": ..., "shape": np.index_exp[...]}` entry requesting a sliced HDF5 virtual dataset — see [Learn > Application definitions](appdefs.md) for why this has to be a slice rather than the full array.
- `post_process(eln_data)` — derives `atom_types` from the sample's chemical formula if the ELN didn't already provide one.

If a second vendor parser is added, `parsers/base.py` is the contract to implement against 

## Adding a second vendor

1. Add a new parser module under `parsers/`, subclassing `_EllipsParser`.
2. Register its file extension in `EllipsometryReader.__init__`'s `self.extensions`.
3. If its data doesn't fit the existing `config_woollam.json` mapping, add a new config file and a way to select it in the reader.
4. Add real vendor example data under `examples/<vendor>/`, following the pattern in [Tutorial > Convert your first ellipsometry dataset](../tutorial/convert_your_first_dataset.md).
