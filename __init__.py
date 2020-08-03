#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! 

#contributers:
#Bram Eulaers
#Jeiel Aranal (added pixel snapping!)

bl_info = {
    "name": "DreamUV",
    "category": "UV",
    "author": "Bram Eulaers",
    "description": "Edit selected faces'UVs directly inside the 3D Viewport. WIP. Check for updates @leukbaars",
    "blender": (2, 80, 0),
    "version": (0, 8)
}

if 'bpy' not in locals():
    import bpy
    from bpy.props import EnumProperty, BoolProperty, FloatProperty, PointerProperty
    from . import DUV_UVTranslate, DUV_UVRotate, DUV_UVScale, DUV_UVExtend, DUV_UVStitch, DUV_UVTransfer, DUV_UVCycle, DUV_UVMirror, DUV_UVMoveToEdge,DUV_Utils,DUV_HotSpot,DUV_UVProject,DUV_UVUnwrap
else:
    from importlib import reload
    reload(DUV_UVTranslate)
    reload(DUV_UVRotate)
    reload(DUV_UVScale)
    reload(DUV_UVExtend)
    reload(DUV_UVStitch)
    reload(DUV_UVTransfer)
    reload(DUV_UVCycle)
    reload(DUV_UVMirror)
    reload(DUV_UVMoveToEdge)
    reload(DUV_HotSpot)
    reload(DUV_UVProject)
    reload(DUV_UVUnwrap)
    reload(DUV_Utils)


uvmenutype = [("SUBMENU", "Submenu", ""),
              ("INDIVIDUAL", "Individual Entries", "")]


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

    show_panel_tools : BoolProperty(
        name="Show Tools in UV Panel",
        default=True
    )

    #adduvmenu = BoolProperty(name="Add DUV UVTools to UV Menu", default=True)
    #individualorsubmenu = EnumProperty(name="Individual or Sub-Menu", items=uvmenutype, default="SUBMENU")

    def draw(self, context):
        layout = self.layout

        #column = layout.column(align=True)

        #row = column.row()
        #row.prop(self, "adduvmenu")
        #if self.adduvmenu:
        #    row.prop(self, "individualorsubmenu", expand=True)

        #column.prop(self, "show_panel_tools")
        #column.prop(self, "pixel_snap")


class DUV_UVPanel(bpy.types.Panel):
    """DreamUV Tools Panel Test!"""
    bl_label = "DreamUV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DreamUV'
    bl_context = "mesh_edit"

    @classmethod
    def poll(cls, context):
        prefs = bpy.context.preferences.addons[__name__].preferences
        return prefs.show_panel_tools

    def draw_header(self, _):
        layout = self.layout
        #layout.label(text="", icon='FACESEL_HLT')

    def draw(self, context):
        addon_prefs = prefs()
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Viewport UV Tools:")
        row = col.row(align = True)
        row.operator("uv.duv_uvtranslate", text="Move", icon="UV_SYNC_SELECT")
        row = row.row(align = True)
        row.prop(addon_prefs, 'move_snap', text="")

        row = col.row(align = True)
        op = row.operator("uv.duv_uvtranslatestep", text=" ", icon="TRIA_UP")
        op.direction="up"
        op = row.operator("uv.duv_uvtranslatestep", text=" ", icon="TRIA_DOWN")
        op.direction="down"
        op = row.operator("uv.duv_uvtranslatestep", text=" ", icon="TRIA_LEFT")
        op.direction = "left"
        op = row.operator("uv.duv_uvtranslatestep", text=" ", icon="TRIA_RIGHT")
        op.direction = "right"
        col.separator()

        row = col.row(align = True)
        row.operator("uv.duv_uvscale", text="Scale", icon="FULLSCREEN_ENTER")
        row = row.row(align = True)
        row.prop(addon_prefs, 'scale_snap', text="")
        row = col.row(align = True)
        op = row.operator("uv.duv_uvscalestep", text=" ", icon="ADD")
        op.direction="+XY"
        op = row.operator("uv.duv_uvscalestep", text=" ", icon="REMOVE")
        op.direction="-XY"
        op = row.operator("uv.duv_uvscalestep", text="+X")
        op.direction = "+X"
        op = row.operator("uv.duv_uvscalestep", text="-X")
        op.direction = "-X"
        op = row.operator("uv.duv_uvscalestep", text="+Y")
        op.direction = "+Y"
        op = row.operator("uv.duv_uvscalestep", text="-Y")
        op.direction = "-Y"
        col.separator()

        row = col.row(align = True)
        row.operator("uv.duv_uvrotate", text="Rotate", icon="FILE_REFRESH")
        row = row.row(align = True)
        row.prop(addon_prefs, 'rotate_snap', text="")
        row = col.row(align = True)
        op = row.operator("uv.duv_uvrotatestep", text=" ", icon="LOOP_FORWARDS")
        op.direction="forward"
        op = row.operator("uv.duv_uvrotatestep", text=" ", icon="LOOP_BACK")
        op.direction="reverse"
        col.separator()
        col.operator("uv.duv_uvextend", text="Extend", icon="MOD_TRIANGULATE")
        col.operator("uv.duv_uvstitch", text="Stitch", icon="UV_EDGESEL")
        col.operator("uv.duv_uvcycle", text="Cycle", icon="FILE_REFRESH")
        row = col.row(align = True)
        op = row.operator("uv.duv_uvmirror", text="Mirror X", icon="MOD_MIRROR")
        op.direction = "x"
        op = row.operator("uv.duv_uvmirror", text="Mirror Y")
        op.direction = "y"

        # pixel snap not functional in 2.8
        #layout.prop(addon_prefs, "pixel_snap", text = 'Move Pixel Snap')
        #col.prop(addon_prefs, "pixel_snap", text = 'Move Pixel Snap', icon = 'FORCE_TEXTURE') 

        #box = layout.box()
        #col = box.column(align=True)
        col.label(text="Move to UV Edge:")
        row = col.row(align = True)
        op = row.operator("uv.duv_uvmovetoedge", text=" ", icon="TRIA_UP_BAR")
        op.direction="up"
        op = row.operator("uv.duv_uvmovetoedge", text=" ", icon="TRIA_DOWN_BAR")
        op.direction="down"
        op = row.operator("uv.duv_uvmovetoedge", text=" ", icon="TRIA_LEFT_BAR")
        op.direction = "left"
        op = row.operator("uv.duv_uvmovetoedge", text=" ", icon="TRIA_RIGHT_BAR")
        op.direction = "right"

        box = layout.box()
        col = box.column(align=True)


        col.label(text="Unwrapping Tools:")
        col.operator("uv.duv_uvunwrapsquare", text="Square Fit Unwrap", icon="OUTLINER_OB_LATTICE")
        unwraptool=col.operator("uv.unwrap", text="Blender Unwrap", icon='UV')
        unwraptool.method='CONFORMAL'
        unwraptool.margin=0.001
        

        col.separator()
        box = layout.box()
        col = box.column(align=True)
        col.label(text="UV Transfer Tool:")
        row = col.row(align = True)
        #row.label(text="minUV/maxUV:")
        row.prop(context.scene, "uvtransferxmin", text="")
        row.prop(context.scene, "uvtransferymin", text="")
        row.prop(context.scene, "uvtransferxmax", text="")
        row.prop(context.scene, "uvtransferymax", text="")

        col.operator("uv.duv_uvtransfergrab", text="Grab UV from selection", icon="FILE_TICK")
        row = col.row(align = True)
        row.operator("uv.duv_uvtransfer", text="Transfer to selection", icon="MOD_UVPROJECT")
        #col.label(text="top right coord:")
        #row = col.row(align = True)
        
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        #col = self.layout.column(align = True)
        
        col.label(text="HotSpot Tool:")
    
        #col = self.layout.column(align = True)
        row = col.row(align = True)
        row.label(text="Atlas Object:")
        row.prop_search(context.scene, "subrect_atlas", context.scene, "objects", text="", icon="MOD_MULTIRES")

        col.separator()
        row = col.row(align = True)
        row.operator("uv.duv_hotspotter", text="HotSpot", icon="SHADERFX")
        row.prop(context.scene, "duv_useorientation", icon="EVENT_W", text="")
        row.prop(context.scene, "duv_usemirrorx", icon="EVENT_X", text="")
        row.prop(context.scene, "duv_usemirrory", icon="EVENT_Y", text="")

        

        col = self.layout.column(align = True)
        #col.enabled = True
        col2= self.layout.column(align = True)
        col2.label(text="DreamUV Beta")
        col2.enabled = False
        col2.label(text="send feedback to @leukbaars!")
        #col.operator("DUV.uvproject", text = "PROJECT!")


def prefs():
    return bpy.context.preferences.addons[__name__].preferences

classes = (
    DUVUVToolsPreferences,
    DUV_UVPanel,
    DUV_UVTranslate.UVTranslate,
    DUV_UVTranslate.UVTranslateStep,
    DUV_UVRotate.UVRotate,
    DUV_UVRotate.UVRotateStep,
    DUV_UVScale.UVScale,
    DUV_UVScale.UVScaleStep,
    DUV_UVExtend.UVExtend,
    DUV_UVStitch.UVStitch,
    DUV_UVTransfer.UVTransfer,
    DUV_UVTransfer.UVTransferGrab,
    DUV_UVCycle.UVCycle,
    DUV_UVMirror.UVMirror,
    DUV_UVMoveToEdge.UVMoveToEdge,
    DUV_UVProject.UVProject,
    DUV_UVUnwrap.UVUnwrapSquare,
    DUV_HotSpot.HotSpotter,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    #if prefs().adduvmenu:
    #    bpy.types.VIEW3D_MT_uv_map.prepend(uv_menu_func)
    
    bpy.types.Scene.subrect_atlas = bpy.props.PointerProperty (
        name="atlas",
        type=bpy.types.Object,
        description="atlas object",
        )
    bpy.types.Scene.uvtransferxmin = bpy.props.FloatProperty (
        name = "uvtransferxmin",
        default = 0.0,
        description = "uv left bottom corner X",
        )
    bpy.types.Scene.uvtransferymin = bpy.props.FloatProperty (
        name = "uvtransferymin",
        default = 0.0,
        description = "uv left bottom corner Y",
        )
    bpy.types.Scene.uvtransferxmax = bpy.props.FloatProperty (
        name = "uvtransferxmax",
        default = 1.0,
        description = "uv right top corner X",
        )
    bpy.types.Scene.uvtransferymax = bpy.props.FloatProperty (
        name = "uvtransferymax",
        default = 1.0,
        description = "uv right top corner Y",
        )
    bpy.types.Scene.duv_useorientation = bpy.props.BoolProperty (
        name = "duv_useorientation",
        default = False,
        description = "Align UVs with world orientation",
        )
    bpy.types.Scene.duv_usemirrorx = bpy.props.BoolProperty (
        name = "duv_usemirrorx",
        default = True,
        description = "Randomly mirror faces on the x-axis",
        )
    bpy.types.Scene.duv_usemirrory = bpy.props.BoolProperty (
        name = "duv_usemirrory",
        default = True,
        description = "Randomly mirror faces on the y-axis",
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.subrect_atlas
    del bpy.types.Scene.uvtransferxmin
    del bpy.types.Scene.uvtransferymin
    del bpy.types.Scene.uvtransferxmax
    del bpy.types.Scene.uvtransferymax
    del bpy.types.Scene.duv_useorientation
    del bpy.types.Scene.duv_usemirrorx
    del bpy.types.Scene.duv_usemirrory

if __name__ == "__main__":
    register()
