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
from . import DUV_UVCopy
from . import DUV_UVMirror 
from . import DUV_UVMoveToEdge
from . import DUV_Utils
from . import DUV_HotSpot
from . import DUV_UVProject
from . import DUV_UVUnwrap
from . import DUV_UVInset
from . import DUV_UVTrim
from . import DUV_ApplyMaterial
from . import DUV_UVBoxmap

import importlib
if 'bpy' in locals():
    importlib.reload(DUV_UVTranslate)
    importlib.reload(DUV_UVRotate)
    importlib.reload(DUV_UVScale)
    importlib.reload(DUV_UVExtend) 
    importlib.reload(DUV_UVStitch)
    importlib.reload(DUV_UVTransfer) 
    importlib.reload(DUV_UVCycle) 
    importlib.reload(DUV_UVCopy)
    importlib.reload(DUV_UVMirror) 
    importlib.reload(DUV_UVMoveToEdge)
    importlib.reload(DUV_Utils)
    importlib.reload(DUV_HotSpot)
    importlib.reload(DUV_UVProject)
    importlib.reload(DUV_UVUnwrap)
    importlib.reload(DUV_UVInset)
    importlib.reload(DUV_UVTrim)
    importlib.reload(DUV_ApplyMaterial)
    importlib.reload(DUV_UVBoxmap)

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
        
        #row.label(text="Atlas Object:")
        #row.prop_search(context.scene, "subrect_atlas", context.scene, "objects", text="", icon="MOD_MULTIRES")
        #row = col.row(align = True)
        
        col.separator()
        
        radiobutton = (
            context.scene.duv_hotspot_atlas1,
            context.scene.duv_hotspot_atlas1,
            context.scene.duv_hotspot_atlas2,
            context.scene.duv_hotspot_atlas3,
            context.scene.duv_hotspot_atlas4,
            context.scene.duv_hotspot_atlas5,
            context.scene.duv_hotspot_atlas6,
            context.scene.duv_hotspot_atlas7,
            context.scene.duv_hotspot_atlas8,
        )
        
        listsize = 1
        col.prop(context.scene, "atlas_list_size", text="atlas count:")
        
        
        while listsize <= context.scene.atlas_list_size:
            row = col.row(align = True)      
            #row.prop(context.scene, "duv_hotspot_atlas1", icon="IPO_SINE", text="")
            if radiobutton[listsize]: 
                op = row.operator("view3d.dreamuv_pushhotspot", text="", icon="RADIOBUT_ON")
            if not radiobutton[listsize]: 
                op = row.operator("view3d.dreamuv_pushhotspot", text="", icon="RADIOBUT_OFF")
            op.index = listsize
            row.prop_search(context.scene, "subrect_atlas"+str(listsize), context.scene, "objects", text="", icon="MOD_MULTIRES")
            row.prop_search(context.scene, "duv_hotspotmaterial"+str(listsize), bpy.data, "materials", text="")
            listsize += 1
                
        col.separator()
        row = col.row(align = True)
        row.label(text="Atlas Scale:")
        row.prop(context.scene, "duvhotspotscale", text="")
        row = col.row(align = True)
        #row.label(text="Hotspot material:")
        #row.prop_search(context.scene, "duv_hotspotmaterial", bpy.data, "materials", text="")
        
        
        
        row = col.row(align = True)
        row.prop(context.scene, "duv_hotspotuseinset", icon="FULLSCREEN_EXIT", text="inset")
        row.separator()
        row.prop(context.scene, "hotspotinsetpixels", text="")
        row.prop(context.scene, "hotspotinsettexsize", text="")

        col.separator()
        row = col.row(align = True)
        row.operator("view3d.dreamuv_hotspotter", text="HotSpot", icon="SHADERFX")
        row.prop(context.scene, "duv_useorientation", icon="EVENT_W", text="")
        row.prop(context.scene, "duv_usemirrorx", icon="EVENT_X", text="")
        row.prop(context.scene, "duv_usemirrory", icon="EVENT_Y", text="")
        row.prop(context.scene, "duv_autoboxmap", icon="EVENT_B", text="")
        row.prop(context.scene, "duv_hotspot_uv1", icon="IPO_SINE", text="")
        row.prop(context.scene, "duv_hotspot_uv2", icon="IPO_QUAD", text="")

        #trim
        col.separator()
        box = layout.box()
        if bpy.context.object.mode != 'EDIT':
            box.enabled = False
        col = box.column(align=True)
        col.label(text="Trim Tool:")
        row = col.row(align = True)
        
        row.label(text="Trim/Cap Atlas:")
        row.prop_search(context.scene, "trim_atlas", context.scene, "objects", text="", icon="LINENUMBERS_ON")
        row = col.row(align = True)
        #row.prop(context.scene, "trim_index", text="")
        row.label(text="Trim index: "+str(context.scene.trim_index))
        #row = col.row(align = True) 
        op = row.operator("view3d.dreamuv_uvtrimnext", text=" ", icon="BACK")
        op.reverse = True
        op = row.operator("view3d.dreamuv_uvtrimnext", text=" ", icon="FORWARD")
        op.reverse = False
        
        row = col.row(align = True)
        row.label(text="Cap index: "+str(context.scene.cap_index))
        #row = col.row(align = True) 
        op = row.operator("view3d.dreamuv_uvcapnext", text=" ", icon="BACK")
        op.reverse = True
        op = row.operator("view3d.dreamuv_uvcapnext", text=" ", icon="FORWARD")
        op.reverse = False
        
        row = col.row(align = True)
        row.enabled = not context.scene.duv_uvtrim_randomshift
        row.prop(context.scene, "duv_uvtrim_bounds", icon="CENTER_ONLY", text="bounds")
        row.separator()
        row.prop(context.scene, "duv_uvtrim_min", text="")
        row.prop(context.scene, "duv_uvtrim_max", text="")
        
        col.separator()
        row = col.row(align = True) 
        row.operator("view3d.dreamuv_uvtrim", text="Trim", icon="SEQ_SEQUENCER")

        row.operator("view3d.dreamuv_uvcap", text="Cap", icon="MOD_BUILD")
        
        row.prop(context.scene, "duv_uvtrim_randomshift", icon="NLA_PUSHDOWN", text="")
        row.prop(context.scene, "duv_autoboxmaptrim", icon="EVENT_B", text="")
        row.prop(context.scene, "duv_trimcap_uv1", icon="IPO_SINE", text="")
        row.prop(context.scene, "duv_trimcap_uv2", icon="IPO_QUAD", text="")
        
        
        
        #boxmap
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Boxmapping Tool:")
        row = col.row(align = True)
        row.label(text="Box Reference:")
        row.prop_search(context.scene, "uv_box", context.scene, "objects", text="", icon="MOD_MULTIRES")
        row = col.row(align = True)
        row.operator("view3d.dreamuv_uvboxmap", text="Boxmap", icon="FILE_3D")
        row.prop(context.scene, "duv_boxmap_uv1", icon="IPO_SINE", text="")
        row.prop(context.scene, "duv_boxmap_uv2", icon="IPO_QUAD", text="")
        
               
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        col.label(text="UV sets:")
        row = col.row(align = True)

        op = row.operator("view3d.dreamuv_uvcopy", text="copy uv1->2", icon="XRAY")
        op.reverse = False
        op = row.operator("view3d.dreamuv_uvcopy", text="copy uv2->1", icon="XRAY")
        op.reverse = True
        
        if bpy.context.object.type == 'MESH':
            me = bpy.context.object.data
            #me = bpy.context.object.mesh

            row = col.row()
            col = row.column()

            col.template_list("MESH_UL_uvmaps", "uvmaps", me, "uv_layers", me.uv_layers, "active_index", rows=2)
            col = row.column(align=True)
            col.operator("mesh.uv_texture_add", icon='ADD', text="")
            col.operator("mesh.uv_texture_remove", icon='REMOVE', text="")
        
        #context.scene.duv_experimentaltools = True
        #if context.scene.duv_experimentaltools is True:
        col.separator()
                
        

        

        col = self.layout.column(align = True)
        col2= self.layout.column(align = True)
        col2.label(text="Send feedback to:")
        row = col2.row(align = True) 
        row.label(text="@Leukbaars@mastodon.gamedev.place")
        row.prop(context.scene, "duv_experimentaltools", icon="HEART", text="")
        
        


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
    DUV_UVCopy.DREAMUV_OT_uv_copy,
    DUV_UVMirror.DREAMUV_OT_uv_mirror,
    DUV_UVMoveToEdge.DREAMUV_OT_uv_move_to_edge,
    DUV_UVProject.DREAMUV_OT_uv_project,
    DUV_UVUnwrap.DREAMUV_OT_uv_unwrap_square,
    DUV_HotSpot.DREAMUV_OT_hotspotter,
    DUV_HotSpot.DREAMUV_OT_pushhotspot,
    DUV_UVInset.DREAMUV_OT_uv_inset,
    DUV_UVInset.DREAMUV_OT_uv_inset_step,
    DUV_UVTrim.DREAMUV_OT_uv_trim,
    DUV_UVTrim.DREAMUV_OT_uv_cap,
    DUV_UVTrim.DREAMUV_OT_uv_trimnext,
    DUV_UVTrim.DREAMUV_OT_uv_capnext,
    DUV_ApplyMaterial.DREAMUV_OT_apply_material,
    DUV_UVBoxmap.DREAMUV_OT_uv_boxmap,
)

def poll_material(self, material):
    return not material.is_grease_pencil

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.subrect_atlas = bpy.props.PointerProperty (name="atlas",type=bpy.types.Object,description="atlas object")
    bpy.types.Scene.uv_box = bpy.props.PointerProperty (name="uvbox",type=bpy.types.Object,description="uv box")
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
    bpy.types.Scene.duvhotspotscale = bpy.props.FloatProperty (name = "duvhotspotscale",default = 1.0,description = "Hotspotting scale multiplier")
    bpy.types.Scene.duv_hotspotmaterial = bpy.props.PointerProperty (name="duv_hotspotmaterial",type=bpy.types.Material,poll=poll_material,description="Hotspot material")
    bpy.types.Scene.duv_hotspotuseinset = bpy.props.BoolProperty (name = "duv_hotspotuseinset",default = False,description = "Use inset when hotspotting")
    bpy.types.Scene.hotspotinsetpixels = bpy.props.FloatProperty (name = "hotspot inset pixel amount",default = 1.0,description = "")
    bpy.types.Scene.hotspotinsettexsize = bpy.props.FloatProperty (name = "hotspot texture size",default = 1024.0,description = "")
    bpy.types.Scene.duv_experimentaltools = bpy.props.BoolProperty (name = "duv_experimentaltools",default = False,description = "Show experimental tools")
    bpy.types.Scene.duv_uv2copy = bpy.props.BoolProperty (name = "duv_uv2copy",default = False,description = "Copy uv2")
    bpy.types.Scene.duv_hotspot_uv1 = bpy.props.BoolProperty (name = "duv_hotspot_uv1",default = False,description = "Always hotspot UV 1")
    bpy.types.Scene.duv_hotspot_uv2 = bpy.props.BoolProperty (name = "duv_hotspot_uv2",default = False,description = "Always hotspot UV 2")
    bpy.types.Scene.duv_boxmap_uv1 = bpy.props.BoolProperty (name = "duv_boxmap_uv1",default = False,description = "Always box map UV 1")
    bpy.types.Scene.duv_boxmap_uv2 = bpy.props.BoolProperty (name = "duv_boxmap_uv2",default = False,description = "Always box map UV 2")
    bpy.types.Scene.duv_autoboxmap = bpy.props.BoolProperty (name = "duv_autoboxmap",default = False,description = "Auto apply boxmap after hotspot operation")
    bpy.types.Scene.duv_trimcap_uv1 = bpy.props.BoolProperty (name = "duv_trimcap_uv1",default = False,description = "Always apply trim/cap to UV 1")
    bpy.types.Scene.duv_trimcap_uv2 = bpy.props.BoolProperty (name = "duv_trimcap_uv2",default = False,description = "Always apply trim/cap to UV 2")
    bpy.types.Scene.duv_autoboxmaptrim = bpy.props.BoolProperty (name = "duv_autoboxmaptrim",default = False,description = "Auto apply boxmap after trim/cap operation")
    bpy.types.Scene.duv_uvtrim_randomshift = bpy.props.BoolProperty (name = "duv_uvtrim_randomshift",default = False,description = "Randomize trim position along tiling axis")
    bpy.types.Scene.duv_uvtrim_bounds = bpy.props.BoolProperty (name = "duv_uvtrim_bounds",default = False,description = "Scale trim to boundary region")
    bpy.types.Scene.duv_uvtrim_min = bpy.props.FloatProperty (name = "duv_uvtrim_min",default = 0.0,description = "Boundary start")
    bpy.types.Scene.duv_uvtrim_max = bpy.props.FloatProperty (name = "duv_uvtrim_max",default = 1.0,description = "Boundary end")
    
    bpy.types.Scene.subrect_atlas1 = bpy.props.PointerProperty (name="atlas1",type=bpy.types.Object,description="atlas1")
    bpy.types.Scene.subrect_atlas2 = bpy.props.PointerProperty (name="atlas2",type=bpy.types.Object,description="atlas2")
    bpy.types.Scene.subrect_atlas3 = bpy.props.PointerProperty (name="atlas3",type=bpy.types.Object,description="atlas3")
    bpy.types.Scene.subrect_atlas4 = bpy.props.PointerProperty (name="atlas4",type=bpy.types.Object,description="atlas4")
    bpy.types.Scene.subrect_atlas5 = bpy.props.PointerProperty (name="atlas5",type=bpy.types.Object,description="atlas5")
    bpy.types.Scene.subrect_atlas6 = bpy.props.PointerProperty (name="atlas6",type=bpy.types.Object,description="atlas6")
    bpy.types.Scene.subrect_atlas7 = bpy.props.PointerProperty (name="atlas7",type=bpy.types.Object,description="atlas7")
    bpy.types.Scene.subrect_atlas8 = bpy.props.PointerProperty (name="atlas8",type=bpy.types.Object,description="atlas8")

    bpy.types.Scene.duv_hotspotmaterial1 = bpy.props.PointerProperty (name="duv_hotspotmaterial1",type=bpy.types.Material,poll=poll_material,description="Hotspot material 1")
    bpy.types.Scene.duv_hotspotmaterial2 = bpy.props.PointerProperty (name="duv_hotspotmaterial2",type=bpy.types.Material,poll=poll_material,description="Hotspot material 2")
    bpy.types.Scene.duv_hotspotmaterial3 = bpy.props.PointerProperty (name="duv_hotspotmaterial3",type=bpy.types.Material,poll=poll_material,description="Hotspot material 3")
    bpy.types.Scene.duv_hotspotmaterial4 = bpy.props.PointerProperty (name="duv_hotspotmaterial4",type=bpy.types.Material,poll=poll_material,description="Hotspot material 4")
    bpy.types.Scene.duv_hotspotmaterial5 = bpy.props.PointerProperty (name="duv_hotspotmaterial5",type=bpy.types.Material,poll=poll_material,description="Hotspot material 5")
    bpy.types.Scene.duv_hotspotmaterial6 = bpy.props.PointerProperty (name="duv_hotspotmaterial6",type=bpy.types.Material,poll=poll_material,description="Hotspot material 6")
    bpy.types.Scene.duv_hotspotmaterial7 = bpy.props.PointerProperty (name="duv_hotspotmaterial7",type=bpy.types.Material,poll=poll_material,description="Hotspot material 7")
    bpy.types.Scene.duv_hotspotmaterial8 = bpy.props.PointerProperty (name="duv_hotspotmaterial8",type=bpy.types.Material,poll=poll_material,description="Hotspot material 8")
    
    bpy.types.Scene.duv_hotspot_atlas1 = bpy.props.BoolProperty (name = "duv_hotspot_atlas1",default = True,description = "duv_hotspot_atlas1")
    bpy.types.Scene.duv_hotspot_atlas2 = bpy.props.BoolProperty (name = "duv_hotspot_atlas2",default = False,description = "duv_hotspot_atlas2")
    bpy.types.Scene.duv_hotspot_atlas3 = bpy.props.BoolProperty (name = "duv_hotspot_atlas3",default = False,description = "duv_hotspot_atlas3")
    bpy.types.Scene.duv_hotspot_atlas4 = bpy.props.BoolProperty (name = "duv_hotspot_atlas4",default = False,description = "duv_hotspot_atlas4")
    bpy.types.Scene.duv_hotspot_atlas5 = bpy.props.BoolProperty (name = "duv_hotspot_atlas5",default = False,description = "duv_hotspot_atlas5")
    bpy.types.Scene.duv_hotspot_atlas6 = bpy.props.BoolProperty (name = "duv_hotspot_atlas6",default = False,description = "duv_hotspot_atlas6")
    bpy.types.Scene.duv_hotspot_atlas7 = bpy.props.BoolProperty (name = "duv_hotspot_atlas7",default = False,description = "duv_hotspot_atlas7")
    bpy.types.Scene.duv_hotspot_atlas8 = bpy.props.BoolProperty (name = "duv_hotspot_atlas8",default = False,description = "duv_hotspot_atlas8")
    
    bpy.types.Scene.atlas_list_size = bpy.props.IntProperty (
        name = "atlas_list_size",
        default = 1,
        min = 1,
        max = 8,
        description = "atlas_list_size",
        )
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
