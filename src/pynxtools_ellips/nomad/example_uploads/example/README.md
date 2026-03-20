# Ellipsometry example

## Introduction

This example demonstrates how NOMAD platform can convert, standardize, and store ellipsometry data. It shows the generation of a NeXus file according to the [`NXellipsometry`](https://manual.nexusformat.org/classes/applications/NXellipsometry.html#nxellipsometry) application definition and a successive analysis of an example data set (measured values of the ellipsometric angles Psi and Delta of SiO2 on Si).

## Viewing uploaded data

Below, you find an overview of your uploaded data.
Click on the `> /` button to get a list of your files or select **FILES** from the top menu of this upload.
You may add your own files to the upload or experiment with the pre-existing electronic lab notebook (ELN) example.
The ELN follows the general structure of NOMAD ELN templates. You can learn about NOMAD ELNs in the [documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/manage/eln.html).
When the ELN is saved, a NeXus file will be generated from the provided example data.
You may also view your supplied or generated NeXus files here with the H5Web viewer.
To do so open the **FILES** tab and select a `.nxs` file.

### Filelist

- Measurement data: test-data.dat
- Metadata file: eln_data.yaml
- Notebook with instructions: Ellipsometry workflow example.ipynb
- NeXus file: SiO2onSi.ellips.nxs (will be created when running the notebook)

## Analyzing the data

One option to start an analysis is using the [nomad-north-jupyter](https://github.com/FAIRmat-NFDI/nomad-north-jupyter) tool from the **NOMAD Remote Tools Hub**. This provides a docker container with a jupyterlab instance that has all readers from `pynxtools` installed. Your `uploads` should be mounted into this container. Please refer to the documentation of [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools.git) and the documentation of the NORTH as a NOMAD service for further details.

## Where to go from here?

If you're interested in using this pipeline and NOMAD in general you'll find support at [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).

For questions regarding the experiment or this specific example [contact the developers](https://fairmat-nfdi.github.io/pynxtools-ellips/contact.html) of this example upload.

If you want to learn more about analysis tools for ellipsometry like [pyElli](https://github.com/PyEllips/pyElli), feel free to explore their [documentation](https://pyelli.readthedocs.io/en/latest/).
