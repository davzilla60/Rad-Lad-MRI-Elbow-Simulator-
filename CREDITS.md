# Credits

## MRI imaging — "Elbow Patient 4 (Stock video)"

**Adapted from:** three Shutterstock 4K stock clips of a DICOM viewer scrolling an elbow MRI:
shutterstock_3814450591 (sagittal T1), shutterstock_3814451857 (coronal, probably T2 TSE) and
shutterstock_3814452021 (axial T1). These are used under the Shutterstock licence held by Rad-Lad.

**This is not scanner data.** The slices were recovered from the video frames.

### Changes made

1. Each clip was split into its unique slices, taken from runs of identical frames between hard cuts, and decoded
   as 10-bit luma. Pixel values are display brightness, not MR signal.
2. Geometry is estimated:
   - in-plane scale from the anatomy (radial head ≈ 22 mm), giving 0.25 mm pixels after 4× downsampling;
   - slice spacing of 4.4 mm (SAG), 3.3 mm (COR) and 5.0 mm (AX);
   - the series' relative positions are set by hand (SAG 13, COR 11 and AX 11 at the joint centre).
3. A burned-in ruler on sagittal slice 1 (in air) was blacked out.
4. **Localisers** are simulated. Neighbouring slices were averaged into an 8 mm slab and resampled to a 180 mm /
   256 grid. Contrast was flattened, then local-coil shading, k-space truncation (256 × 160) and Rician noise were
   added (`../elbow-mri/localisers.py`). The localiser animation is a real inverse FFT of those images.
5. In the browser the images are cropped to the planned FOV. Two effects are added there: **wrap-around** when the
   FOV is narrower than the arm in the phase direction, and an intensity gradient for the off-centre
   (elbow-by-the-side) position. Neither is present in the source data.
6. A right elbow is inferred from the anatomy and the localiser's R marker. It wasn't recorded.
7. Sequences other than SAG T1, COR T2 and AX T1 are listed for teaching only. There are no images for them.

Educational simulation. It isn't a medical device and isn't for clinical use.
