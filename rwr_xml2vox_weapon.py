import xml.etree.ElementTree as ET
import numpy as np
import os, sys
from collections import Iterable

def ToCharacterCode(string):
    return [ord(c) for c in string ]

def ToData(int32):
    x = np.array([int32]).astype('uint32')
    x.dtype = 'uint8'
    return x


def Transformation(vec4):
    trans_bias = 49
    matrix = np.array([
            [1,0,0,0],
            [0,0,-1,0],
            [0,1,0,0],
            [0,0,0,1]
            ])
    return (np.dot(matrix,vec4) + [trans_bias, trans_bias, trans_bias, 0] ).tolist()

def TranslateXMLtoVOX(path_xml):
    box_size = 99
    trans_bias = 49
    key = path_xml[:-4]
    path_vox = key + ".vox"
    # path_skl = path_xml + ".skl"
    # path_bnd = path_xml + ".bnd"
    print("Input: " + path_xml)

    tree = ET.parse(path_xml)
    root = tree.getroot()
    if root.tag != 'model':
        print(path_xml+' is not a valid model.')
        return False

    # parse voxel data
    data_xyzi = []
    color_rule = {}
    color_index = 1
    for voxel in root.iterfind('voxels/voxel'):
        color = (
                    voxel.attrib['r'],
                    voxel.attrib['g'],
                    voxel.attrib['b'],
                    voxel.attrib['a']
                )
        if color not in color_rule.keys():
            color_rule[color] = color_index
            color_index += 1

        xyzi =  [
                    voxel.attrib['x'],
                    voxel.attrib['y'],
                    voxel.attrib['z'],
                    color_rule[color]
                ]
        data_xyzi.append(xyzi)


    # skeleton = root.find('skeleton')
    # tree = ET.ElementTree(skeleton) 
    # tree.write(path_skl)

    # skeletonVoxelBindings = root.find('skeletonVoxelBindings')
    # tree = ET.ElementTree(skeletonVoxelBindings) 
    # tree.write(path_bnd)






    data_xyzi = np.asarray(data_xyzi, dtype=int)
    data_xyzi = [ Transformation(xyzi) for xyzi in data_xyzi ]
    data_xyzi = np.asarray(data_xyzi,'uint8')

    data_rgba = np.asarray(list(color_rule.keys()), dtype=float)
    data_rgba = data_rgba * 255
    data_rgba = data_rgba.astype('uint8')
    data_rgba = np.pad(data_rgba, ((0,256-len(data_rgba)),(0,0)), 'constant')

    # print(data_rgba)
    # print(data_xyzi)

    m = len(data_xyzi)
    n = 4 * m + 4
    l = 12 * 3 +12 + n + 1024
    print("Total voxel number:"+ str(n))

    
    flat = lambda t: [x for sub in t for x in flat(sub)] if isinstance(t, Iterable) else [t]
    chunk_init = bytes(flat([
                    ToCharacterCode("VOX "), ToData(150),
                    ToCharacterCode("MAIN"), ToData(0),
                    ToData(l)
                ]))

    chunk_size = bytes(flat([
                    ToCharacterCode("SIZE"), ToData(12), ToData(0),
                    ToData(box_size), ToData(box_size), ToData(box_size)
                ]))

    chunk_xyzi = bytes(flat([
                    ToCharacterCode("XYZI"), ToData(n), ToData(0),
                    ToData(m),
                    data_xyzi
                ]))

    chunk_rgba = bytes(flat([
                    ToCharacterCode("RGBA"), ToData(256*4), ToData(0),
                    data_rgba,
                ]))

    with open(path_vox,"wb") as f:
        f.write(chunk_init)
        f.write(chunk_size)
        f.write(chunk_xyzi)
        f.write(chunk_rgba)

    print("Output: " + path_vox)
    print("")


def getFileName(path):
    ''' 获取指定目录下的所有指定后缀的文件名 '''
    f_list = os.listdir(path)
    ret_list = []
    # print f_list
    for i in f_list:
        # os.path.splitext():分离文件名与扩展名
        if os.path.splitext(i)[1] == '.xml':
            ret_list.append(i)
    return ret_list


if __name__ == '__main__':
    num_argv = len(sys.argv)
    print('Author: Xe-No')
    if num_argv == 1:
        print('Tanslate all xml files')
        list_xml = getFileName('./')
        for path_xml in list_xml:
            TranslateXMLtoVOX(path_xml)
    elif num_argv == 2:
        TranslateXMLtoVOX(sys.argv[1])
    else:
        print('Invalid argument number')
        sys.exit()

    input('Complete!')

