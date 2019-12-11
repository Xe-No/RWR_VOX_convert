import xml.etree.ElementTree as ET
# import lxml as ET
import numpy as np
import os, sys
from collections import Iterable

def prettyXml(element, indent, newline, level = 0): # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行    
    if element:  # 判断element是否有子元素    
        if element.text == None or element.text.isspace(): # 如果element的text没有内容    
            element.text = newline + indent * (level + 1)      
        else:    
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)    
    #else:  # 此处两行如果把注释去掉，Element的text也会另起一行    
        #element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level    
    temp = list(element) # 将elemnt转成list    
    for subelement in temp:    
        if temp.index(subelement) < (len(temp) - 1): # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致    
            subelement.tail = newline + indent * (level + 1)    
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个    
            subelement.tail = newline + indent * level    
        prettyXml(subelement, indent, newline, level = level + 1) # 对子元素进行递归操作    




def FromCharacterCode(arr):
    lst = [chr(n) for n in arr ]
    st = "".join(lst)
    return st

def FromData(int8x4):
    x = np.array(int8x4).astype('uint8')
    x.dtype = 'uint32'
    return x[0]

def TransformationReverse(vec4):
    trans_bias = 49
    matrix = np.matrix([
        [1,0,0,0],
        [0,0,1,0],
        [0,-1,0,0],
        [0,0,0,1]
        ])
    vec4 = vec4 - [trans_bias, trans_bias, 0, 0]
    return np.dot(matrix,vec4).tolist()[0]

def GetChunkIndex(b_array, addr):
    fsize = len(b_array)
    if addr >= fsize:
        return False

    char = FromCharacterCode(b_array[addr   :addr+4])
    size_content =  FromData(b_array[addr+4 :addr+8])
    size_subcont =  FromData(b_array[addr+8 :addr+12])
    addr_start   =  addr + 12
    addr_end     =  addr + 12 + size_content
    # print(addr_end)
    return [char, addr_start, addr_end]

def VOXToChunks(b_array):
    addr = 8
    targets = []
    heads = []
    while 1:
        target = GetChunkIndex(b_array, addr)
        # print(target)
        if not target:
            break
        addr = target[2]
        heads.append(target[0])
        targets.append(target)

    # print(targets)
    xyzi = targets[heads.index('XYZI')]
    rgba = targets[heads.index('RGBA')]

    chunk_xyzi = b_array[xyzi[1]:xyzi[2]]
    chunk_rgba = b_array[rgba[1]:rgba[2]]

    num_block = FromData(chunk_xyzi[0:4])


    chunk_xyzi = chunk_xyzi[4:].reshape((num_block,4))
    index = np.lexsort([chunk_xyzi[:,2], chunk_xyzi[:,1], chunk_xyzi[:,0]])
    chunk_xyzi = chunk_xyzi[index, :]
 



    chunk_xyzi = [ TransformationReverse(xyzi) for xyzi in chunk_xyzi ]

    num_color = FromData(b_array[rgba[1]-8:rgba[1]-4]) /4 
    num_color = int(num_color) 

    chunk_rgba = chunk_rgba.reshape((num_color,4)).astype('float') / 255
    chunk_rgba = chunk_rgba.round(4) 
    # print(chunk_rgba)

    return [chunk_xyzi, chunk_rgba]

def XYZItoVoxel(xyzi):
    global colors
    x, y, z, i = xyzi
    r, g, b, a = chunk_rgba[i-1]

    # print(chunk_rgba[0])
    x, y, z ,i, r, g, b, a = [ str(m) for m in [x, y, z, i, r, g, b, a] ]

    voxel = ET.fromstring('<voxel x="'+ x +'" y="'+ y +'" z="'+ z +'" r="'+ r +'" g="'+ g +'" b="'+ b +'" a="'+ a +'" />')
    # print(voxel)
    # print(a + " "+ i)
    return voxel

def ChunkToVoxels(chunk_xyzi_rgba):
    chunk_xyzi, chunk_rgba = chunk_xyzi_rgba

    voxels = ET.Element('voxels')
    for xyzi in chunk_xyzi:
        x, y, z, i = xyzi
        r, g, b, a = chunk_rgba[i-1]
        x, y, z ,i, r, g, b, a = [ str(m) for m in [x, y, z, i, r, g, b, a] ]
        voxel = ET.fromstring('<voxel x="'+ x +'" y="'+ y +'" z="'+ z +'" r="'+ r +'" g="'+ g +'" b="'+ b +'" a="'+ a +'" />')
        voxels.append(voxel)
    return voxels

def GetSkeleton(path_skl):
    if os.path.exists(path_skl):
        skeleton_tree = ET.parse(path_skl)
        skeleton = skeleton_tree.getroot()
    else: 
        skeleton = ET.fromstring("""<skeleton>
<particle bodyAreaHint="2" id="50" invMass="15.000000" name="head" x="0.500000" y="55.500000" z="0.500000" />
<particle bodyAreaHint="2" id="45" invMass="10.000000" name="neck" x="0.500000" y="48.500000" z="0.500000" />
<particle bodyAreaHint="2" id="15" invMass="8.000000" name="rightshoulder" x="-6.500000" y="45.500000" z="0.500000" />
<particle bodyAreaHint="2" id="25" invMass="8.000000" name="leftshoulder" x="7.500000" y="45.500000" z="0.500000" />
<particle bodyAreaHint="2" id="12274576" invMass="70.000000" name="rightelbow" x="-14.500000" y="45.500000" z="0.500000" />
<particle bodyAreaHint="2" id="12273840" invMass="70.000000" name="leftelbow" x="15.500000" y="45.500000" z="0.500000" />
<particle bodyAreaHint="2" id="12274112" invMass="200.000000" name="righthand" x="-21.500000" y="44.500000" z="0.500000" />
<particle bodyAreaHint="2" id="12273488" invMass="200.000000" name="lefthand" x="22.500000" y="44.500000" z="0.500000" />
<particle bodyAreaHint="1" id="1" invMass="10.000000" name="midspine" x="0.500000" y="35.500000" z="0.500000" />
<particle bodyAreaHint="1" id="10" invMass="10.000000" name="righthip" x="-4.500000" y="28.500000" z="0.500000" />
<particle bodyAreaHint="1" id="20" invMass="10.000000" name="lefthip" x="5.500000" y="28.500000" z="0.500000" />
<particle bodyAreaHint="1" id="12285328" invMass="15.000000" name="rightknee" x="-4.500000" y="13.500000" z="0.500000" />
<particle bodyAreaHint="1" id="21" invMass="15.000000" name="leftknee" x="5.500000" y="13.500000" z="0.500000" />
<particle bodyAreaHint="1" id="12285680" invMass="20.000000" name="rightfoot" x="-4.500000" y="0.500000" z="0.500000" />
<particle bodyAreaHint="1" id="22" invMass="20.000000" name="leftfoot" x="5.500000" y="0.500000" z="0.500000" />
<stick a="12285680" b="12285328" />
<stick a="12285328" b="10" />
<stick a="10" b="20" />
<stick a="20" b="21" />
<stick a="21" b="22" />
<stick a="10" b="1" />
<stick a="1" b="15" />
<stick a="15" b="25" />
<stick a="20" b="1" />
<stick a="1" b="25" />
<stick a="25" b="12273840" />
<stick a="12273840" b="12273488" />
<stick a="15" b="12274576" />
<stick a="12274576" b="12274112" />
<stick a="15" b="45" />
<stick a="45" b="25" />
<stick a="45" b="50" />
</skeleton>""")
    return skeleton

def GetSticks(path_skl):
    skeleton = GetSkeleton("human.skl")
   
    particles = {}
    sticks = []

    for voxel in skl_root.iterfind('particle'):
        particles[voxel.attrib['id']] = [
                    float(voxel.attrib['x']),
                    float(voxel.attrib['y']),
                    float(voxel.attrib['z'])
        ]      

    for voxel in skl_root.iterfind('stick'):
        stick = [particles[voxel.attrib['a']],particles[voxel.attrib['b']]]
        sticks.append(stick)


    return sticks

def XYZItoBinding(chunk_xyzi, sticks):
    def FindCloseSkl(point, sticks):
        def GetDistance(p1, l1, l2):
        # p1为点坐标，l1为线段一端坐标，l2为线段另一端坐标
            p1 = np.array(p1)
            l1 = np.array(l1)
            l2 = np.array(l2)
            va = p1-l1
            vb = p1-l2
            vc = l1-l2
            a = np.linalg.norm(va)
            b = np.linalg.norm(vb)
            c = np.linalg.norm(vc)
        
            if b**2 > a**2 + c**2 : # b的对边为钝角，a最短
                return a
            if a**2 > b**2 + c**2 : # a的对边为钝角，b最短
                return b
            # 锐角三角形
            theta = np.arccos(np.dot(va,vc)/(a*c))
            return np.sin(theta) * a
            
        diss = []
        for skl in sticks:
            diss.append(GetDistance(point,skl[0],skl[1]))
        # print(sticks)
        return diss.index(min(diss))


    groups = []
    for x in range(0,17):
        groups.append(ET.fromstring('<group constraintIndex="'+ str(x) +'" />'))

    index = 0 
    for xyzi in chunk_xyzi:
        x, y, z, i = xyzi
        group_index = FindCloseSkl([x,y,z],sticks)
        # print(group_index)
        voxel = ET.fromstring('<voxel index="'+ str(index) +'" />')
        groups[group_index].append(voxel)
        index = index + 1

    return groups

def ChunkTOBindings(chunk_xyzi_rgba):
    chunk_xyzi, chunk_rgba = chunk_xyzi_rgba
    skeletonVoxelBindings = ET.Element('skeletonVoxelBindings')

    groups = []
    for x in range(0,17):
        groups.append(ET.fromstring('<group constraintIndex="'+ str(x) +'" />'))

    index = 0 
    for xyzi in chunk_xyzi:
        x, y, z, i = xyzi
        group_index = i - 1
        # print(group_index)
        voxel = ET.fromstring('<voxel index="'+ str(index) +'" />')
        groups[group_index].append(voxel)
        index = index + 1

    for group in groups:
        skeletonVoxelBindings.append(group)

    return skeletonVoxelBindings


def TranslateBNDtoXML(path_bnd):
    key = path_bnd[:-4]
    if key[-4:] == ".bnd":
        key = key[:-4]
    else:
        print(path_bnd + " is not a binding file")
        return -1

    path_xml = key + ".xml"
    path_vox = key + ".vox"
    path_skl = 'human.skl'
    
    print("Input:", path_bnd)
    
    b_array = np.fromfile(path_vox,dtype='uint8')
    chunk_xyzi_rgba = VOXToChunks(b_array)
    voxels = ChunkToVoxels(chunk_xyzi_rgba)   

    b_array = np.fromfile(path_bnd,dtype='uint8')
    chunk_xyzi_rgba = VOXToChunks(b_array)
    skeletonVoxelBindings = ChunkTOBindings(chunk_xyzi_rgba)
    
    skeleton = GetSkeleton("human.skl")
    
    model = ET.Element('model')
    model.append(voxels)
    model.append(skeleton)
    model.append(skeletonVoxelBindings)
    
    tree = ET.ElementTree(model)
    prettyXml(tree.getroot(), '\t', '\n')
    
    tree.write(path_xml)
    print("Output:", path_xml)


if __name__ == '__main__':
    path_bnd = "95_VER2.bnd.vox"
    TranslateBNDtoXML(path_bnd)



