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

def TransformationReverse(vec4, sizes):
    x, y, z = [ int( (sizes[0]-1) /2  )  for num in sizes  ]
    vec4 = vec4 - [x, y, 0, 0]
    matrix = np.matrix([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1]
            ])
    return np.dot(matrix,vec4).tolist()[0]


def GetSkeleton(path_skl):
    if os.path.exists(path_skl):
        skeleton = ET.parse(path_skl)
        print(path_skl)
    else: 
        skeleton_ele = ET.fromstring("""<skeleton>
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
        skeleton = ET.ElementTree(skeleton_ele)
    return skeleton

def TranslateVOXtoXML(path_vox):
    def GetChunkIndex(b_array, addr):
        fsize = os.path.getsize(path_vox)
        if addr >= fsize:
            return False

        char = FromCharacterCode(b_array[addr   :addr+4])
        size_content =  FromData(b_array[addr+4 :addr+8])
        size_subcont =  FromData(b_array[addr+8 :addr+12])
        addr_start   =  addr + 12
        addr_end     =  addr + 12 + size_content
        # print(addr_end)
        return [char, addr_start, addr_end]

    def GetSticks(path_skl):
        skeleton = GetSkeleton(path_skl)
        print(skeleton)


        particles = {}
        sticks = []

        for voxel in skeleton.iterfind('particle'):
            particles[voxel.attrib['id']] = [
                        float(voxel.attrib['x']),
                        float(voxel.attrib['y']),
                        float(voxel.attrib['z'])
            ]      

        for voxel in skeleton.iterfind('stick'):
            stick = [particles[voxel.attrib['a']],particles[voxel.attrib['b']]]
            sticks.append(stick)


        return sticks

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



    key = path_vox[:-4]
    path_xml = key + ".xml"
    path_skl = 'human.skl'

    sticks = GetSticks(path_skl)

    print("Input:", path_vox)

    b_array = np.fromfile(path_vox,dtype='uint8')

    # addr = 8
    # main = GetChunkIndex(b_array, addr)
    # addr = main[2]

    # temp = GetChunkIndex(b_array, addr)
    # if temp[0] == "PACK":
    #     # unfinished for this case
    #     pack = temp
    #     addr += 16

    # size = GetChunkIndex(b_array, addr)
    # addr = size[2]

    # xyzi = GetChunkIndex(b_array, addr)
    # addr = xyzi[2]

    # nTRN = GetChunkIndex(b_array, addr)
    # addr = nTRN[2]

    # nGRP = GetChunkIndex(b_array, addr)
    # addr = nGRP[2]

    # nSHP = GetChunkIndex(b_array, addr)
    # addr = nSHP[2]

    # parse binary array to xml tree structure
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
    # print(targets)
    size = targets[heads.index('SIZE')]
    xyzi = targets[heads.index('XYZI')]
    rgba = targets[heads.index('RGBA')]

    chunk_size = b_array[size[1]:size[2]]
    chunk_xyzi = b_array[xyzi[1]:xyzi[2]]
    chunk_rgba = b_array[rgba[1]:rgba[2]]

    sizes = [ FromData( temp ) for temp in chunk_size.reshape((3,4)) ]
    print(sizes)

    num_block = FromData(chunk_xyzi[0:4])
    chunk_xyzi = chunk_xyzi[4:].reshape((num_block,4))
    chunk_xyzi = [ TransformationReverse(xyzi, sizes) for xyzi in chunk_xyzi ]
    print("Total voxel number:"+ str(num_block))
    # print(chunk_xyzi)

    # num_colors = 6
    # print(chunk_rgba)
    # print(rgba)
    # dirty
    num_color = FromData(b_array[rgba[1]-8:rgba[1]-4]) /4 
    num_color = int(num_color) 

    # print(chunk_rgba)
    chunk_rgba = chunk_rgba.reshape((num_color,4)).astype('float') / 255
    chunk_rgba = chunk_rgba.round(4) 
    # print(chunk_rgba)

    method = 1
    # xml generate
    if method == 1:
        model = ET.Element('model')
        voxels = ET.SubElement(model, 'voxels')
        skeletonVoxelBindings = ET.SubElement(model, 'skeletonVoxelBindings')
        skeleton = GetSkeleton(path_skl)
        # print(skeleton.getroot())
        model.append(skeleton.getroot())

    
    
        for xyzi in chunk_xyzi:
            voxels.append(XYZItoVoxel(xyzi))

        groups = XYZItoBinding(chunk_xyzi, sticks)
        for group in groups:
            skeletonVoxelBindings.append(group)
    
        tree = ET.ElementTree(model)
    
        prettyXml(tree.getroot(), '\t', '\n')

        tree.write(path_xml)

    if method == 2:
        model = ET.Element('model')
        voxels = ET.SubElement(model, 'voxels')
        skeleton = ET.SubElement(model, 'skeleton')
        skeletonVoxelBindings = ET.SubElement(model, 'skeletonVoxelBindings')

        for xyzi in chunk_xyzi:
            voxels.append(XYZItoVoxel(xyzi))


        tree = ET.ElementTree(model)
        prettyXml(tree.getroot(), '\t', '\n')
        tree.write(path_xml)
        # root = tree.getroot()

    
    print("Output:", path_xml)

def getFileName(path):
    ''' 获取指定目录下的所有指定后缀的文件名 '''

    f_list = os.listdir(path)
    ret_list = []
    # print f_list
    for i in f_list:
        # os.path.splitext():分离文件名与扩展名
        if os.path.splitext(i)[1] == '.vox':
            ret_list.append(i)

    return ret_list


if __name__ == '__main__':
    num_argv = len(sys.argv)
    print('Author: Xe-No')
    if num_argv == 1:
        print('Tanslate all vox files')
        list_vox = getFileName('./')
        for path_vox in list_vox:
            TranslateVOXtoXML(path_vox)  
    elif num_argv == 2:
        TranslateVOXtoXML(sys.argv[1])
    else:
        print('Invalid argument number')
        sys.exit()

    input('Complete!')
    # input()

