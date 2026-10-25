"""Build the simulator's image assets + geometry from the recovered Elbow Patient 4 slices.

    python tools/gen_assets.py      (run from the elbow-mri-sim folder)

Inputs (in ../elbow-mri): slices/{SAG,COR,AX}_NNN.png (16-bit, 0.0625 mm per pixel, from the stock clips)
and localisers/LOC_{SAG,COR,AX}.png (256 px synthetic tri-plane localiser, see ../elbow-mri/localisers.py).

Anatomical frame used everywhere in the sim (mm, origin = centre of the elbow joint):
  L  + lateral (radial side)      - right elbow: lateral is image LEFT on COR / AX
  A  + posterior                  - anterior is image LEFT on SAG, image TOP on AX
  Z  + distal                     - image DOWN on SAG / COR
Through-plane positions are the estimated spacings from build.py (SAG 4.4, COR 3.3, AX 5.0 mm),
anchored on hand-picked slices: SAG 13 = between trochlea and capitellum, COR 11 = mid-joint,
AX 11 = radiocapitellar joint line. Geometry is notional (the series had separate frames).
"""
import json, os, shutil
import numpy as np, cv2

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(HERE), 'elbow-mri')
OUT = os.path.join(HERE, 'assets')
SRC_PX, DS = 0.0625, 4
LOC_N, LOC_PX = 256, 180.0 / 256
# localisers.py placed source point C at localiser pixel (131, 122), scale SRC_PX / LOC_PX
LOC_C = {'sag': (1030, 930), 'cor': (830, 1120), 'ax': (1110, 1030)}
# series: count, spacing, anchor slice, origin (joint centre) in full-res source px, through-plane sign
SER = {
    'sag': dict(n=26, sp=4.4, k0=13, o=(1030, 1080), seq='T1 TSE'),
    'cor': dict(n=22, sp=3.3, k0=11, o=(823, 1134), seq='T2 TSE (no fat suppression)'),
    'ax':  dict(n=30, sp=5.0, k0=11, o=(1110, 1030), seq='T1 TSE'),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    calib = {'loc': {'n': LOC_N, 'px': LOC_PX}, 'ser': {}}
    s = SRC_PX / LOC_PX
    for p in ('sag', 'cor', 'ax'):
        shutil.copy(os.path.join(SRC, 'localisers', f'LOC_{p.upper()}.png'), os.path.join(OUT, f'loc_{p}.png'))
        o, c = SER[p]['o'], LOC_C[p]
        calib['loc'][p] = {'o': [round(131 + (o[0] - c[0]) * s, 2), round(122 + (o[1] - c[1]) * s, 2)]}
    for p, d in SER.items():
        imgs = [cv2.imread(os.path.join(SRC, 'slices', f'{p.upper()}_{k:03d}.png'), -1).astype(np.float32)
                for k in range(d['n'])]
        if p == 'sag':
            imgs[0][:, 1990:] = 0                       # burned-in ruler on the first slice (in air)
        allpx = np.concatenate([a[a > 3000].ravel()[::50] for a in imgs])
        lo, hi = np.percentile(allpx, [0.5, 99.6])
        ext = []
        hs = 1 if p == 'sag' else -1                     # image x -> mm along the panel's h axis (A or -L)
        for k, a in enumerate(imgs):
            a = cv2.resize(a, (a.shape[1] // DS, a.shape[0] // DS), interpolation=cv2.INTER_AREA)
            v = np.clip((a - lo) / (hi - lo), 0, 1) ** 0.95 * 255
            cv2.imwrite(os.path.join(OUT, f'{p}_{k:02d}.jpg'), v.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
            # tissue bounding box (mm, panel axes: h signed like the localiser panel, v down)
            m = cv2.morphologyEx((cv2.GaussianBlur(v, (0, 0), 2) > 28).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
            ys, xs = np.nonzero(m)
            if len(xs) < 200:
                ext.append(None); continue
            ox, oy = d['o'][0] / DS, d['o'][1] / DS
            hx = sorted([hs * (xs.min() - ox) * SRC_PX * DS, hs * (xs.max() - ox) * SRC_PX * DS])
            ext.append([round(hx[0], 1), round(hx[1], 1), round((ys.min() - oy) * SRC_PX * DS, 1), round((ys.max() - oy) * SRC_PX * DS, 1)])
        h, w = imgs[0].shape
        calib['ser'][p] = {'n': d['n'], 'sp': d['sp'], 'w': w // DS, 'h': h // DS, 'px': SRC_PX * DS,
                           'o': [d['o'][0] / DS, d['o'][1] / DS], 'seq': d['seq'], 'ext': ext,
                           'pos': [round((k - d['k0']) * d['sp'], 2) for k in range(d['n'])]}
        print(p, d['n'], 'slices', (w // DS, h // DS))
    for n in ('logo_full', 'logo_mark'):
        shutil.copy(os.path.join(os.path.dirname(HERE), 'wrist-scanogram', 'assets', n + '.png'), os.path.join(OUT, n + '.png'))
    json.dump(calib, open(os.path.join(OUT, 'calib.json'), 'w'), indent=1)
    open(os.path.join(OUT, 'calib.js'), 'w').write('window.MRE_CALIB=' + json.dumps(calib) + ';\n')
    print(json.dumps(calib['loc']))


if __name__ == '__main__':
    main()
