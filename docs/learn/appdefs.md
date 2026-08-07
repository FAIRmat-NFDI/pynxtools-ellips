# NXoptical_spectroscopy and NXellipsometry

[`NXellipsometry`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXellipsometry.html){:target="_blank" rel="noopener"} is the NeXus application definition this reader converts into. It builds on the more generic [`NXoptical_spectroscopy`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXoptical_spectroscopy.html){:target="_blank" rel="noopener"} base structure (entry, instrument, sample, user) and adds ellipsometry-specific concepts under `ENTRY/data_collection`, `ENTRY/instrument`, and `ENTRY/derived_parameters`.

## The `data_collection` group

`ENTRY/data_collection` is an `NXdata` group holding both the raw measurement and its NeXus default-plot metadata:

- **`measured_data`** — the full result set, shape `(N_measurements, N_observables, N_spectrum)`. For a VASE/CompleteEASE Psi/Delta scan, `N_measurements` is the number of angles of incidence, `N_observables` is 2 (Psi, Delta), and `N_spectrum` is the number of wavelength points.
- **`NAME_spectrum`** (e.g. `wavelength_spectrum`) — the 1D spectral axis, length `N_spectrum`.
- **`DATA[*]`** (e.g. `Psi_50deg`, `Delta_60deg`) — one field per (angle, observable) combination, each a **1D slice** of `measured_data` along the spectrum dimension.

## Why the default-plot signal must be 1D, not 3D

NeXus's `NXdata` convention requires the `@signal` field's shape to line up dimension-by-dimension with its `@axes` field(s) — a viewer like h5web reads `@signal`/`@axes` and expects `signal.shape[i] == len(axes[i])`. `measured_data` is intentionally 3D (the application definition says so explicitly), but `wavelength_spectrum` is 1D, so `measured_data` itself can never be the default-plot `@signal` — only a 1D slice of it can be.

That's what the per-field `DATA[Psi_50deg]` etc. entries are for: each is written as an HDF5 **virtual dataset (VDS)** — a `{"link": "/entry/data_collection/measured_data", "shape": np.index_exp[angle_index, observable_index, :]}` template entry — a real, separate 1D dataset that shares storage with `measured_data` rather than copying it. `data_collection/@signal` points at the first of these (e.g. `Psi_50deg`), `@axes` points at `wavelength`, and `@auxiliary_signals` lists the rest, so h5web (or any NeXus-aware viewer) can render a proper multi-line default plot.
