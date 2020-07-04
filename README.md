# DreamUV

## About
DreamUV is a collection of tools that allow you to manipulate UVs in the 3D viewport. This toolset is designed to be used with reusable textures like tiling textures, trimsheets and texture atlases. Its intent is to allow you to texture your geometry without having to exit the 3D view, saving you time and improving flexibility.

![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_header.jpg)

## Installation

* download as a zip and in user Preferences/Add-ons, use "Install from File..."
* DreamUV should now be visible in the add-ons tab, in the UV category.
* once activated, you can find DreamUV in the toolbar in Edit mode.

## Using DreamUV

After installing, you can find the DreamUV toolset in the toolbar of the 3D viewport window. It'll appear when in edit mode.

![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_tools.jpg)

## Viewport UV Tools

The Viewport UV Tools are a collection of tool to directly manipulate UV maps in the 3D Viewport. These tools are particularly useful when working with tiling or trim based materials.

The **Move, Scale and Rotate** tools allow you to transform your uvs in realtime just like you would be transforming a mesh. 
Some keyboard and mouse combos can be used while the tool is used. They have been set up to work similarly to the default Blender transform tools:

* X: constrain translate/scale to x-axis
* Y: constrain translate/scale to y-axis
* MIDDLE MOUSE: hold and drag along the x or y axis to constrain the tool to that axis. Release to lock the constraint. 
* SHIFT: precision mode
* CTRL: stepped mode
* CTRL+SHIFT: stepped mode with smaller intervals

The **Move, Scale and Rotate** tools also have buttons to transform your UV by discrete steps, which can be set using the snap sizes.

The **extend** Tool will unwrap selected faces and attach them to the active face.

The **Stitch** Tool will stitch the uvs of two selected faces on their shared edge

The **Cycle** Tool will rotate the selected face's uvs by 90 degrees and keep it confined within its boundaries.

The **Mirror** Tools will mirror selected uvs while also keeping the uvs confined within its boundaries.

The **Move to UV Edge** will move the entire uv to the 0-1 uv boundary. This is useful to align a face to a texture's edge.

## Unwrapping Tools:

**Square Fit Unwrap** will try to unwrap your selection fitted to a square. It's useful to unwrap patches, and is particularly useful when unwrapping pipes. 

**Blender Unwrap** is the standard blender unwrap tool. 

(more unwrapping tools are planned, like planar and box mapping options. Watch this space!)

## UV Transfer Tool:

The **UV Transfer Tool** allows you to essentially copy paste a uv to a different spot. The top row are coordinates that represent a uv clipboard. You can type them in manually or use the grab from selection to save a UV boundary. The transfer to selection button will map the saved uv to your selection.

## Hotspotting:

Hotspotting is a technique to quickly assign uv's to UV islands by referencing a predefined uv atlas. The DreamUV hotspot tool will attempt its best to find an appropriate sized rectangle on the atlas and fit it to the mesh geometry.

For the hotspotting tool to work correctly, an atlas needs to be created. This is simply a mesh consisting of a variety of different sized rectangles. For example:
![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_atlas.jpg)
This is just one example layout, any layout should work.

Keep in mind to scale the atlas geometry to a similar scale you want to uv's to be applied to your final mesh. Also make sure that the atlas object scale is set to 1 to make sure the sizes are transferred correctly.

To hotspot a mesh, simply select the faces you want to hotspot and click the hotspot button. Clicking multiple times will make the tool cycle through different variations and uv placement. The mesh will be split into multiple uv islands that are hotspotted individually, using hard edges and seams. Its highly recommended to place extra seams manually to guide the tool and try to divide up your geometry into rectangular patches.
![screenshot](http://www.brameulaers.net/blender/addons/github_images/dreamuv_hotspot.jpg)

If you have any feedback you can just message me via twitter: @leukbaars
