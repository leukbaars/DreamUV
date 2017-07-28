#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

#   TODO
#-precision mode for rotation
#-draw on screen handles that fit with Blender's transform tools

bl_info = {
    "name": "BRM UV Tools",
    "category": "3D View",
    "author": "Bram Eulaers",
    "description": "Edit selected faces'UVs directly inside the 3D Viewport. WIP. Check for updates @leukbaars",
    "version": (0, 6)
}

import bpy
import bmesh
import math
import mathutils


class BRM_UVPanel(bpy.types.Panel):
    """UV Tools Panel Test!"""
    bl_label = "BRM UV Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Shading / UVs'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Viewport UV tools:")
        col.operator("mesh.brm_uvtranslate", text="Translate")
        col.operator("mesh.brm_uvscale", text="Scale")
        col.operator("mesh.brm_uvrotate", text="Rotate")



     
class BRM_UVTranslate(bpy.types.Operator):
    """Translate UVs in the 3D Viewport"""
    bl_idname = "mesh.brm_uvtranslate"
    bl_label = "BRM_UVTranslate"
    bl_options = {"GRAB_CURSOR","UNDO","BLOCKING"}

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
    
    stateswitch = False
    mousetestx=False
    constrainttest = False
    
    def invoke(self, context, event):
        
        self.shiftreset = False
        self.xlock=False
        self.ylock=False
        self.constrainttest = False
        self.stateswitch = False
        self.mousetestx=False
        
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
        
        #setup constraints first   
        if event.type == 'X':
            self.stateswitch=True
            self.xlock=False
            self.ylock=True
        if event.type == 'Y':
            self.stateswitch=True
            self.xlock=True
            self.ylock=False
        
        #test is middle mouse held down
        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.constrainttest = True
        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.constrainttest = False
        
        #test if mouse is in the right quadrant for X or Y movement
        if self.constrainttest:
            mouseangle=math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            mousetestx=False
            if (mouseangle < 0.785 and mouseangle > -0.785) or (mouseangle > 2.355 or mouseangle < -2.355): 
               mousetestx=True           
            if mousetestx:
                self.xlock=False
                self.ylock=True
            else:
                self.xlock=True
                self.ylock=False 
            if mousetestx is not self.mousetestx:
                self.stateswitch=True
                self.mousetestx = not self.mousetestx
       
        if self.stateswitch:
            self.stateswitch=False
            #reset to start editing from start position
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        vert[self.bm.loops.layers.uv.active].uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv     
                         
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




class BRM_UVScale(bpy.types.Operator):
    """Scale UVs in the 3D Viewport"""
    bl_idname = "mesh.brm_uvscale"
    bl_label = "BRM_UVScale"
    bl_options = {"GRAB_CURSOR","UNDO","BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None
    
    xcenter=0
    ycenter=0
    
    shiftreset = False
    
    xlock=False
    ylock=False
    constrainttest = False
    
    s1=3
    s2=.5
    
    def invoke(self, context, event):
        
        #object->edit switch seems to "lock" the data. Ugly but hey it works 
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.shiftreset = False
        self.xlock=False
        self.ylock=False
        self.constrainttest = False
        
        if context.object:
            self.first_mouse_x = event.mouse_x+1000/self.s1
            self.first_mouse_y = event.mouse_y+1000/self.s1
            
            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)
  
            #have to do this for some reason  
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()

            #find "center"
            #loop through every selected face and move the uv's using original uv as reference
            xmin=0
            xmax=0
            ymin=0
            ymax=0
            first = True
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        if first:
                            xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            xmax=vert[self.bm.loops.layers.uv.active].uv.x
                            ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            ymax=vert[self.bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if vert[self.bm.loops.layers.uv.active].uv.x < xmin:
                                xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            elif vert[self.bm.loops.layers.uv.active].uv.x > xmax:
                                xmax=vert[self.bm.loops.layers.uv.active].uv.x
                                
                            if vert[self.bm.loops.layers.uv.active].uv.y < ymin:
                                ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            elif vert[self.bm.loops.layers.uv.active].uv.y > ymax:
                                ymax=vert[self.bm.loops.layers.uv.active].uv.y
            
            self.xcenter=(xmin+xmax)/2
            self.ycenter=(ymin+ymax)/2

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
        
        #test is middle mouse held down
        if event.type == 'MIDDLEMOUSE' and event.value == 'PRESS':
            self.constrainttest = True
        if event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            self.constrainttest = False
        
        #test if mouse is in the right quadrant for X or Y movement
        if self.constrainttest:
            mouseangle=math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            mousetestx=False
            if (mouseangle < 0.785 and mouseangle > -0.785) or (mouseangle > 2.355 or mouseangle < -2.355): 
               mousetestx=True           
            if mousetestx:
                self.xlock=True
                self.ylock=False
            else:
                self.xlock=False
                self.ylock=True 
        
        
        if event.type == 'MOUSEMOVE':
            
            deltax = self.first_mouse_x - event.mouse_x
            deltay = self.first_mouse_y - event.mouse_y
            
            
            if event.shift and not event.ctrl:
                #self.delta*=.1
                #reset origin position to shift into precision mode
                
                if not self.shiftreset:
                    self.shiftreset=True
                    self.first_mouse_x = event.mouse_x+1000/self.s2
                    self.first_mouse_y = event.mouse_y+1000/self.s2
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                deltax = self.first_mouse_x - event.mouse_x
                deltay = self.first_mouse_y - event.mouse_y
                deltax*=0.001*self.s2
                deltay*=0.001*self.s2
            
            else:
                #reset origin position to shift into normal mode
                if self.shiftreset:
                    self.shiftreset=False
                    self.first_mouse_x = event.mouse_x+1000/self.s1
                    self.first_mouse_y = event.mouse_y+1000/self.s1
                    for i,face in enumerate(self.bm.faces):
                        if face.select:
                            for o,vert in enumerate(face.loops):
                                self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv = vert[self.bm.loops.layers.uv.active].uv
                deltax = self.first_mouse_x - event.mouse_x
                deltay = self.first_mouse_y - event.mouse_y
                deltax*=0.001*self.s1
                deltay*=0.001*self.s1
            
            if not self.xlock and not self.ylock:
                delta=(deltax+deltay)*.5
                deltax=delta
                deltay=delta
            
            if self.xlock:
                deltax=1
               
            if self.ylock:
                deltay=1
                
            if event.ctrl and not event.shift:
                deltax=math.floor(deltax*2)/2
                deltay=math.floor(deltay*2)/2
            if event.ctrl and event.shift:
                deltax=math.floor(deltax*8)/8
                deltay=math.floor(deltay*8)/8
            
            #loop through every selected face and move the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                                        
                        vert[self.bm.loops.layers.uv.active].uv.x=((deltax)*self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x)+((1-(deltax))*self.xcenter)
                        vert[self.bm.loops.layers.uv.active].uv.y=((deltay)*self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y)+((1-(deltay))*self.ycenter)
  
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
                        vert[self.bm.loops.layers.uv.active].uv = self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv
            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

class BRM_UVRotate(bpy.types.Operator):
    """Rotate UVs in the 3D Viewport"""
    bl_idname = "mesh.brm_uvrotate"
    bl_label = "BRM_UVRotate"
    bl_options = {"GRAB_CURSOR","UNDO","BLOCKING"}

    first_mouse_x = None
    first_value = None
    mesh = None
    bm = None
    bm2 = None
    
    xcenter=0
    ycenter=0
    
    startdelta=0
    
    def invoke(self, context, event):
        
        #object->edit switch seems to "lock" the data. Ugly but hey it works 
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.object:
            #self.first_mouse_x = event.mouse_x
            #self.first_mouse_y = event.mouse_y
            
            #test: set rotation center to viewport center for now
            #test: possibly change this to selection center?
            self.first_mouse_x = (bpy.context.region.width/2)+bpy.context.region.x
            self.first_mouse_y = (bpy.context.region.height/2)+bpy.context.region.y
            
            #get neutral angle from start location
            self.startdelta=math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            
            self.mesh = bpy.context.object.data
            self.bm = bmesh.from_edit_mesh(self.mesh)

            #save original for reference
            self.bm2 = bmesh.new()
            self.bm2.from_mesh(self.mesh)
  
            #have to do this for some reason  
            self.bm.faces.ensure_lookup_table()
            self.bm2.faces.ensure_lookup_table()

            #find "center"
            xmin=0
            xmax=0
            ymin=0
            ymax=0
            first = True
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):
                        if first:
                            xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            xmax=vert[self.bm.loops.layers.uv.active].uv.x
                            ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            ymax=vert[self.bm.loops.layers.uv.active].uv.y
                            first=False
                        else:
                            if vert[self.bm.loops.layers.uv.active].uv.x < xmin:
                                xmin=vert[self.bm.loops.layers.uv.active].uv.x
                            elif vert[self.bm.loops.layers.uv.active].uv.x > xmax:
                                xmax=vert[self.bm.loops.layers.uv.active].uv.x
                                
                            if vert[self.bm.loops.layers.uv.active].uv.y < ymin:
                                ymin=vert[self.bm.loops.layers.uv.active].uv.y
                            elif vert[self.bm.loops.layers.uv.active].uv.y > ymax:
                                ymax=vert[self.bm.loops.layers.uv.active].uv.y
            
            self.xcenter=(xmin+xmax)/2
            self.ycenter=(ymin+ymax)/2

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            
            #get angle of cursor from start pos in radians
            delta = -math.atan2(event.mouse_y-self.first_mouse_y,event.mouse_x-self.first_mouse_x)
            #neutralize angle for mouse start position
            delta+=self.startdelta
            
            print(event.mouse_x)
            vcenterx = (bpy.context.region.width/2)+bpy.context.region.x
            print(vcenterx)
            #step rotation
            if event.ctrl and not event.shift: 
                #PI/4=0.78539816339
                PIdiv=0.78539816339
                delta=math.floor(delta/PIdiv)*PIdiv
            if event.ctrl and event.shift: 
                #PI/16=0.19634954084
                PIdiv=0.19634954084
                delta=math.floor(delta/PIdiv)*PIdiv
            
            #loop through every selected face and scale the uv's using original uv as reference
            for i,face in enumerate(self.bm.faces):
                if face.select:
                    for o,vert in enumerate(face.loops):

                        px=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.x
                        py=self.bm2.faces[i].loops[o][self.bm2.loops.layers.uv.active].uv.y
                        
                        vert[self.bm.loops.layers.uv.active].uv.x = math.cos(delta) * (px-self.xcenter) - math.sin(delta) * (py-self.ycenter) + self.xcenter
                        vert[self.bm.loops.layers.uv.active].uv.y = math.sin(delta) * (px-self.xcenter) +  math.cos(delta) * (py-self.ycenter) + self.ycenter
  
            #update mesh
            bmesh.update_edit_mesh(self.mesh, False, False)

        elif event.type == 'LEFTMOUSE':
            #finish up and make sure changes are locked in place
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}



def register():
    bpy.utils.register_class(BRM_UVPanel)
    bpy.utils.register_class(BRM_UVTranslate)
    bpy.utils.register_class(BRM_UVScale)
    bpy.utils.register_class(BRM_UVRotate)


def unregister():
    bpy.utils.unregister_class(BRM_UVPanel)
    bpy.utils.unregister_class(BRM_UVTranslate)
    bpy.utils.unregister_class(BRM_UVScale)
    bpy.utils.unregister_class(BRM_UVRotate)
        
if __name__ == "__main__":
    register()
