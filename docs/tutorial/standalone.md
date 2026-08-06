# Convert ellipsometry (meta)data to NeXus

## Who is this tutorial for?

This document is for people who want to standardize their research data by converting these
into a NeXus standardized format.

## What should you know before this tutorial?

- You should have a basic understanding of [FAIRmat NeXus](https://github.com/FAIRmat/nexus_definitions) and [pynxtools](https://github.com/FAIRmat/pynxtools)
- You should have a basic understanding of using Python and Jupyter notebooks via [JupyterLab](https://jupyter.org)

## What you will know at the end of this tutorial?

You will have a basic understanding how to use pynxtools-ellips for converting your ellipsometry data to a NeXus/HDF5 file.

## Steps

### Installation

See the [installation guide](installation.md) for how to install `pynxtools` together with the `ellips` reader plugin.

### Running the reader from the command line

An example script to run the `ellips` reader in `pynxtools`:

```shell
pynx convert eln_data.yaml test-data.dat --reader ellips --nxdl NXellipsometry --output SiO2onSi.nxs
```

Both the ELN yaml and the vendor `.dat` file must be passed explicitly. The `eln_data.yaml` serves two purposes at once: it's the carrier for metadata that are typically entered in an ELN such as in NOMAD, and it declares the `.dat` file's column layout (`colnames`/`sep`/`skip`), which the reader needs to read `test-data.dat` at all — see [Learn > Reader architecture](../learn/architecture.md).

# How to use it?

Navigate to the examples directory. Therein, execute the following command
which instructs the `ellips` reader to convert the example data using the `NXellipsometry` NeXus application definition resulting in a NeXus/HDF5 file:

### Examples

You can find examples how to use `pynxtools-ellips` for your ellipsometry research data pipeline in `src/pynxtools_ellips/nomad/examples_uploads/example`. That example is designed for working with [`NOMAD`](https://nomad-lab.eu/).

**Congrats! You now have a FAIR NeXus file!**

