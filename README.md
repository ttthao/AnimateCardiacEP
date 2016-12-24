# Electrophysiology Animation for Blender

### Summary:
Use Blender to animate the electrophysiology of a ventricular model with voltage solutions created by CMRG's Continuity. For Chris Villongco (Postdoctoral Researcher, UCSD). 

### To-do List:
1. Convert the script into a plugin with a Blender UI.
2. Get rid of hardcoded constants. Move it to the interface, so the user can define it.
3. Query existing GPUs and split task among GPUs.
4. Include necessary materials/properties so vertex color maps can be seen when rendered.
5. Create checks to make sure that the START/END time is valid.

### A Note on Vertices in Blender:
Blender has two different methods of indexing vertices; we will regard them as global versus local indexing. Global vertices are indexed with respect to the entire 3D figure. For example, a regular cube has 8 global vertices, that can be indexed in some way. However, local vertices are indexed with respect to each face of that figure. For example, a cube has 6 faces, and each face has four local vertices. This means that a cube has (6 x 4) = 24 local vertices. In other words, a local vertex is associated with a specific face of a figure, so there can be multiple local vertices corresponding to a single global vertex (a cube has three local vertices to a single global vertex since each global vertex touches three faces).

### Why We Care:
The voltage solution is created in terms of global vertices. However, the way we color vertices is with a Blender feature called "vertex color layer" that utilizes local vertices. Thus, we need to create a mapping from the local to global vertices. This mapping occurs in a predictable pattern: if we iterate through each "face" in "mesh.polygons" and each "global_vertex" in each "face.vertices", the order in which this is iterated corresponds exactly with the local vertices used by vertex color layers.

### Try It Out:
We will provide testfiles, including the Blender model and voltage solution colormap very soon. Stay tuned!

### Created by:
* Jonathan Chiu (@jonathanhchiu)
* Tommy Truong (@ttthao)
* Chris Villongco (@ctvillongco)

### For Inquiries:
Please email jonathanhchiu@gmail.com, tttruong701@gmail.com, or ctvillongco@gmail.com for questions or requests.
