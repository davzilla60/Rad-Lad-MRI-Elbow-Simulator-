# MR-I Ready — MRI Elbow

An embeddable, single-file teaching simulator for the Rad-Lad website. It uses the same engine and layout as the
"Scanogram" CT simulators, but for MRI. **It's a demonstration only.** It shows how much anatomy each plan would
cover in theory. Marker: **Elbow Grease** (all three planes cover the key anatomy with no wrap-around).

## Flow

1. **Patient set-up.** The patient arrives supine with the arm by the side. Choose one of three positions for a
   **right** elbow, and the 3-D MRI room (`room3d.js`, three.js from jsDelivr) changes pose straight away. A flexible
   receive coil is wrapped around the elbow in every pose:
   - prone with the arm overhead, elbow straight, palm up (the "superman" position);
   - supine with the arm overhead (backstroke);
   - supine with the elbow by the side.

   Each position comes with a short note on its trade-offs: isocentre and field uniformity against comfort and
   motion. `load` moves the table head first, lands the landmark laser on the coil, and sends the coil to isocentre.
   The magnet covers then fade so you can see the elbow inside the bore.
2. **Localiser.** The tri-plane 2D GRE localiser (sagittal, coronal, axial) is "acquired" line by line. Each image is
   rebuilt from its own k-space with an inverse FFT as the phase-encode lines fill, and the k-space panel shows the
   rows coming in.
3. **Protocol.** Plan the **axial**, **coronal** and **sagittal** sequences separately, in any order. Each plane's
   box shows on all three localisers and they stay linked: it's a slice stack on the two localisers it cuts across
   and a square FOV on the one parallel to it.
   - Drag the box to move it, drag the edges to change the coverage (number of slices) or the FOV, or use
     slices / thickness / gap / FOV.
   - The rail shows live which key structures are inside the stack, the estimated scan time, and a wrap-around
     warning when the FOV is narrower than the arm in the phase direction.
   - The preview panel shows the centre slice cropped to the FOV, with the wrap included.
   - Each plane lists the **sequences to consider**, which can be ticked (for example T1, PD FS / T2 FS, STIR,
     T2* GRE, 3D GRE / DESS, FABS, post-contrast T1 FS).
4. **Scan → images.** Each scan shows only the real slices that fall inside your stack, cropped to your FOV.
   - **Plan on completed sequences.** Each scanned series then appears in a "completed series" tray in the rail.
     Drag its thumbnail onto the localiser of the same plane, or tap it, and that localiser is replaced by the real
     images, so the later sequences are planned on sharper anatomy, as on a scanner. Scroll the panel to choose the
     slice, and press **↺ LOCALISER** to put the localiser back. A series dropped on a different plane's panel is
     refused with a note. CLI: `use ax|cor|sag`, `restore ax|cor|sag`.
5. **Debrief.** Coverage for each plane, the position note, three hero images, a sequences-to-consider table, and
   the marker.

Typical targets (mm from the joint centre):
- **AX:** distal humeral metaphysis (−38) to the radial tuberosity (+32).
- **COR:** anterior capsule (−18) to the triceps insertion (+24).
- **SAG:** medial epicondyle (−34) to the lateral epicondyle (+28).

## Files

- `elbow.embed.html` is the self-contained deliverable (~2.8 MB, every image inlined). `index.html` is an identical
  copy for one-drop hosting.
- `elbow.html` is the source. It loads `./assets/`, `assets/calib.js` and `room3d.js`. Run `python inline.py` to
  rebuild both deliverables.
- `room3d.js` is the procedural three.js MRI room: magnet, three poses and the elbow coil. The canvas is mirrored in
  CSS so the modelled arm reads as the patient's right; texture text is pre-mirrored. If you change it, bump
  `?v=N` in `elbow.html` **and** `inline.py` together.
- `assets/` holds:
  - `loc_sag/cor/ax.png`, the 256 px localisers;
  - `sag_NN` / `cor_NN` / `ax_NN`, the diagnostic slices (0.25 mm pixels);
  - `calib.json` / `calib.js` (geometry, slice positions, tissue extents);
  - the logos.
- `tools/gen_assets.py` rebuilds `assets/` from `../elbow-mri/slices` and `../elbow-mri/localisers`.

Debug hooks: `window.__mre` (`parse(cmd)`, `gotoPlan(q)`, `useSeries(q)`, `autoPlan()`, `analyse(q)`, `planOK(q)`, `S()`) and
`window.__room()` (`setPose`, `cam`, `snap`).

## Geometry caveat

The three diagnostic series came from separate stock clips, so they share no frame of reference. They're tied
together by hand: SAG slice 13, COR slice 11 and AX slice 11 are taken as passing through the joint centre, using
the estimated spacings of 4.4, 3.3 and 5.0 mm. That's accurate enough to show coverage, but not for measurement.
Stack angulation (obliquing the coronal to the epicondylar line, and so on) isn't simulated yet. It's mentioned in
the hints instead.
