
import open3d as o3d
import numpy as np
import pickle as pkl
import os
import shutil

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

def print_joint2(infoname,save = True):
    if not os.path.exists(infoname):
        clean_info(infoname.replace("_clean",""))


    lines = open(infoname).readlines()



    infoname = infoname.replace("_clean","")
    meshname = infoname.replace(".txt", ".obj")
    inmesh = o3d.io.read_triangle_mesh(meshname)
    # v_posed = np.array(inmesh.vertices)

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
    if save:
        savejoint_dir = infoname.replace(".txt", "_joint.txt")
        savejoint_dir = os.path.join("model", "match_list", os.path.split(savejoint_dir)[-1])
        if os.path.exists(savejoint_dir):
            print("It has been jointed!")
            return
        names = [s.lower() for s in smpl_joint_names]
        count = 0
        with open(savejoint_dir, 'w') as f:
            for joint, id in new_joint2index.items():
                if joint.lower() in names:
                    f.write("%s : %d:%d\n" % (joint, id, names.index(joint.lower())))
                    count += 1
                else:
                    f.write("%s : %d\n" % (joint, id))
            f.write("\n[%d/%d] TO MATCH" % (count, len(smpl_joint_names)))
        print("finish joint!")
        return None
    else:
        return new_joint2index

def read_match(path:str):
    #clean
    path = path.replace("_clean",'').replace('_intermediate','')
    # add joint
    path = path.replace(".txt","_joint.txt")
    match_path = os.path.join("model","match_list",os.path.split(path)[-1])
    assert os.path.exists(match_path),"match_file doesn't exist!"
    match = {}
    with open(match_path,'r') as f:
        s = f.read().split('\n')
    for line in s:
        if line == '':
            break
        line = line[line.find(':') + 1:]
        if ':' in line:
            i = line.find(':')
            match[int(line[:i])] = int(line[i + 1:])

    return match

def perfect_matching():
    path = os.path.join("model","group_0","fbx")
    for file in os.listdir(path):
        if 'txt' in file:
            s = print_joint2(os.path.join(path,file),False)
            count = 0
            for joint, id in s.items():
                if joint.lower() == 'spine':
                    count +=1
                if joint.lower() == 'spine1':
                    count +=1
                if joint.lower() == 'spine2':
                    count +=1
            if count >= 3:
                print(file)

def load_pkl(path):
    with open(path,'rb') as f:
        m = pkl.load(f)
        print(m['model2smpl'])

def save_result(good_match_list):
    if not os.path.exists("submit_results"):
        os.mkdir("submit_results")
    for good_match in good_match_list:
        if not os.path.exists(os.path.join("submit_results",good_match)):
            os.mkdir(os.path.join("submit_results",good_match))
        else:
            pass
        path_obj = os.path.join("model","group_0","fbx",good_match+".obj")
        path_fbx = os.path.join("model", "group_0", "fbx", good_match + ".fbx")
        path_txt = os.path.join("model", "group_0", "fbx", good_match + ".txt")
        path_vis = os.path.join("results",good_match,"vis.mp4")
        for file in os.listdir(os.path.join("results",good_match)):
            if 'pkl' in file:
                pkl_name = file
                break
        path_pkl = os.path.join("results", good_match, pkl_name)
        shutil.copy(path_obj,os.path.join("submit_results",good_match,good_match+".obj"))
        shutil.copy(path_fbx, os.path.join("submit_results", good_match, good_match + ".fbx"))
        shutil.copy(path_txt, os.path.join("submit_results", good_match, good_match + ".txt"))
        shutil.copy(path_vis, os.path.join("submit_results", good_match, "vis.mp4"))
        shutil.copy(path_pkl, os.path.join("submit_results", good_match,pkl_name))
