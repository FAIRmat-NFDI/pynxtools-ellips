# Convert your first ellipsometry dataset

## Who is this tutorial for?

Anyone who has `pynxtools-ellips` installed and wants to see, hands-on, how an ellipsometry measurement turns into a standardized `NXellipsometry` file.

## What should you know before this tutorial?

- You should have `pynxtools-ellips` installed — see the [installation guide](installation.md).
- You should have a copy of the [`pynxtools-ellips` repository](https://github.com/FAIRmat-NFDI/pynxtools-ellips), since this tutorial uses the example files that ship with it.

## What will you know at the end of this tutorial?

- How the pieces of a conversion — raw data, an ELN file, and the `pynx convert` command — fit together.
- What a converted `NXellipsometry` file looks like.
- Where to go if you want to add a second vendor format.

## The example dataset

The repository ships a small, self-contained example under `examples/`: a J.A. Woollam VASE/CompleteEASE Psi/Delta scan of a 2nm SiO2 layer on Si, measured on an RC2 ellipsometer.

```text
examples/
├── test-data.dat    # the raw VASE/CompleteEASE export
└── eln_data.yaml     # metadata the raw export doesn't carry, plus its own column layout
```

Open `test-data.dat`: the first three lines are a title and acquisition-method header, then a flat table — one row per (angle of incidence, wavelength) pair, repeated in blocks for each of the three measured angles (50°, 60°, 70°). Open `eln_data.yaml` too: besides the usual instrument/sample/user metadata, it also declares `colnames`, `sep`, and `skip` — the column layout `test-data.dat` needs to be parsed at all, since the raw export doesn't describe its own columns.

## Steps

### 1. Run the conversion

From the root of the repository:

```console
pynx convert examples/eln_data.yaml examples/test-data.dat --reader ellips --nxdl NXellipsometry --output SiO2onSi_example.nxs
```

You're passing three things:

- the `.yaml` **ELN file**,
- the `.dat` **raw data file**,
- `--reader ellips --nxdl NXellipsometry`, selecting `pynxtools-ellips`'s reader and the `NXellipsometry` application definition.

The reader figures out which input file is which by extension, and reads the `.yaml` file first regardless of the order you pass them in — the `.dat` file's column layout depends on it (see [Learn > Reader architecture](../learn/architecture.md)).

### 2. Read the output

The command prints a handful of warnings about missing documentation for a few fields and attributes — expected for this example, and they don't stop the conversion.

At the end you should see:

```text
The output file generated: SiO2onSi_example.nxs.
```

### 3. Inspect the file

`SiO2onSi_example.nxs` is a regular HDF5 file. Open it with [H5Web](https://h5web.panosc.eu/h5wasm){:target="_blank" rel="noopener"} in your browser, the VS Code H5Web extension, or any HDF5 viewer. You should find, among others:

- `entry/data_collection/measured_data`: the full `(3, 2, 1088)` result array — 3 angles, 2 observables (Psi, Delta), 1088 wavelength points.
- `entry/data_collection/Psi_50deg`, `Delta_50deg`, ...: 1D virtual-dataset slices of `measured_data`, one per angle/observable — these are what the default plot actually shows, and why they have to be 1D rather than the full 3D array (see [Learn > Application definitions](../learn/appdefs.md)).
- `entry/sample/name`: `2nm SiO2 on Si`, taken straight from `eln_data.yaml`.
- The default plot itself, rendered by any NeXus-aware viewer from `data_collection`'s `@signal`/`@axes`/`@auxiliary_signals` attributes.

## Where to go next

- If you want to understand what's actually happening during the conversion, [Learn > Reader architecture](../learn/architecture.md) explains the design, and [Learn > Application definitions](../learn/appdefs.md) explains the NeXus concepts involved.
- For the bare command without the explanations, see [How-to > Convert data](../how-tos/convert_data.md).
- If you're adding a second vendor format, [Learn > Reader architecture](../learn/architecture.md#adding-a-second-vendor) has the checklist.
