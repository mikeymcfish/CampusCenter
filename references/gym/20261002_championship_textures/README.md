# Gym championship banner textures

66 independently reviewed, AI-generated native PNG textures for the four gym walls: A 16, B 19, C 19, D 12. Only team championship titles and years are included.

These are generated visual reconstructions, not photographic cutouts or measured reproductions. The PNG bytes and their C2PA generation provenance are preserved unchanged. No originals or personal rosters are included.

## Contents

- `wall_a/`, `wall_b/`, `wall_c/`, `wall_d/`: the 66 native RGB PNG textures
- `Public_Texture_Manifest.json`: exact intended lines, wall/row/column positions, dimensions, byte sizes, SHA-256 and Git blob hashes, provenance, and source/assumption distinctions
- `QA_Report.json`: independent text, completeness and privacy checks and integration limitations
- `SHA256SUMS.txt`: checksums for all 66 PNGs and the three public documents

## Four explicitly unverified class letters

Class C is a user-approved reconstruction assumption for these four Wall D banners. It is **not** a newly verified reading of the photographs:

- D_BLEACHER_SIDELINE-R1-C02
- D_BLEACHER_SIDELINE-R1-C06
- D_BLEACHER_SIDELINE-R2-C01
- D_BLEACHER_SIDELINE-R2-C03

## Integration

Use the manifest for ordering and placement. Preserve native aspect ratio, which varies by asset. A/C and eight D images are 1536 x 1024; B images are approximately 1.599:1; four D images are approximately 1.595:1. These are RGB rectangles with baked cloth shading and stitched hems, not alpha-cutout meshes or complete PBR materials. Check UV mapping, placement, lighting, viewing-distance legibility and runtime performance in the final scene.

The 66 PNGs total 208,046,441 bytes. From this directory, verify the complete transfer with `sha256sum -c SHA256SUMS.txt` (or an equivalent SHA-256 checker).

## Source references

The photo-grounded source manifest and approved name-free reference excerpts are at [the source-reference commit](https://github.com/mikeymcfish/CampusCenter/tree/fd9d2963d132cc7932b2e155374727cfc6a16d5b/references/gym/20261002_name_free). No gym-model or release changes are part of this reference transfer.
