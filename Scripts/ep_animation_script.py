import bpy
import numpy as np
import time

# Arbitrary names
VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
KS_NAME = 'MyNewKeyingSet'                          # Keying Set
SURFACE = 'surface'
MATERIAL = 'MyMaterial'

# Time constants
FRAME_NUM = 1                                      # Time between frames
TIME = 0                                           # Times in colormap
START = 0
KEYFRAMES = 1501

# TODO Find the right place to run the job
with open('/data/tthao/blender/EP/logs/log15001.txt', 'w') as f:

    # Blender constants
    scn = bpy.context.scene                             # Active scene
    obj = bpy.data.objects['BiV2_67584_RVmL']           # Active object
    mesh = obj.data                                     # Active object's mesh

    # Select heart object
    obj.select = True
    bpy.context.scene.objects.active = obj

    # Filepath
    # TODO Change me for different colormaps!
    FILEPATH = '/data/tthao/blender/EP/3000ms.npy'

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
    COMPUTE_DEVICE_TYPE = bpy.context.user_preferences.system.compute_device_type
    f.write(COMPUTE_DEVICE_TYPE)
    # TODO CHANGE ME TO FREE GPUS
    bpy.context.user_preferences.system.compute_device = 'CUDA_0'
    COMPUTE_DEVICE = bpy.context.user_preferences.system.compute_device
    f.write(COMPUTE_DEVICE)
    f.write('CUDA rendering initiated! ...\n')

    # Check for proper vertex color layer
    # f.write('Checking vertex color layer ...\n')
    # if VC_NAME not in mesh.vertex_colors:
    #     f.write('Deleting old vertex color layers ...\n')
    #     for i in range(0, len(mesh.vertex_colors)):
    #         bpy.ops.mesh.vertex_color_remove()
    #
    #     f.write('Creating new vertex color layer ...\n')
    #     # Create a new vertex color layer
    #     mesh.vertex_colors.new(VC_NAME)
    # else:
    #     f.write('Vertex color layer exists!')

    # Check for proper material
    f.write('Checking material ...\n')
    if MATERIAL not in mesh.materials:

        f.write('Adding new materials ...\n')
        # Make a new material
        material = bpy.data.materials.new(name=MATERIAL)

        # Append material to the mesh
        mesh.materials.append(material)

        # Enable nodes to display vertex color layer
        material.use_nodes = True

        mat = bpy.data.materials['MyMaterial']
        nodes = mat.node_tree.nodes

        for node in nodes:
            nodes.remove(node)

        # Add necessary nodes
        # Create Output node
        # f.write("Adding output node...\n")
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        node_output.location = 0, 0

        # Create mixer node
        # f.write("Adding mixer node...\n")
        node_mixer = nodes.new(type="ShaderNodeMixShader")
        nodes["Mix Shader"].inputs[0].default_value = 0.15
        node_mixer.location = -200, 0

        # Create Mix bsdf diffuse node
        # f.write("Adding diffuse node...\n")
        node_diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
        node_diffuse.location = -400, 0

        # Create attribute node
        # f.write("Adding attribute node...\n")
        node_attr = nodes.new(type="ShaderNodeAttribute")
        node_attr.location = -600, 0
        nodes["Attribute"].attribute_name = VC_NAME


        # Create antisotropic node
        # f.write("Adding antro node...\n")
        node_antro = nodes.new(type="ShaderNodeBsdfAnisotropic")
        nodes["Anisotropic BSDF"].inputs[1].default_value = 1
        nodes["Anisotropic BSDF"].distribution = 'ASHIKHMIN_SHIRLEY'
        node_antro.location = -400, -200

        # Link nodes together
        links = mat.node_tree.links
        link_attr_diffuse = links.new(node_attr.outputs[0], node_diffuse.inputs[0])
        link_diffuse_mixer = links.new(node_diffuse.outputs[0], node_mixer.inputs[1])
        link_antro_mixer = links.new(node_antro.outputs[0], node_mixer.inputs[2])
        link_mixer_output = links.new(node_mixer.outputs[0], node_output.inputs[0])

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

    # # Check for proper keying set
    # f.write("Checking Keyingset ...\n")
    # if KS_NAME not in scn.keying_sets:
    #     f.write('Deleting old keying sets ... \n')
    #     for i in range(0, len(scn.keying_sets)):
    #         bpy.ops.anim.keying_set_remove()
    #
    #     f.write("Creating new keying set ...\n")
    #     # Create a new keying set
    #     bpy.ops.anim.keying_set_add()
    #
    #     # Set current keying set as active
    #     keying_set = scn.keying_sets.active
    #
    #     # Rename keying set
    #     keying_set.bl_label = KS_NAME
    #
    #     # Retrieve the total number of local vertices in the color layer
    #     total_vertices = len(mesh.vertex_colors[VC_NAME].data)
    #
    #     # Add each local vertex's color attribute to the keying set
    #     # Add the RGB values of the local vertices to be keyframed
    #     f.write("Filling keying set ... One moment ...\n")
    #     # Read in numpy array containing colormap
    #     start = time.clock()
    #     for local_vertex in range(0, total_vertices):
    #
    #         # Only add surface local vertices to the keying set
    #         if SURFACE in vgroups[reducedMap[local_vertex]]:
    #             # 'vertex_colors[VC_NAME].data[local_vertex].color'
    #             data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, local_vertex)
    #
    #             # Add data path to active keying set
    #             keying_set.paths.add(mesh, data_path)
    #             f.write("Data path added for vertex: " + str(local_vertex) + '\n')
    #
    #     end = time.clock()
    #     f.write("Keyingset time: " + str(end - start) + '\n')
    #     f.write("Keyingset title: " + keying_set.bl_label +'\n')
    # else:
    #     f.write('Keyingset exists!\n')


    # Start time
    start = time.clock()

    # bpy.context.scene.render.filepath = "/data/tthao/blender/EP/imagestrips/"
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
                    # f.write('Coloring vertex #: ' + str(local_vertex) + '\n')
                    vertex_color_layer.data[local_vertex].color = vsoln_colormap[TIME, global_vertex][0:3]
                local_vertex += 1

        # f.write('Vertices colored: ' + str(local_vertex) + '\n')

        # f.write('Rendering...' + '\n')
        bpy.data.scenes["Scene"].render.filepath = '/data/tthao/blender/EP/imagestrips/3000ms/frame_%d.jpg' % TIME
        bpy.ops.render.render( write_still=True )

        # Update increments
        FRAME_NUM += 1
        TIME += 1

    # End time
    end = time.clock()
    f.write("Coloring frame time: " + str(end - start) + '\n')
    f.write('Finished\n\n')
