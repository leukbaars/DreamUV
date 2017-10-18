import bpy
import math
import bmesh
from mathutils import Vector

class UVTransfer(bpy.types.Operator):
    """Copy UVs from active face to selected faces"""
    bl_idname = "uv.brm_uvtransfer"
    bl_label = "3D View UVTransfer"
    bl_options = {"UNDO"}

    def execute(self, context):
        mesh = bpy.context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active
        face0=[]

        #save active face
        for l in bm.faces.active.loops:
            face0.append(l[uv_layer].uv)

        #copy uvs to selected face
        for f in bm.faces:
            if f.select:
                if f is not bm.faces.active:
                    for i,l in enumerate(f.loops):
                        if i < len(face0):
                            l[uv_layer].uv=face0[i]
                        else:
                            #TODO: possibly interpolate uvs for better transfer
                            l[uv_layer].uv=face0[len(face0)-1]

        bmesh.update_edit_mesh(mesh, False, False)
        return {'FINISHED'}