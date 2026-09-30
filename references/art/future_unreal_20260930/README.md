# Art references: FUTURE UNREAL IMPLEMENTATION

Status: **DEFERRED — source photographs only.** Added on 2026-09-30 for later CampusCenter Unreal work. No artwork has been imported, modeled, textured, or placed in the Unreal scene by this addition.

## Source provenance

- Source archive: `fwd.zip`, supplied by the project owner on 2026-09-30
- The 12 original image payloads are stored individually here, unchanged, with their original filenames
- The untouched ZIP is retained separately in the project owner's Library; the ZIP itself is not included in this repository addition
- Size: 1,224,923 bytes
- SHA-256: `44feb642fc0d6241ecf19073a28e589de635e63687207065c616aaa69acf744b`
- Contents: 12 art photographs, 1,265,400 bytes uncompressed
- Inspection: all entry CRC checks passed and all images decoded; no unsafe paths, symlinks, duplicate filenames, encrypted entries, scripts, or executable files were found

See [`manifest.json`](manifest.json) for machine-readable hashes and import notes. Existing repository Git LFS rules are unchanged.

## Inventory

Dimensions below are intended display dimensions, accounting for EXIF orientation. Descriptions identify visible content rather than supplying artwork titles or attribution.

| File | Display pixels | Bytes | Visible content |
|---|---:|---:|---|
| `IMG_1758.jpeg` | 640 × 402 | 101,167 | Photograph of eight mannequins displaying colorful garments against a gallery wall |
| `IMG_1770.jpeg` | 640 × 480 | 90,469 | Photograph of a blue and an orange hand artwork with thin strings or cords extending upward |
| `IMG_1795.jpeg` | 640 × 480 | 90,738 | Wide gallery-wall photograph with large red/black abstract work and three smaller works below |
| `IMG_1820.jpeg` | 640 × 385 | 109,007 | Framed horizontal mixed-media artwork with layered colored forms and visible background text |
| `IMG_1869.jpeg` | 640 × 480 | 99,331 | Closer photograph of the same red/black abstract work seen in IMG_1795.jpeg |
| `IMG_2813.jpeg` | 480 × 640 | 71,308 | Cream ceramic teapot with orange handle/lid and colored curved-line decoration |
| `IMG_3037.jpeg` | 480 × 640 | 77,773 | Pale blue-gray ceramic teapot sculpture with two foot-like supports |
| `IMG_3248.jpeg` | 640 × 480 | 102,914 | Colorful wall-mounted cluster of stylized faces with pink backlighting |
| `IMG_3260.jpeg` | 480 × 482 | 124,042 | Circular blue Earth-like artwork on a dark speckled background |
| `IMG_4122.jpeg` | 427 × 640 | 28,591 | Monochrome sculpture of a hand holding a long rod, emerging from a cylindrical base |
| `IMG_6652.jpeg` | 480 × 640 | 134,508 | Mixed-media collage with prominent HOW DARE YOU text, blue diagonal section, and hanging red threads |
| `IMG_6988.jpeg` | 480 × 640 | 235,552 | Orange spiky-faced mixed-media wall sculpture with clock, traffic-light form, and assorted objects |

## Later implementation notes

- Preserve the original archive and filenames. Create any cropped, color-converted, or reoriented images as separate derivatives during a later implementation task.
- These are photographic references, not meshes, Unreal asset packages, or complete PBR texture sets. Placement, physical scale, cropping, and modeling are still to be determined.
- `IMG_3037.jpeg` and `IMG_6652.jpeg` store 640 × 480 pixels with EXIF orientation 6; display them as 480 × 640 portrait images.
- `IMG_6988.jpeg` is a two-frame MPO despite its extension: a 480 × 640 RGB photograph and a 240 × 320 grayscale auxiliary image. The auxiliary image is not a separate artwork reference.
- Most files embed the Apple Wide Color Sharing Profile; `IMG_6988.jpeg` embeds Apple Poppy Output Profile. Account for embedded profiles during later color-managed preparation.
- `IMG_1795.jpeg` and `IMG_1869.jpeg` show overlapping views of the same red/black wall artwork.
- The archive contains no placement notes, README, or license file. Inspected descriptive EXIF/IPTC metadata contains no rights statement. This record makes no claim about artwork ownership or reuse rights.

## Per-file SHA-256

| File | SHA-256 |
|---|---|
| `IMG_1758.jpeg` | `515c71512f78f702caecd675a89a8b63c394eeefaf1eb7f26bfb69d75a8ec36a` |
| `IMG_1770.jpeg` | `1f069931a06312b012429edbc864f77550f1e23bff613862f390dbc43185bbe2` |
| `IMG_1795.jpeg` | `6030794747d51337dae03a8a58633851958992b23dfbdee0bfeb08cb2eaf656b` |
| `IMG_1820.jpeg` | `264c7f48b8838c368ce48068e88a7d7e7786ea2f2284823a508cf8a1e610c04f` |
| `IMG_1869.jpeg` | `72dbc24b8ac895cb7b286aa461cfbce48abf2cc684be6fc5aaefab83f46accd6` |
| `IMG_2813.jpeg` | `0c40b34aadcad819c06df99bd2d1a53f6e4a3f72011ea212b73859af881f3173` |
| `IMG_3037.jpeg` | `775abaaf03302d047ec7289a80ba1a7578715905e0c2a98bb88a3eb1258ce34e` |
| `IMG_3248.jpeg` | `67b4330caab9b44f600915bb2d9c634303ed5d1e7891d936928b6f040c1317ab` |
| `IMG_3260.jpeg` | `e66514bb56cb61500047a124e5f4522ad88809b4cdeec1967667a4a2b5e26af8` |
| `IMG_4122.jpeg` | `93b02a7ce599a0e4ffad64b84476c0042897c883dcdd54c8e03314f15ee4d431` |
| `IMG_6652.jpeg` | `50bcc6ae03c0d852c941ea7bafb88ab4702b53efcc765cc99842c3cf888c7974` |
| `IMG_6988.jpeg` | `2bfa8af481ec36e91b855dba5dba3f1fb294bba2cffb4383989c9734cd30dd5c` |
