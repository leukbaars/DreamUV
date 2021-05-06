import bpy
import bmesh
import math
from mathutils import Vector
from . import DUV_Utils


class DREAMUV_OT_uv_unwrap_square(bpy.types.Operator):
    """Unwrap and attempt to fit to a square shape"""
    bl_idname = "view3d.dreamuv_uvunwrapsquare"
    bl_label = "unwrap to square shape if possible"
    
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        HSfaces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                HSfaces.append(face)    

        
        is_rect = DUV_Utils.square_fit(context)

        #FIT TO 0-1 range
        xmin, xmax = HSfaces[0].loops[0][uv_layer].uv.x, HSfaces[0].loops[0][uv_layer].uv.x
        ymin, ymax = HSfaces[0].loops[0][uv_layer].uv.y, HSfaces[0].loops[0][uv_layer].uv.y
        
        for face in HSfaces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)

        #prevent divide by 0:
        if (xmax - xmin) == 0:
            xmin = .1
        if (ymax - ymin) == 0:
            ymin = .1

        for face in HSfaces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xmin
                loop[uv_layer].uv.y -= ymin
                loop[uv_layer].uv.x /= (xmax-xmin)
                loop[uv_layer].uv.y /= (ymax-ymin)

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        return {'FINISHED'}