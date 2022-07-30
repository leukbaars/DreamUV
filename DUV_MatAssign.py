import bpy
import bmesh

class DREAMUV_OT_mat_assign(bpy.types.Operator):
    """Assigns the material from the active face to the selected faces."""
    bl_idname = "view3d.dreamuv_matassign"
    bl_label = "3D View Assign Material"
    bl_options = {"UNDO"}

    def execute(self, context):
        # to-do:
        # make a list of the objects that have selected faces.
        ob = bpy.context.object
        mesh = ob.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active

        facecounter = 0

        selected_faces=[]
        active_face = bm.faces.active

        # Ensure at least 1 face is selected.
        for f in bm.faces:
            if f.select:
                facecounter += 1
        if facecounter < 2:
            self.report({'INFO'}, "only one face selected, aborting")
            return {'FINISHED'}

        # Save the active face.
        # for f in bm.faces.active:
        #     active_face.append(f)

        # Save the remaining selected faces.
        for f in bm.faces:
            if f.select:
                if f is not bm.faces.active:
                    selected_faces.append(f)
                # Not sure what the point of this is.
                else:
                    f.select=False

        # Try to get the material being applied to the face.
        slot_len = len(ob.material_slots)
        if active_face.material_index < 0 or active_face.material_index >= slot_len:
            self.report({'INFO'}, "object has no materials, aborting")
            return {'FINISHED'}
            
        material = ob.material_slots[active_face.material_index].material
        if material is None:
            self.report({'INFO'}, "face has no material, aborting")
            return {'FINISHED'}

        # Sets the selected faces' materials to that of the active face.
        for f in selected_faces:
            f.material_index = active_face.material_index

        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}