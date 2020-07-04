import bpy

class UVStitch(bpy.types.Operator):
    """Stitch shared vertices on selected faces"""
    bl_idname = "uv.duv_uvstitch"
    bl_label = "3D View UV Stitch"
    bl_options = {"UNDO"}

    def execute(self, context):
        #yup, it's this simple
        bpy.ops.uv.select_all(action='SELECT')
        #2 stitch operations, possibly need more
        bpy.ops.uv.stitch(use_limit=False,snap_islands=False,midpoint_snap=True)
        bpy.ops.uv.stitch(use_limit=False,snap_islands=False,midpoint_snap=True)
        return {'FINISHED'}