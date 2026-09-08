# Sources and interpretation

## King identity

Official [King School homepage](https://www.kingschoolct.org/) links the seal via its organization metadata and its wordmark via its header resource. Downloaded 2026-09-08:

- https://www.kingschoolct.org/uploaded/themes/default_15/images/footerseal.svg
- https://resources.finalsite.net/images/v1641811484/kinglow/epdkrpk8fmefwjrrfsts/KingSchool.svg

The SVG source and rasterizations are retained. Logo ownership remains with King School; no open license is implied. The navy banner layout is reference-informed, not an official supplied production banner file. Only `King_banner.png` is used as a new image texture in the model.

## References already in the project

`references/interior_appearance/08_wide_commons_mezzanine.png` informed banner palette and seating colors; existing gallery locations come from the scene and supplied hallway views. `references/equipment/references/` supplied Bambu H2D with AMS, BigRep, Epson and UV flatbed appearance. Floorplan-derived locations and existing structural geometry remain the basis.

## Free-model check before rebuilding printers

Checked public searches for H2D / AMS 2 Pro CAD and BigRep ONE CAD. The Bambu community discussion is https://forum.bambulab.com/t/3d-cad-model-of-the-h2d-available/155678 . An H2D community listing was found at https://3dwarehouse.sketchup.com/model/cae32d0a-108f-470e-b883-e19c4cc798d2/H2D but an accessible download and reuse terms could not be verified in this session. No verified downloadable full BigRep model was obtained. This does not establish that none exists.

The existing project already contains manufacturer Formlabs CAD, which was retained. Other printer replacements in this revision are original parametric visualization geometry based on supplied photographs and existing envelopes. They are explicitly not manufacturer CAD or exact engineering replicas.

## Original additions and inherited materials

Plants, frames, geometric artwork, furniture refinements and new machine geometry are authored in `build_details.py`. Gallery artwork is an original decorative interpretation, not actual student work. Plant species and upholstery colors are illustrative choices.

The packed v02 ambientCG wood, fabric and plaster textures retain their existing CC0 provenance in `../v01/assets/SOURCES.md`. No new third-party plant or furniture meshes were imported.
