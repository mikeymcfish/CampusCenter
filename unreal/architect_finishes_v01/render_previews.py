import bpy
from mathutils import Vector
from pathlib import Path

root = Path(__file__).parent
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_x = 1200
s.render.resolution_y = 675
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.film_transparent = False
s.render.image_settings.color_mode = 'RGB'
s.view_settings.view_transform = 'AgX'

def shot(name, pos, target):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    s.collection.objects.link(cam)
    cam.location = pos
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    data.lens = 23
    s.camera = cam
    s.render.filepath = str(root / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)

shot('Commons_finish_preview', (14.1,15.3,1.72), (2.5,24.0,3.0))
shot('CRI_finish_preview', (8.3,2.1,1.72), (6.5,12.7,1.85))
