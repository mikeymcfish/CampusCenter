# Edit the walkable area

Open **Edit_Commons_Dusk.cmd**, then load **CampusCenter_Dusk**. Stop Play before editing. Save a copy of the level before substantial layout changes.

## Change where the crowd can walk

1. Press **P** in the level viewport to display the navigation mesh in green.
2. Find **Commons_Walkable_Bounds** in the Outliner. This Nav Mesh Bounds Volume defines where Unreal is allowed to calculate crowd routes.
3. Use **W** to move it and **R** to resize it. It must cover the floor and have enough vertical extent to include that floor.
4. Navigation is configured to rebuild dynamically. If the green surface does not update, use **Build → Build Paths**, then inspect again.
5. To exclude a small patch from crowd routes, add a **Nav Modifier Volume**, place it over that patch, and set **Area Class** to **NavArea_Null**. This excludes AI navigation; it does not physically block the player.

Keep the volume below upper floors when it is intended only for ground-floor circulation. A larger navigation volume does not create missing floors or open a blocked door.

## Change where you can walk

Player movement uses physical collision, independently of the green navigation overlay.

- Move furniture out of a passage to open it. Select every actor in a multipart furniture folder together.
- Add a **Blocking Volume** to create an invisible physical barrier.
- Select a mesh component and inspect **Collision Presets**. `BlockAll` blocks the player; `NoCollision` lets the player pass through. Avoid disabling collision on floors, walls, stairs, or safety railings.
- For a newly imported mesh, open the Static Mesh Editor and inspect its simple collision. Detailed furniture can use appropriate simple boxes/convex shapes; a solid box across a doorway will block the passage even if the visible doorway is open.

Press Play and test the actual route, doorway, and stair transitions after edits. A green path alone does not verify player clearance.

## Adjust movement and crowd size

- Select **Campus_Walk_Settings** under **Walkthrough / Settings**. **Walk Speed** and **Run Speed** are editable in centimetres per second. Current values: 720 and 1,100. Hold either Shift key to run; release it to walk.
- Select **Commons_MetaHuman_Crowd** under **Commons / Crowd**, then change **Count**. Current count: 6. Keep **Auto Spawn on Begin Play** enabled.
- The crowd uses four sample appearances. Its configuration is `/Game/Campus/Crowd/DA_CommonsCrowd`; its spawn-area query is `/Game/Campus/Crowd/EQS_CommonsSpawn`.

Restart the walkthrough after saving changes, especially when a project plugin has changed. The launchers use the editable project; the old packaged executable does not contain these revisions.
