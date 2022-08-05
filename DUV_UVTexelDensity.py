from cmath import sqrt
import bpy
import bmesh
from mathutils import Vector

def tri_area(co1, co2, co3):
    return (co2-co1).cross(co3-co1).length/2.0

class DREAMUV_OT_texel_density(bpy.types.Operator):
    """Set the texel density of the selected face(s)"""
    bl_idname = "view3d.dreamuv_texeldensity"
    bl_label = "3D View Texel Density"
    bl_options = {"UNDO"}

    def execute(self, context):

        ob = bpy.context.object
        mesh = ob.data
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(mesh)
        # Make a copy of the original mesh so that we can restore it to a pre-triangulation state.
        original_mesh = bm.copy()
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active

        # Texel density: The amount of pixels that maps to one unit. Will be set in-editor.
        self.set_texel_density = 512.0
        module_name = __name__.split('.')[0]
        addon_prefs = bpy.context.preferences.addons[module_name].preferences
        self.set_texel_density = addon_prefs.set_texel_density
        target_texel_density = self.set_texel_density
        # The resolution of the target texture. Need to accomodate for non-square textures at some point.
        # Pull the image resolution automatically. Add an option to set it manually.
        image_resolution = 64.0
        # The amount of units that the texture covers. A 64x64 px texture at TD = 32 px covers 4 units.
        texel_uv_multiplier = (image_resolution / target_texel_density) ** 2

        scale_faces = {}
        scale_mult_list = []

        for f in bm.faces:
            face_area = 0.0
            uv_area = 0.0
            scale_multiplier = 0.0
            tri_count = 0
            curr_face = []

            if f.select:
                scale_faces[f] = scale_multiplier
                curr_face.append(f)

                for tri in bmesh.ops.triangulate(bm, faces = curr_face)["faces"]:
                    # Can also use tri.calc_area(), at least for the face area.
                    face_area += tri_area(*(v.co for v in tri.verts))
                    # Doesn't handle non-flat faces very well.
                    uv_area += tri_area( *(Vector( (*l[uv_layer].uv, 0) ) for l in tri.loops) )
                    tri_count += 1
                    print("face_area: ", face_area, "; uv_area: ", uv_area)
    
                scale_multiplier = sqrt(((uv_area * texel_uv_multiplier) / face_area)).real
                scale_faces[f] = scale_multiplier
                scale_mult_list.append(scale_multiplier)

                face_area, uv_area = 0.0, 0.0
                tri_count = 0
                curr_face = []

        bm.free()
        # Restore the original mesh.
        bpy.ops.object.mode_set(mode="OBJECT")
        original_mesh.to_mesh(mesh)
        bpy.ops.object.mode_set(mode="EDIT")
        original_mesh.free()
        
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active

        faces = list()
        #MAKE FACE LIST
        for face in bm.faces:
            if face.select:
                faces.append(face)  

        #get original size
        xmin, xmax = faces[0].loops[0][uv_layer].uv.x, faces[0].loops[0][uv_layer].uv.x
        ymin, ymax = faces[0].loops[0][uv_layer].uv.y, faces[0].loops[0][uv_layer].uv.y
        
        for face in faces: 
            for vert in face.loops:
                xmin = min(xmin, vert[uv_layer].uv.x)
                xmax = max(xmax, vert[uv_layer].uv.x)
                ymin = min(ymin, vert[uv_layer].uv.y)
                ymax = max(ymax, vert[uv_layer].uv.y)
        
        xcenter=(xmin+xmax)/2
        ycenter=(ymin+ymax)/2

        for i, face in enumerate(faces):
            for loop in face.loops:
                loop[uv_layer].uv.x -= xcenter
                loop[uv_layer].uv.y -= ycenter

                loop[uv_layer].uv.x /= scale_mult_list[i]
                loop[uv_layer].uv.y /= scale_mult_list[i]

                loop[uv_layer].uv.x += xcenter
                loop[uv_layer].uv.y += ycenter

        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
        
        return {'FINISHED'}