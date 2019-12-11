import xml.etree.ElementTree as ET
# import lxml as ET
import numpy as np
import os, sys
from collections import Iterable

def FromCharacterCode(arr):
	lst = [chr(n) for n in arr ]
	st = "".join(lst)
	return st

def FromData(int8x4):
	x = np.array(int8x4).astype('uint8')
	x.dtype = 'uint32'
	return x[0]


def AssertVOX(path_vox):
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
	
		# voxel = ET.fromstring('<voxel x="'+ x +'" y="'+ y +'" z="'+ z +'" r="'+ r +'" g="'+ g +'" b="'+ b +'" a="'+ a +'" />')
		# print(voxel)
		# print(a + " "+ i)
		return voxel

	key = path_vox[:-4]
	path_xml = key + ".xml"
	path_bnd = key + ".bnd"
	path_skl = key + ".skl"

	# print("Input: " + path_vox)

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


	
	xyzi = targets[heads.index('XYZI')]
	chunk_xyzi = b_array[xyzi[1]:xyzi[2]]
	num_block = FromData(chunk_xyzi[0:4])
	chunk_xyzi = chunk_xyzi[4:].reshape((num_block,4))
	array_z = chunk_xyzi[:,2]
	dz = max(array_z) - min(array_z)
	
	if dz > 42:
		m_type = "human"
	else:
		m_type = "weapon"

	# print("Voxel Number:[",num_block, "]  Height:[",dz, "]  Type:[",m_type,"]")

	return m_type


def AssertXML(path_xml):
	box_size = 99
	trans_bias = 49
	key = path_xml[:-4]
	path_vox = key + ".vox"
	# path_skl = path_xml + ".skl"
	# path_bnd = path_xml + ".bnd"
	# print("Input: " + path_xml)

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
	array_y = data_xyzi[:,1]
	num_block = len(array_y)
	dy = max(array_y) - min(array_y)
	if dy > 42:
		m_type = "human"
	else:
		m_type = "weapon"

	# print("Voxel Number:[",num_block, "]  Height:[",dy, "]  Type:[",m_type,"]")

	return m_type


def TypeAssert(file_name):
	suffix = file_name[-3:]
	if suffix == "vox":
		ret = AssertVOX(file_name)


	if suffix == "xml":
		ret = AssertXML(file_name)

	return ret


if __name__ == '__main__':

	AssertXML("nazrin-maid.xml")
	AssertVOX("nazrin-maid.vox")