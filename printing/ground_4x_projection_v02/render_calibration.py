import bpy,pathlib,json
R=pathlib.Path(__file__).parent;s=bpy.context.scene
o=next(o for o in s.objects if o.type=='MESH');m=o.data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links
em=next(n for n in n if n.type=='EMISSION');mask_socket=em.inputs[0].links[0].from_node.inputs[2].links[0].from_socket
uv=next(x for x in n if x.type=='TEX_COORD');mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';l.new(uv.outputs['UV'],mul.inputs[0]);mul.inputs[1].default_value=(790.4255022321429/25,606.7133249555316/25,1)
check=n.new('ShaderNodeTexChecker');check.inputs['Scale'].default_value=1;check.inputs['Color1'].default_value=(.6,.6,.6,1);check.inputs['Color2'].default_value=(.02,.18,.2,1);l.new(mul.outputs[0],check.inputs['Vector'])
out=n.new('ShaderNodeMixRGB');out.blend_type='MULTIPLY';out.inputs[0].default_value=1;l.new(check.outputs[0],out.inputs[1]);l.new(mask_socket,out.inputs[2]);l.new(out.outputs[0],em.inputs[0]);s.render.filepath=str(R/'Calibration_25mm_Floor_Only.png');bpy.ops.render.render(write_still=True)
