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
    vec4 = vec4 - [x, y, z, 0]
    matrix = np.matrix([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1]
            ])
    return np.dot(matrix,vec4).tolist()[0]




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

    key = path_vox[:-4]
    path_xml = key + ".xml"
    path_bnd = key + ".bnd"
    path_skl = key + ".skl"

    print("Input: " + path_vox)

    b_array = np.fromfile(path_vox,dtype='uint8')

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

    method = 2
    # xml generate
    if method == 1:
        model = ET.Element('model')
        voxels = ET.SubElement(model, 'voxels')
        
        skeleton = ET.parse(path_skl)
        skeletonVoxelBindings = ET.parse(path_bnd)
    
        model.append(skeleton.getroot())
        model.append(skeletonVoxelBindings.getroot())
    
    
        for xyzi in chunk_xyzi:
            voxels.append(XYZItoVoxel(xyzi))
    
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

    print("Output: " + path_xml)
    print("")

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
    chunk_xyzi = [ TransformationReverse(xyzi) for xyzi in chunk_xyzi ]
    # print("Total voxel number:"+ str(num_block))
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

    return [chunk_xyzi, chunk_rgba]


def ChunkToVoxels(chunk_xyzi):
    voxels = ET.Element(model, 'voxels')
    for xyzi in chunk_xyzi:
        voxels.append(XYZItoVoxel(xyzi))
    return voxels




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