
import open3d as o3d
import numpy as np

import os

def clean_info(filename):
    """
    some fbx downloaded from the internet has strange pattern, clean that
    """
    with open(filename, "r") as f:
        content = f.read().strip()
    start = content.find('mix')
    end = content.find(':')
    if start == -1 or end == -1:
        return
    pattern = content[start:end+1]
    # print(pattern)
    content = content.replace(pattern, "")
    new_filename = filename.replace(".txt","_clean.txt")
    with open(new_filename, "w") as f:
        f.write(content)
    print('clean finished')

smpl_joint_names = [
    "hips",
    "leftUpLeg",
    "rightUpLeg",
    "spine",
    "leftLeg",
    "rightLeg",
    "spine1",
    "leftFoot",
    "rightFoot",
    "spine2",
    "leftToeBase",
    "rightToeBase",
    "neck",
    "leftShoulder",
    "rightShoulder",
    "head",
    "leftArm",
    "rightArm",
    "leftForeArm",
    "rightForeArm",
    "leftHand",
    "rightHand",
    "leftHandIndex1",
    "rightHandIndex1",
]

def print_joint2(infoname):
    if not os.path.exists(infoname):
        clean_info(infoname.replace("_clean",""))


    lines = open(infoname).readlines()



    infoname = infoname.replace("_clean","")
    meshname = infoname.replace(".txt", ".obj")
    inmesh = o3d.io.read_triangle_mesh(meshname)
    v_posed = np.array(inmesh.vertices)

    hier = {}
    joint2index = {}
    index = 0
    # parse rig info file and obtain kinematic chain(hierarchical structure)
    for line in lines:
        line = line.strip('\n').strip()
        if line[:4] != 'hier':
            continue
        splits = line.split(' ')
        parent_name = splits[1]
        child_name = splits[2]
        if parent_name not in joint2index:
            joint2index[parent_name] = index
            index += 1
        if child_name not in joint2index:
            joint2index[child_name] = index
            index += 1
        if parent_name not in hier:
            hier[parent_name] = [child_name]
        else:
            hier[parent_name].append(child_name)

    index2joint = {v: k for k, v in joint2index.items()}
    hier_index = {}
    for k, v in hier.items():
        hier_index[joint2index[k]] = [joint2index[vv] for vv in v]
    parents = list(hier_index.keys())
    children = []
    for v in hier_index.values():
        children.extend(v)
    root = [item for item in parents if item not in children]
    assert len(root) == 1
    root = root[0]

    # reorganize the index mapping to ensure that along each chain,
    # from root node to leaf node, the index number increases
    new_hier = {}
    new_joint2index = {index2joint[root]: 0}
    top_level = [root]
    index = 1
    for item in top_level:
        if item not in hier_index:
            # print('continue')
            continue
        for child in hier_index[item]:
            child_name = index2joint[child]
            if child_name not in new_joint2index:
                new_joint2index[child_name] = index
                index += 1
            if new_joint2index[index2joint[item]] not in new_hier:
                new_hier[new_joint2index[index2joint[item]]] = []
            new_hier[new_joint2index[index2joint[item]]].append(new_joint2index[child_name])
            top_level.append(child)
    print('joint names and their indices in the 3d character model')
    savejoint_dir = infoname.replace(".txt","_joint.txt")
    names = [s.lower() for s in smpl_joint_names]
    count = 0
    with open(savejoint_dir,'w') as f:
        for joint,id in new_joint2index.items():
            if joint.lower() in names:
                f.write("%s : %d need to match\n" % (joint, id))
                count += 1
            else:
                f.write("%s : %d\n" % (joint, id))
        f.write("\n[%d/%d] TO MATCH"%(count,len(smpl_joint_names)))