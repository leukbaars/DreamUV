bl_info = {
    "name": "HotSpotter",
    "category": "3D View",
    "author": "brame@valvesoftware.com",
    "description": "Adds source 2 Utilities to the scene properties tab",
    "blender": (2, 80, 0)
    }

import bpy
import bmesh
import math
from mathutils import Vector
from . import DUV_Utils


class DREAMUV_OT_uv_project(bpy.types.Operator):
    bl_idname = "view3d.dreamuv_uvproject"
    bl_label = "project along world axis!"
    
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()
        faces = list()

        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                faces.append(face)

        for face in faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate (OBJECT SPACE)
                worldcoords = obj.matrix_world @ loop.vert.co
                loop_uv.uv = worldcoords.xy
        
        #FIT TO 0-1 range
        print("fitting it")
        xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
        ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y
        
        for face in faces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)

        for face in faces:
            for loop in face.loops:
                loop[uv_layer].uv.x -= xmin
                loop[uv_layer].uv.y -= ymin
                loop[uv_layer].uv.x /= (xmax-xmin)
                loop[uv_layer].uv.y /= (ymax-ymin)

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}