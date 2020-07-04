# DreamUV

## About
This script will add the ability to translate, scale and rotate UV coordinates directly in the 3D Viewport. It should be very useful for 3D artists who find themselves working often with tiling textures that don't require a clean UV layout.

## Installation

* download as a zip and in user Preferences/Add-ons, use "Install from File..."
* DreamUV should now be visible in the add-ons tab, in the UV category.
* once activated, you can find DreamUV in the toolbar in Edit mode.

## Using BRM UVTools



For the Move, Scale and Rotate tools, some keyboard and mouse combos can be used while the interactive tool is running. They have been set up to work similarly to the default Blender transform tools:

* X: constrain translate/scale to x-axis
* Y: constrain translate/scale to y-axis
* MIDDLE MOUSE: hold and drag along the x or y axis to constrain the tool to that axis. Release to lock the constraint. 
* SHIFT: precision mode
* CTRL: stepped mode
* CTRL+SHIFT: stepped mode with smaller intervals

## Hotspotting:

Hotspotting is a technique to quickly assign uv's to UV islands by referencing a predefined uv atlas. The DreamUV hotspot tool will attempt it's best to find an appropriate sized rectangle on the atlas and fit it to the mesh geometry.

For the hotspotting too to work correctly, an atlas needs to be created. This is simply a mesh consisting of a variety of different sized rectangles. For example:
![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_atlas.jpg)
This is just one example layout, any layout should work.

To hotspot a mesh, simply select the faces you want to hotspot and click the hotspot button. Clicking multiple times will make the tool cycle through different variations and uv placement. The mesh will be split into multiple uv islands that are hotspotted individually, using hard edges and seams. Its highly recommended to place extra seams manually to guide the tool and try to divide up your geometry into rectangular patches.
![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_hotspot.jpg)

If you have any feedback you can just message me via twitter: @leukbaars
