#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

bl_info = {
    "name": "BRM_UVTranslateView",
    "category": "Mesh",
    "author": "Bram Eulaers",
    "description": "Translate the selected faces'UVs inside the 3D Viewport. WIP. Check for updates @leukbaars. Command: brm.uvtranslateview"
    }

import bpy
import bmesh
import math
import mathutils

class BRM_UVTranslateView(bpy.types.Operator):
    """BRM_UVTranslateView"""
    bl_idname = "brm.uvtranslateview"
    bl_label = "BRM_UVTranslateView"
    bl_options = {"GRAB_CURSOR","UNDO"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None
    bm_orig = None
    
    shiftreset = False
    delta=0
    
    xlock=False
    ylock=False
    
    def invoke(self, context, event):
        
        self.shiftreset = False
        self.xlock=False
        self.ylock=False
        
        #object->edit switch seems to "lock" the data. Ugly but hey it works 
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            
            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)
            self.bm_orig = bmesh.new()
            self.bm_orig.from_mesh(self.mesh)
  
            #have to do this for some reason  
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()
            self.bm_orig.faces.ensure_lookup_table()
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
    
    def modal(self, context, event):
        
        if event.type == 'X':
            self.xlock=False
            self.ylock=True
        if event.type == 'Y':
            self.xlock=True
            self.ylock=False
            
        if event.type == 'MOUSEMOVE':
            
            
            self.delta=((self.first_mouse_x - event.mouse_x),(self.first_mouse_y - event.mouse_y))
            self.delta = mathutils.Vector(self.delta)*0.001
            
            if event.shift and not event.ctrl:
                self.delta*=.1
                #reset origin position to shift into precision mode
                if not self.shiftreset:
                    self.shiftreset=True
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                    self.delta=(0,0)
                    self.delta = mathutils.Vector(self.delta)
            
            else:
                #reset origin position to shift into normal mode
                if self.shiftreset:
                    self.shiftreset=False
                    self.first_mouse_x = event.mouse_x
                    self.first_mouse_y = event.mouse_y
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                    self.delta=(0,0)
                    self.delta = mathutils.Vector(self.delta)
                                
            if event.ctrl and not event.shift:
                self.delta.x=math.floor(self.delta.x*4)/4
                self.delta.y=math.floor(self.delta.y*4)/4
            if event.ctrl and event.shift:
                self.delta.x=math.floor(self.delta.x*16)/16
                self.delta.y=math.floor(self.delta.y*16)/16

            #loop through every selected face and move the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        if not self.xlock:
                            vert[self.bm.loops.layers.uv.active].uv.x = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x + self.delta.x
                        if not self.ylock:
                            vert[self.bm.loops.layers.uv.active].uv.y = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y + self.delta.y
            
            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            #reset all uvs to reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        vert[self.bm.loops.layers.uv.active].uv = self.bm_orig.faces[i].loops[o][self.bm_orig.loops.layers.uv.active].uv
            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(BRM_UVTranslateView)


def unregister():
    bpy.utils.unregister_class(BRM_UVTranslateView)


if __name__ == "__main__":
    register()

