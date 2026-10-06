# CampusCenter location telemetry v1 (frozen)

Transport: one OSC 1.0 message per UDP datagram, 20 Hz, destination **127.0.0.1:9001**. Receiver binds IPv4 loopback only, exclusively. No bundles, LAN, broadcast, multicast, discovery, firewall rule, or authentication claim. Opt-in sender must leave all input, rendering and launcher settings intact.

Address: `/campuscenter/player/v1`

Exact type tag string: `,issisfffffiii`

| Index | OSC type | Meaning |
|---|---|---|
| 1 | i | protocol version, exactly 1 |
| 2 | s | profile, exactly `campuscenter-r29-p02-sample-1-250-v1` |
| 3 | s | session ID, fresh `ue-` + UUID per sender start (simulator uses `sim-` + UUID) |
| 4 | i | sequence, nonnegative int32, strictly increasing per session; create new session before wrap |
| 5 | s | UTC Unix milliseconds, decimal ASCII string (avoids float precision and int64 OSC dependency) |
| 6 | f | Unreal world X, centimetres, **camera/HMD world location**, including room-scale offset |
| 7 | f | Unreal world Y, centimetres, same sample as X |
| 8 | f | P02 sample model X, millimetres: `(worldX + 4700) / 25` |
| 9 | f | P02 sample model Y, millimetres: `(-worldY + 230) / 25` |
| 10 | f | Unreal world camera yaw, degrees; yaw 0 = +world X; yaw +90 = +world Y |
| 11 | i | floor: 0 ground, 1 upstairs, -1 unknown; floor detection belongs to sender |
| 12 | i | validity: 1 reliable player pose and classified floor; 0 invalid/lost tracking/unknown floor/no usable player |
| 13 | i | teleport/discontinuity: 1 on first snapshot and after teleport/recenter/discontinuity, otherwise 0 |

Ground = sharp dot. Upstairs = soft blurred dot at the **same XY** on the ground sample. Invalid = immediately hidden. Outside sample foundation footprint = hidden, including bounding-box cutouts. No player-following map. Heading arrow is optional; model direction for yaw is `(cos(yaw), -sin(yaw))`.

P02 physical source: `print_revision02/deliverables/Ground_R29_P02_Sample_1_250.obj`, right-handed model mm, Z up, +Y north. Actual sample bounds `[4.48,2.72] .. [267.84,199.52]` mm; scale denominator 250. Source XY datum is world `[-4700,+230]` cm -> model `[0,0]` mm. Do not use inherited 1:100 projection canvas, UV atlas coordinates, or UV02 larger assembly. Companion derives footprint from z=0 foundation faces of this exact sample. Physical projection calibration is separate from world-to-model registration.

Receiver hides after 500 ms without an accepted snapshot using a receiver monotonic clock. Malformed/nonfinite/wrong-contract/mismatched world-to-model (>0.05 mm)/duplicate/out-of-order packets do not refresh that timer. Shared-PC UTC stamp guards queued packets: reject >500 ms old or >1000 ms in future; also require timestamp nondecreasing within a session. A local wall-clock jump >1500 ms relative to elapsed monotonic time permits timestamp regression on the next accepted increasing sequence; the 500 ms receive timeout never uses wall time. On new session accept a fresh snapshot, retire previous session so its delayed packets cannot reclaim the stream. While current telemetry is fresh, a new session must start at sequence 0 with teleport=1; after stale timeout a fresh new session may join at any sequence. Receiver caps retired session history at 1024 then requires restart. Invalid packets participate in sequence/session state. No smoothing: every accepted snapshot uses its exact XY, so teleports always snap. Status distinguishes `sim-` and `ue-`; `ue-` labels telemetry origin and does not certify a packaged-game integration test.

Sender must use valid=0 if headset pose loses tracking, application focus safety invalidates pose, camera/player absent, or floor classification is unknown. Desktop can report active camera world pose; its heading/location are not headset evidence. Detect floor by known walkable surfaces/volumes with hysteresis using floor/body reference, not HMD eye height alone; gym tall ground-floor void must stay ground. Sender integration and floor classification QA are owned by Unreal task 01a0f36f-2c2f-74cd-a7a4-9f81894fe015.

No physical projection, HMD behavior, or performance claim follows from simulator or software receiver tests.

References: [OSC 1.0](https://opensoundcontrol.stanford.edu/spec-1_0.html).
