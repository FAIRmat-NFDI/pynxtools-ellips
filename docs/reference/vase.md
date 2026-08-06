# Data from Woollam instruments

The reader supports [VASE/CompleteEASE ellipsometry files exported from J.A. Woollam instruments](https://www.jawoollam.com/ellipsometry-software/completeease) in the `.dat` format, via `WoollamParser`.

- Parser: [`src/pynxtools_ellips/parsers/woollam.py`](https://github.com/FAIRmat-NFDI/pynxtools-ellips/blob/main/src/pynxtools_ellips/parsers/woollam.py)
- Config file: [`src/pynxtools_ellips/config/config_woollam.json`](https://github.com/FAIRmat-NFDI/pynxtools-ellips/blob/main/src/pynxtools_ellips/config/config_woollam.json)

See [Learn > Reader architecture](../learn/architecture.md) for how the pieces fit together.

## Example

An example dataset can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-ellips/tree/main/examples). Both the ELN file and the `.dat` data file need to be passed:

```console
pynx convert examples/eln_data.yaml examples/test-data.dat --reader ellips --nxdl NXellipsometry --output SiO2onSi.nxs
```

See [Tutorial > Convert your first ellipsometry dataset](../tutorial/convert_your_first_dataset.md) for a walkthrough.

## Acknowledgments

We thank Carola Emminger and Chris Sturm for providing the implementation and respective example data for this reader.
