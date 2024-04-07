import bpy
import bmesh

class DREAMUV_OT_uv_copy(bpy.types.Operator):
    """Copy selected UVs to other UV set"""
    bl_idname = "view3d.dreamuv_uvcopy"
    bl_label = "copy selected uvs from uv2 to uv1"
    bl_options = {"UNDO"}
    #bl_options = {'SEARCH_ON_KEY_PRESS'}  
    
    reverse : bpy.props.BoolProperty()
    
    def execute(self, context):        
        if len(bpy.context.object.data.uv_layers) == 2:                        
            
            #make sure active object is actually selected in edit mode:
            if bpy.context.object.mode == 'EDIT':
                bpy.context.object.select_set(True)

            #check for object or edit mode:
            objectmode = False
            if bpy.context.object.mode == 'OBJECT':
                objectmode = True
                #switch to edit and select all
                bpy.ops.object.editmode_toggle() 
                bpy.ops.mesh.select_all(action='SELECT')   
        

            obj = bpy.context.view_layer.objects.active
            bm = bmesh.from_edit_mesh(obj.data)
            uv_layer = bm.loops.layers.uv[0]
            uv_layer2 = bm.loops.layers.uv[1]

            for f in bm.faces:
                if f.select:
                    for vert in f.loops:
                        if self.reverse == True:
                            vert[uv_layer].uv.x = vert[uv_layer2].uv.x
                            vert[uv_layer].uv.y = vert[uv_layer2].uv.y
                        if self.reverse == False:
                            vert[uv_layer2].uv.x = vert[uv_layer].uv.x
                            vert[uv_layer2].uv.y = vert[uv_layer].uv.y

            bmesh.update_edit_mesh(obj.data)
            
            if objectmode is True:
                bpy.ops.object.editmode_toggle() 
                    
        return {'FINISHED'}
