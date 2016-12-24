import bpy
import numpy as np
import time

# Arbitrary names
VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
KS_NAME = 'MyNewKeyingSet'                          # Keying Set
SURFACE = 'Surface'
MATERIAL = 'MyMaterial'
ATTRIBUTE = 'Attribute'
EMISSION = 'Emission'
OUTPUT = 'Material Output'

# Time constants
FRAME_NUM = 1                                      # Time between frames
TIME = 0                                            # Times in colormap
START = 0
KEYFRAMES = 66

# TODO Find the right place to run the job
with open('/data/tthao/blender/EP/logs/log0.txt', 'w') as f:

    # Blender constants
    scn = bpy.context.scene                             # Active scene
    obj = bpy.data.objects['BiV2_67584_RVmL']           # Active object
    mesh = obj.data                                     # Active object's mesh
    obj.select = True
    bpy.context.scene.objects.active = obj

    # Filepath
    # TODO Change me for different colormaps!
    FILEPATH = '/data/tthao/blender/EP/500ms.npy'

    # Read in numpy array containing colormap
    start = time.clock()

    f.write('Loading input file ... One moment ...\n')
    vsoln_colormap = np.load(FILEPATH)
    end = time.clock()
    f.write("Loading input time: " + str(end - start) + '\n')

    # Enable Cycles
    f.write('Initiating Cycles ...\n')
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    # Set to CUDA rendering
    f.write('Initiating CUDA rendering ...\n')
    bpy.context.user_preferences.system.compute_device_type = 'CUDA'
    # TODO CHANGE ME TO FREE GPUS
    bpy.context.user_preferences.system.compute_device = 'CUDA_0'
    f.write('CUDA rendering initiated! ...\n')

    # Check for proper vertex color layer
    f.write('Checking vertex color layer ...\n')
    if VC_NAME not in mesh.vertex_colors:
        f.write('Deleting old vertex color layers ...\n')
        for i in range(0, len(mesh.vertex_colors)):
            bpy.ops.mesh.vertex_color_remove()

        f.write('Creating new vertex color layer ...\n')
        # Create a new vertex color layer
        mesh.vertex_colors.new(VC_NAME)
    else:
        f.write('Vertex color layer exists!')

    # Check for proper material
    f.write('Checking material ...\n')
    if MATERIAL not in mesh.materials:

        f.write('Deleting old material slots ...\n')
        # Delete all material slots
        for i in range(len(mesh.materials)):
            bpy.ops.object.material_slot_remove()

        f.write('Deleting old materials ...\n')
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        f.write('Adding new materials ...\n')
        # Make a new material
        material = bpy.data.materials.new(name=MATERIAL)

        # Append material to the mesh
        mesh.materials.append(material)

        # Enable nodes to display vertex color layer
        material.use_nodes = True
    else:
        f.write('Material exists!\n')

    # Select the current vertex color layer
    vertex_color_layer = mesh.vertex_colors[VC_NAME]

    # Map vertex color layer vertices to the global vertices
    reducedMap = np.zeros(len(vertex_color_layer.data),dtype='int')

    # Create a mapping between the local (for vertex colors) and global vertices
    f.write("Mapping local to global vertices ...\n")
    local_vertex = 0
    for poly in mesh.polygons:
        for global_vertex in poly.vertices:
            reducedMap[local_vertex] = global_vertex
            local_vertex += 1

    f.write("Creating vertex group dict ...\n")
    # Create dictionary for each vertex: (vertex, list of vertex groups)
    vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

    # create dictionary of vertex group assignments per vertex
    vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}

    # Check for proper keying set
    f.write("Checking Keyingset ...\n")
    if KS_NAME not in scn.keying_sets:
        f.write('Deleting old keying sets ... \n')
        for i in range(0, len(scn.keying_sets)):
            bpy.ops.anim.keying_set_remove()

        f.write("Creating new keying set ...\n")
        # Create a new keying set
        bpy.ops.anim.keying_set_add()

        # Set current keying set as active
        keying_set = scn.keying_sets.active

        # Rename keying set
        keying_set.bl_label = KS_NAME

        # Retrieve the total number of local vertices in the color layer
        total_vertices = len(mesh.vertex_colors[VC_NAME].data)

        # Add each local vertex's color attribute to the keying set
        # Add the RGB values of the local vertices to be keyframed
        f.write("Filling keying set ... One moment ...\n")
        # Read in numpy array containing colormap
        start = time.clock()
        for local_vertex in range(0, total_vertices):

            # Only add surface local vertices to the keying set
            if SURFACE in vgroups[reducedMap[local_vertex]]:
                # 'vertex_colors[VC_NAME].data[local_vertex].color'
                data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, local_vertex)

                # Add data path to active keying set
                keying_set.paths.add(mesh, data_path)
                f.write("Data path added for vertex: " + str(local_vertex) + '\n')

        end = time.clock()
        f.write("Keyingset time: " + str(end - start) + '\n')
        f.write("Keyingset title: " + keying_set.bl_label +'\n')
    else:
        f.write('Keyingset exists!\n')


    # Start time
    start = time.clock()

    # Add a keyframe per iteration
    for i in range(START, KEYFRAMES):

        #Move cursor to next keyframe location before every iteration
        bpy.context.scene.frame_set(frame=FRAME_NUM)

        #Color the vertices
        f.write('Begin coloring...\n')
        local_vertex = 0
        for poly in mesh.polygons:
            for global_vertex in poly.vertices:
                # Only color vertices in the surface
                if SURFACE in vgroups[reducedMap[local_vertex]]:
                    f.write('Coloring vertex #: ' + str(local_vertex) + '\n')
                    vertex_color_layer.data[local_vertex].color = vsoln_colormap[TIME, global_vertex][0:3]
                local_vertex += 1

        f.write('Vertices colored: ' + str(local_vertex) + '\n')

        # Update increments
        FRAME_NUM += 1
        TIME += 1

    # End time
    end = time.clock()
    f.write("Coloring frame time: " + str(end - start) + '\n')
    f.write('Finished\n\n')
