---
hide: toc
---

# Documentation for pynxtools-ellipsometry

pynxtools-ellipsometry is a free, and open-source data software for harmonizing ellipsometry data and metadata for research data management using [NeXus](https://www.nexusformat.org/), implemented with the goal to make scientific research data FAIR (findable, accessible, interoperable and reusable).

pynxtools-ellipsometry, which is a plugin for [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools), provides a tool for reading data from (currently Woollam VASE) proprietary and open data formats from technology partners and the wider ellipsometry community and standardizing it such that it is compliant with the NeXus application definitions [`NXopt`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXopt.html) and [`NXellipsometry`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXellipsometry.html), which is an extension of `NXopt`. pynxtools-ellipsometry is developed both as a standalone reader and as a tool within [NOMAD](https://nomad-lab.eu/), which is the open-source data management platform for materials science we are developing with [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).

pynxtools-ellipsometry solves the challenge of using heterogeneous and unfindable data formats which is common in the field of ellipsometry.

pynxtools-ellipsometry is useful for scientists from the ellipsometry community that deal with heterogeneous data, for technology partners and data providers looking for ways to make their data FAIRer, and for research groups that want to organize their data using NeXus and NOMAD.

<div markdown="block" class="home-grid">
<div markdown="block"> 

### Tutorial

A series of tutorials giving you an overview on how to store or convert your ellipsometry data to NeXus compliant files.

- [Installation guide](tutorial/installation.md)

</div>
<div markdown="block">

### How-to guides

How-to guides provide step-by-step instructions for a wide range of tasks, with the overarching topics:

</div>

<div markdown="block">

### Learn

The explanation section provides background knowledge on the implementation design, how the data is structured, how data processing can be incorporated, how the integration works in NOMAD, and more.

- [NXopt and NXellipsometry](explanation/appdefs.md)

</div>
<div markdown="block">

### Reference

Here you can learn which specific measurement setups and file formats from technology partners pynxtools-ellipsometry currently supports.

- [Woollam VASE](reference/vase.md)

</div>
</div>

<h2>Project and community</h2>

Any questions or suggestions? [Get in touch!](https://www.fair-di.eu/fairmat/about-fairmat/team-fairmat)
