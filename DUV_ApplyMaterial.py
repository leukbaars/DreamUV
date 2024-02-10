import bpy
import bmesh
import math
from mathutils import Vector
from . import DUV_Utils


class DREAMUV_OT_apply_material(bpy.types.Operator):
    """Unwrap and attempt to fit to a square shape"""
    bl_idname = "view3d.dreamuv_apply_material"
    bl_label = "unwrap to square shape if possible"
    
    def execute(self, context):

        #check for object or edit mode:
        objectmode = False
        if bpy.context.object.mode == 'OBJECT':
            objectmode = True
            #switch to edit and select all
            bpy.ops.object.editmode_toggle() 
            bpy.ops.mesh.select_all(action='SELECT')

        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        HSfaces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                HSfaces.append(face)    

        #ADD MATERIAL
        #check if we want to add material, then check if it needs to be added, and keep index for later
        if context.scene.duv_hotspotmaterial is not None:
            matindex = 0
            doesmatexist = False
            for m in obj.data.materials:
                if m == context.scene.duv_hotspotmaterial:
                    doesmatexist = True
                    break
                matindex += 1
            if doesmatexist is False:
                obj.data.materials.append(context.scene.duv_hotspotmaterial)


        #apply material from index
        if context.scene.duv_hotspotmaterial is not None:
            for face in HSfaces:   
                face.material_index = matindex

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        if objectmode is True:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle() 

        return {'FINISHED'}