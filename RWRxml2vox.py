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
    return (np.dot(matrix,vec4) + [trans_bias, trans_bias, 0, 0] ).tolist()

def TranslateXMLtoVOX(path_xml):

    print("Process .xml -> .xml.vox + .xml.skl + .xml.bnd Start.")
    box_size = 99
    trans_bias = 49
    path_vox = path_xml + ".vox"
    path_skl = path_xml + ".skl"
    path_bnd = path_xml + ".bnd"

    tree = ET.parse(path_xml)
    root = tree.getroot()

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


    skeleton = root.find('skeleton')
    tree = ET.ElementTree(skeleton) 
    tree.write(path_skl)

    skeletonVoxelBindings = root.find('skeletonVoxelBindings')
    tree = ET.ElementTree(skeletonVoxelBindings) 
    tree.write(path_bnd)






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
    # print(chunk_xyzi)


    # chunk_init.tofile("test.out")
    # chunk_size.tofile("test.out")
    # chunk_xyzi.tofile("test.out")
    # chunk_rgba.tofile("test.out")


if __name__ == '__main__':
    # TranslateXMLtoVOX(sys.argv[1])
    TranslateXMLtoVOX("test.xml")
