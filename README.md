# 3D Cell Simulator

An interactive 3D animal cell you can rotate, zoom and click, plus printable / editable CAD models of the same cell.
브라우저에서 돌려 보고 눌러 보는 3D 동물세포 시뮬레이터와, 같은 세포의 3D 프린트·CAD 모델입니다.

## Features
- Drag to rotate, scroll / pinch to zoom, click an organelle to see its name and role (English + 한국어)
- Organelles: cell membrane, nucleus & nucleolus, mitochondria, endoplasmic reticulum, Golgi apparatus, ribosomes, lysosomes
- Hide the membrane to look inside
- Single-file web app (three.js r128 from a CDN), no build step

## Run
Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

Publish with GitHub Pages: Settings → Pages → Deploy from branch → `main` / root.

## 3D models (`models/`)
| File | Use |
|---|---|
| `dino_cell_full.stl` | 3D printing (mesh, ~80 mm wide, one watertight piece) |
| `dino_cell_full.step` | CAD editing, e.g. Fusion (true B-rep solids, mm) |

The membrane is a shell with windows so the inside is visible; organelles are tied to it with thin struts so the model prints as one piece. Ribosomes are limited to those on the ER.

## Rebuild the models
```bash
pip install -r requirements.txt
python3 scripts/make_stl.py
python3 scripts/make_step.py
```

## Notes
Organelle positions in the web app are random on each load; the CAD models use one fixed layout. This is a simplified teaching model, not to scale.

## License
MIT
