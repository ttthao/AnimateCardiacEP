import bpy
import numpy as np 

class EpAnimatorPanel(bpy.types.Panel):
    """
    Temporary User Interface for the "mesh.animate_ep" operation. Lies
    in the "Create" tab in the Tools" bar. Only viewable in the 3D viewport
    when in object mode.

    WILL BE CHANGED LATER.
    """
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_label = "Animate Electrophysiology"

    def draw(self, context):
        """
        Create a new column in the "Create" tab and add a simple "Animate"
        button that will invoke the "animate_ep" operator on the active
        object.
        """
        TheCol = self.layout.column(align=True)
        TheCol.operator("mesh.animate_ep", text="Animate!")

class AnimateEp(bpy.types.Operator):
    bl_idname = "mesh.animate_ep"
    bl_label = "Animate Electrophysiology"
    
    def execute(self, context):
        """
        Apply and render the colormap from the voltage solution onto the 
        ventricular model for each frame. The voltage solution is generated
        CMRG's Continuity modeling software and then converted into a
        colormap via matplotlib. It is saved as a NumPy matrix with RGB values
        for each global vertex for each timestep.

        Given a mapping between global and local vertices, coloring the
        model is simple: for each local vertex, determine if its corresponding
        global vertex is on the surface of the model (we only want to color
        the surface). If it is, we grab the color from the colormap using
        its corresponding global vertex and timestep as indices, and apply it
        to the vertex color layer's RGB "color" property. Finally we render that
        frame and move on to the next one.
        
        Dictionary of Hardcoded Constants:
        * VSOLUTION: filepath of the voltage solution colormap.
        * SURFACE: name of the vertex group that contains all the vertices in the
        surface.
        * RENDER: where you want these frames to be saved to
        * START:  what frame to start at
        * END: what frame to end at 

        Params:
        context: context object of this Blender session

        Returns: 
        {'FINISHED'}, signal to Blender that operation is successfully completed.
        """
        VSOLUTION = ''
        SURFACE = ''
        RENDER = ''
        START = 0
        END = 100

        # Select the active object, mesh, and scene 
        scene = bpy.context.scene
        obj = scene.objects.active
        mesh = obj.data

        # Load the voltage solution colormap numpy file
        colormap = np.load(VSOLUTION)

        # Create a dictionary mapping each local vertex to global vertex
        local_vertex = 0

        # Iterate through each face
        for poly in mesh.polygons:

            # Iterate through each global vertex in each face
            for global_vertex in poly.vertices:
                reducedMap[local_vertex] = global_vertex
                local_vertex += 1

        # Create listing of vertex groups in active object
        vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

        # Dictionary with (key, value) = (vertex index, groups it belongs to)
        vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}

        # Color the vertices
        for frame in range(START, END):

            # Move cursor to next keyframe location before every iteration
            bpy.context.scene.frame_set(frame=frame)

            # Iterate through each local vertex
            local_vertex = 0
            for poly in mesh.polygons:
                for global_vertex in poly.vertices:

                    # Look up in the dictionary if a vertex belongs in the "surface"
                    if SURFACE in vgroups[reducedMap[local_vertex]]:

                        # Color only the vertices in the surface
                        vertex_color_layer.data[local_vertex].color = vsoln_colormap[frame, global_vertex][0:3]
                    local_vertex += 1

            # Render to specified directory
            scene.render.filepath = RENDER + '/frame_%d.jpg' % frame
            bpy.ops.render.render(write_still=True)

        return {"FINISHED"}

            
bpy.utils.register_class(AnimateEp)
bpy.utils.register_class(EpAnimatorPanel)