# Campus crowd positioning

Project-local Unreal 5.8 runtime plugin used by `/Game/Campus/Crowd/DA_CommonsCrowd`.

`UCampusCrowdActorManagement` retains MassCrowd's capsule sweep and MetaHuman multi-component visibility handling. It queues an async Mover teleport **after** Mass's deferred actor transform has executed. Reading the actor transform immediately after the base call would read the previous pooled position. Initial spawn uses the entity feet transform plus the actual capsule half-height, including Blueprint-created capsules that may be absent on the template CDO.

Editor binaries are included for the installed UE 5.8 build and work for the editor-based `-game` launcher. A packaged build must compile the Runtime module for its target. The legacy packaged campus executable has not been rebuilt.

Build requirements: MSVC 14.50, Windows SDK, Unreal 5.8. Source is included; engine plugin files are not modified by this repair.

Visual and runtime evidence is in `realism_assets/common_area/placement_v04/` at the workspace root.
