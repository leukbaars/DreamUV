#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! 

bl_info = {
    "name": "DreamUV",
    "category": "UV",
    "author": "Bram Eulaers",
    "description": "Edit selected faces'UVs directly inside the 3D Viewport. WIP. Check for updates @leukbaars",
    "blender": (2, 90, 0),
    "version": (0, 9)
}

import bpy
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty, PointerProperty
from . import DUV_UVTranslate 
from . import DUV_UVRotate 
from . import DUV_UVScale 
from . import DUV_UVExtend 
from . import DUV_UVStitch 
from . import DUV_UVTransfer 
from . import DUV_UVCycle 
from . import DUV_UVMirror 
from . import DUV_UVMoveToEdge
from . import DUV_Utils
from . import DUV_HotSpot
from . import DUV_UVProject
from . import DUV_UVUnwrap
from . import DUV_UVInset
from . import DUV_UVTrim
from . import DUV_ApplyMaterial

import importlib
if 'bpy' in locals():
    importlib.reload(DUV_UVTranslate)
    importlib.reload(DUV_UVRotate)
    importlib.reload(DUV_UVScale)
    importlib.reload(DUV_UVExtend) 
    importlib.reload(DUV_UVStitch)
    importlib.reload(DUV_UVTransfer) 
    importlib.reload(DUV_UVCycle) 
    importlib.reload(DUV_UVMirror) 
    importlib.reload(DUV_UVMoveToEdge)
    importlib.reload(DUV_Utils)
    importlib.reload(DUV_HotSpot)
    importlib.reload(DUV_UVProject)
    importlib.reload(DUV_UVUnwrap)
    importlib.reload(DUV_UVInset)
    importlib.reload(DUV_UVTrim)
    importlib.reload(DUV_ApplyMaterial)

class DUVUVToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    pixel_snap : BoolProperty(
        name="UV Pixel Snap",
        description="Translate Pixel Snapping",
        default=False
    )

    move_snap : FloatProperty(
        name="UV Move Snap",
        description="Translate Scale Subdivision Snap Size",
        default=0.25
    )
    scale_snap : FloatProperty(
        name="UV Scale Snap",
        description="Scale Snap Size",
        default=2
    )
    rotate_snap : FloatProperty(
        name="UV Rotate Snap",
        description="Rotate Angle Snap Size",
        default=45
    )


# This should get its own py file
class DREAMUV_PT_uv(bpy.types.Panel):
    """DreamUV Tools Panel Test!"""
    bl_label = "DreamUV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DreamUV'

    #@classmethod
    #def poll(cls, context):
    #    prefs = bpy.context.preferences.addons[__name__].preferences
    #    return prefs.show_panel_tools

    def draw(self, context):
        addon_prefs = prefs()
        layout = self.layout
        box = layout.box()
        if bpy.context.object.mode != 'EDIT':
            box.enabled = False

        col = box.column(align=True)
        col.label(text="Viewport UV Tools:")
        row = col.row(align = True)
        row.operator("view3d.dreamuv_uvtranslate", text="Move", icon="UV_SYNC_SELECT")
        row = row.row(align = True)
        row.prop(addon_prefs, 'move_snap', text="")

        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvtranslatestep", text=" ", icon="TRIA_UP")
        op.direction = "up"
        op = row.operator("view3d.dreamuv_uvtranslatestep", text=" ", icon="TRIA_DOWN")
        op.direction = "down"
        op = row.operator("view3d.dreamuv_uvtranslatestep", text=" ", icon="TRIA_LEFT")
        op.direction = "left"
        op = row.operator("view3d.dreamuv_uvtranslatestep", text=" ", icon="TRIA_RIGHT")
        op.direction = "right"
        col.separator()

        row = col.row(align = True)
        row.operator("view3d.dreamuv_uvscale", text="Scale", icon="FULLSCREEN_ENTER")
        row = row.row(align = True)
        row.prop(addon_prefs, 'scale_snap', text="")
        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvscalestep", text=" ", icon="ADD")
        op.direction="+XY"
        op = row.operator("view3d.dreamuv_uvscalestep", text=" ", icon="REMOVE")
        op.direction="-XY"
        op = row.operator("view3d.dreamuv_uvscalestep", text="+X")
        op.direction = "+X"
        op = row.operator("view3d.dreamuv_uvscalestep", text="-X")
        op.direction = "-X"
        op = row.operator("view3d.dreamuv_uvscalestep", text="+Y")
        op.direction = "+Y"
        op = row.operator("view3d.dreamuv_uvscalestep", text="-Y")
        op.direction = "-Y"
        col.separator()

        row = col.row(align = True)
        row.operator("view3d.dreamuv_uvrotate", text="Rotate", icon="FILE_REFRESH")
        row = row.row(align = True)
        row.prop(addon_prefs, 'rotate_snap', text="")
        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvrotatestep", text=" ", icon="LOOP_FORWARDS")
        op.direction="forward"
        op = row.operator("view3d.dreamuv_uvrotatestep", text=" ", icon="LOOP_BACK")
        op.direction="reverse"
        col.separator()
        col.operator("view3d.dreamuv_uvextend", text="Extend", icon="MOD_TRIANGULATE")
        col.operator("view3d.dreamuv_uvstitch", text="Stitch", icon="UV_EDGESEL")
        col.operator("view3d.dreamuv_uvcycle", text="Cycle", icon="FILE_REFRESH")
        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvmirror", text="Mirror X", icon="MOD_MIRROR")
        op.direction = "x"
        op = row.operator("view3d.dreamuv_uvmirror", text="Mirror Y")
        op.direction = "y"

        col.separator()
        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvinsetstep", text="Inset", icon="FULLSCREEN_EXIT")
        op.direction = "in"
        op = row.operator("view3d.dreamuv_uvinsetstep", text="Expand", icon="FULLSCREEN_ENTER")
        op.direction = "out"
        row.prop(context.scene, "uvinsetpixels", text="")
        row.prop(context.scene, "uvinsettexsize", text="")

        col.label(text="Move to UV Edge:")
        row = col.row(align = True)
        op = row.operator("view3d.dreamuv_uvmovetoedge", text=" ", icon="TRIA_UP_BAR")
        op.direction="up"
        op = row.operator("view3d.dreamuv_uvmovetoedge", text=" ", icon="TRIA_DOWN_BAR")
        op.direction="down"
        op = row.operator("view3d.dreamuv_uvmovetoedge", text=" ", icon="TRIA_LEFT_BAR")
        op.direction = "left"
        op = row.operator("view3d.dreamuv_uvmovetoedge", text=" ", icon="TRIA_RIGHT_BAR")
        op.direction = "right"

        box = layout.box()
        if bpy.context.object.mode != 'EDIT':
            box.enabled = False
        col = box.column(align=True)
        col.label(text="Unwrapping Tools:")
        col.operator("view3d.dreamuv_uvunwrapsquare", text="Square Fit Unwrap", icon="OUTLINER_OB_LATTICE")
        unwraptool=col.operator("uv.unwrap", text="Blender Unwrap", icon='UV')
        unwraptool.method='CONFORMAL'
        unwraptool.margin=0.001
        

        col.separator()
        box = layout.box()
        if bpy.context.object.mode != 'EDIT':
            box.enabled = False
        col = box.column(align=True)
        col.label(text="UV Transfer Tool:")
        row = col.row(align = True)
        row.prop(context.scene, "uvtransferxmin", text="")
        row.prop(context.scene, "uvtransferymin", text="")
        row.prop(context.scene, "uvtransferxmax", text="")
        row.prop(context.scene, "uvtransferymax", text="")

        col.operator("view3d.dreamuv_uvtransfergrab", text="Grab UV from selection", icon="FILE_TICK")
        row = col.row(align = True)
        row.operator("view3d.dreamuv_uvtransfer", text="Transfer to selection", icon="MOD_UVPROJECT")

        col.separator()
        box = layout.box()
        col = box.column(align=True)
        col.label(text="HotSpot Tool:")
        row = col.row(align = True)
        row.label(text="Atlas Object:")
        row.prop_search(context.scene, "subrect_atlas", context.scene, "objects", text="", icon="MOD_MULTIRES")
        row = col.row(align = True)
        row.label(text="Atlas Scale:")
        row.prop(context.scene, "duvhotspotscale", text="")
        row = col.row(align = True)
        row.label(text="Hotspot material:")
        row.prop_search(context.scene, "duv_hotspotmaterial", bpy.data, "materials", text="")
        row = col.row(align = True)
        row.prop(context.scene, "duv_hotspotuseinset", icon="FULLSCREEN_EXIT", text="use inset")
        row.separator()
        row.prop(context.scene, "hotspotinsetpixels", text="")
        row.prop(context.scene, "hotspotinsettexsize", text="")

        col.separator()
        row = col.row(align = True)
        row.operator("view3d.dreamuv_hotspotter", text="HotSpot", icon="SHADERFX")
        row.prop(context.scene, "duv_useorientation", icon="EVENT_W", text="")
        row.prop(context.scene, "duv_usemirrorx", icon="EVENT_X", text="")
        row.prop(context.scene, "duv_usemirrory", icon="EVENT_Y", text="")

        if context.scene.duv_experimentaltools is True:
            col.separator()
                    
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Trim Tool:")
            row = col.row(align = True)
            
            row.operator("view3d.dreamuv_uvtrim", text="TRIM", icon="MOD_UVPROJECT")
            row.prop_search(context.scene, "trim_atlas", context.scene, "objects", text="", icon="MOD_MULTIRES")
            row = col.row(align = True)
            row.prop(context.scene, "trim_index", text="")
            row = col.row(align = True) 
            op = row.operator("view3d.dreamuv_uvtrimnext", text="previous", icon="MOD_UVPROJECT")
            op.reverse = True
            op = row.operator("view3d.dreamuv_uvtrimnext", text="next", icon="MOD_UVPROJECT")
            op.reverse = False
            
            col.separator()
            
            row = col.row(align = True)
            row.operator("view3d.dreamuv_uvcap", text="CAP", icon="MOD_UVPROJECT")
            row = col.row(align = True)
            row.prop(context.scene, "cap_index", text="")
            row = col.row(align = True) 
            op = row.operator("view3d.dreamuv_uvcapnext", text="previous", icon="MOD_UVPROJECT")
            op.reverse = True
            op = row.operator("view3d.dreamuv_uvcapnext", text="next", icon="MOD_UVPROJECT")
            op.reverse = False
            
            col.separator()
            row = col.row(align = True)
            row.prop(context.scene, "duv_trimuseinset", icon="FULLSCREEN_EXIT", text="use inset")
            row.separator()
            row.prop(context.scene, "hotspotinsetpixels", text="")
            row.prop(context.scene, "hotspotinsettexsize", text="")

            col.separator()
            box = layout.box()
            col = box.column(align=True)

            row = col.row(align = True) 
            op = row.operator("view3d.dreamuv_apply_material", text="apply material", icon="MOD_UVPROJECT")
            row = col.row(align = True) 
            row.prop_search(context.scene, "duv_hotspotmaterial", bpy.data, "materials", )
        

        col = self.layout.column(align = True)
        col2= self.layout.column(align = True)
        col2.label(text="DreamUV Beta")
        row = col2.row(align = True) 
        row.label(text="send feedback to @leukbaars!")
        #row.prop(context.scene, "duv_experimentaltools", icon="HEART", text="")


def prefs():
    return bpy.context.preferences.addons[__name__].preferences

classes = (
    DUVUVToolsPreferences,
    DREAMUV_PT_uv,
    DUV_UVTranslate.DREAMUV_OT_uv_translate,
    DUV_UVTranslate.DREAMUV_OT_uv_translate_step,
    DUV_UVRotate.DREAMUV_OT_uv_rotate,
    DUV_UVRotate.DREAMUV_OT_uv_rotate_step,
    DUV_UVScale.DREAMUV_OT_uv_scale,
    DUV_UVScale.DREAMUV_OT_uv_scale_step,
    DUV_UVExtend.DREAMUV_OT_uv_extend,
    DUV_UVStitch.DREAMUV_OT_uv_stitch,
    DUV_UVTransfer.DREAMUV_OT_uv_transfer,
    DUV_UVTransfer.DREAMUV_OT_uv_transfer_grab,
    DUV_UVCycle.DREAMUV_OT_uv_cycle,
    DUV_UVMirror.DREAMUV_OT_uv_mirror,
    DUV_UVMoveToEdge.DREAMUV_OT_uv_move_to_edge,
    DUV_UVProject.DREAMUV_OT_uv_project,
    DUV_UVUnwrap.DREAMUV_OT_uv_unwrap_square,
    DUV_HotSpot.DREAMUV_OT_hotspotter,
    DUV_UVInset.DREAMUV_OT_uv_inset,
    DUV_UVInset.DREAMUV_OT_uv_inset_step,
    DUV_UVTrim.DREAMUV_OT_uv_trim,
    DUV_UVTrim.DREAMUV_OT_uv_cap,
    DUV_UVTrim.DREAMUV_OT_uv_trimnext,
    DUV_UVTrim.DREAMUV_OT_uv_capnext,
    DUV_ApplyMaterial.DREAMUV_OT_apply_material,
)

def poll_material(self, material):
    return not material.is_grease_pencil

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.subrect_atlas = bpy.props.PointerProperty (name="atlas",type=bpy.types.Object,description="atlas object")
    bpy.types.Scene.trim_atlas = bpy.props.PointerProperty (name="trim_atlas",type=bpy.types.Object,description="trim atlas")
    bpy.types.Scene.trim_index = bpy.props.IntProperty (name = "trim_index",default = 0,description = "trim index")
    bpy.types.Scene.cap_index = bpy.props.IntProperty (name = "cap_index",default = 0,description = "cap index")
    bpy.types.Scene.duv_trimuseinset = bpy.props.BoolProperty (name = "duv_trimuseinset",default = False,description = "Use inset when trimming")
    bpy.types.Scene.uvinsetpixels = bpy.props.FloatProperty (name = "uv inset pixel amount",default = 1.0,description = "")
    bpy.types.Scene.uvinsettexsize = bpy.props.FloatProperty (name = "uv inset texture size",default = 1024.0,description = "")
    bpy.types.Scene.uvtransferxmin = bpy.props.FloatProperty (name = "uvtransferxmin",default = 0.0,description = "uv left bottom corner X")
    bpy.types.Scene.uvtransferymin = bpy.props.FloatProperty (name = "uvtransferymin",default = 0.0,description = "uv left bottom corner Y")
    bpy.types.Scene.uvtransferxmax = bpy.props.FloatProperty (name = "uvtransferxmax",default = 1.0,description = "uv right top corner X")
    bpy.types.Scene.uvtransferymax = bpy.props.FloatProperty (name = "uvtransferymax",default = 1.0,description = "uv right top corner Y")
    bpy.types.Scene.duv_useorientation = bpy.props.BoolProperty (name = "duv_useorientation",default = False,description = "Align UVs with world orientation")
    bpy.types.Scene.duv_usemirrorx = bpy.props.BoolProperty (name = "duv_usemirrorx",default = True,description = "Randomly mirror faces on the x-axis")
    bpy.types.Scene.duv_usemirrory = bpy.props.BoolProperty (name = "duv_usemirrory",default = True,description = "Randomly mirror faces on the y-axis")
    bpy.types.Scene.duvhotspotscale = bpy.props.FloatProperty (name = "duvhotspotscale",default = 1.0,description = "hotspotting scale multiplier")
    bpy.types.Scene.duv_hotspotmaterial = bpy.props.PointerProperty (name="duv_hotspotmaterial",type=bpy.types.Material,poll=poll_material,description="hotspot material")
    bpy.types.Scene.duv_hotspotuseinset = bpy.props.BoolProperty (name = "duv_hotspotuseinset",default = False,description = "Use inset when hotspotting")
    bpy.types.Scene.hotspotinsetpixels = bpy.props.FloatProperty (name = "hotspot inset pixel amount",default = 1.0,description = "")
    bpy.types.Scene.hotspotinsettexsize = bpy.props.FloatProperty (name = "hotspot texture size",default = 1024.0,description = "")
    bpy.types.Scene.duv_experimentaltools = bpy.props.BoolProperty (name = "duv_experimentaltools",default = False,description = "Show experimental tools")
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
