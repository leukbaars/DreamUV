This is a fork of https://github.com/leukbaars/Blender

* adds BRḾ-UVTools subfolder in Blender's addon folder
* adds the BRM UVTools into Blender's UV Menu

---

# BRM UVTools

## About
This script will add the ability to translate, scale and rotate UV coordinates directly in the 3D Viewport. It should be very useful for 3D artists who find themselves working often with tiling textures that don't require a clean UV layout. Level editing packages such as hammer commonly allow you to edit UV coordinates without a 2D uv editor, and this replicates this type of functionality in Blender. I'm sure there are many other uses too.

## Installation
* Clone the repo into blenders addon folder
* Alternatively, download as a zip and extract it into the addon folder
    * rename 'BRM-UVTools-master' folder to just 'BRM-UVTools'
* activate BRM UVTools in the addons tab of the user preferences
* once activated, you can find BRM UVTools in Blenders UV menu (default keymapped to 'U') in Edit mode

## Using BRM UVTools

Some keyboard and mouse combos can be used while running the tool. They have been set up to work similarly to the default Blender transform tools:

* X: constrain translate/scale to x-axis
* Y: constrain translate/scale to y-axis
* MIDDLE MOUSE: hold and drag along the x or y axis to constrain the tool to that axis. Release to lock the constraint. 
* SHIFT: precision mode
* CTRL: stepped mode
* CTRL+SHIFT: stepped mode with smaller intervals

If you have any feedback you can just message me via twitter: @leukbaars
