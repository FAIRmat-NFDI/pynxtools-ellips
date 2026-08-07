# Convert data from the command line

This is the terse reference version of [Tutorial > Convert your first ellipsometry dataset](../tutorial/convert_your_first_dataset.md) — copy-paste commands, no explanations.

## J.A. Woollam VASE/CompleteEASE `.dat` export + ELN

```shell
pynx convert examples/eln_data.yaml examples/test-data.dat --reader ellips --nxdl NXellipsometry --output SiO2onSi_example.nxs
```

Both files are required: the ELN yaml declares the `.dat` file's column layout (`colnames`/`sep`/`skip`), so `pynx` can't parse the vendor file without it. Order doesn't matter — the reader always reads the ELN first.

## What each flag does

- `--reader ellips` — selects the `pynxtools-ellips` reader.
- `--nxdl NXellipsometry` — the application definition the output should conform to.
- `--output <file>.nxs` — where to write the result.
- the `.yaml` file — the ELN metadata (and `.dat` parser configuration), detected by its extension.
- the `.dat` file — the raw VASE/CompleteEASE export, detected by its extension.

## Inspect the result

Open the generated `.nxs` file with [H5Web](https://h5web.panosc.eu/h5wasm){:target="_blank" rel="noopener"}, the VS Code H5Web extension, or any HDF5 viewer.
