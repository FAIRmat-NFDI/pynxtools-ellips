# Convert ellipsometry data and metadata to NeXus

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

See [here](installation.md) for how to install pynxtools together with the `ellips` reader plugin.

### Running the reader from the command line

An example script to run the `ellips` reader in `pynxtools`:

```shell
dataconverter --reader ellips --nxdl NXellipsometry eln_data.yaml --output SiO2onSi.nxs
```

Note that the `eln_data.yaml` serves both as a carrier for metadata that are typically enter in an ELN such as in NOMAD
but serves at the time as a configuration file to instruct where the measured data can be found. The entry in `filename`
configures this. By default the measured data are stored in `test-data.dat`. Make sure that file is present in the
same directory as the `eln_data.yaml` file.

# How to use it?

Navigate to the examples directory. Therein, execute the following command
which instructs the `ellips` reader to convert the example data using the `NXellipsometry` NeXus application definition resulting in a NeXus/HDF5 file:

### Examples

You can find examples how to use `pynxtools-ellips` for your ellipsometry research data pipeline in `src/pynxtools_ellips/nomad/examples_uploads/example`. That example is designed for working with [`NOMAD`](https://nomad-lab.eu/).

**Congrats! You now have a FAIR NeXus file!**

