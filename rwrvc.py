from rwr_xml2vox_weapon import TranslateXMLtoVOX as WXV
from rwr_vox2xml_weapon import TranslateVOXtoXML as WVX
from rwr_bnd2xml_human  import TranslateBNDtoXML as HBX
from rwr_vox2xml_human  import TranslateVOXtoXML as HVX
from rwr_xml2vox_human  import TranslateXMLtoBND as HXB
from rwr_xml2vox_human  import TranslateXMLtoVOX as HXV
from rwr_type_assert	import TypeAssert 		 as TA


import sys,os

def getFileName(path_file, suffix):
	''' 获取指定目录下的所有指定后缀的文件名 '''

	f_list = os.listdir(path_file)
	ret_list = []
	# print(f_list)
	for i in f_list:
		s_size = len(suffix)
		t_size = len(i)
		if t_size > s_size:
			if i[-s_size:] == suffix:
				ret_list.append(i)

	return ret_list


def ConvertFile(path_file):
	key  = os.path.splitext(path_file)[0]
	# if os.path.splitext(path_file)[1] == '.vox' and os.path.splitext(key)[1] == '.bnd':
	# 	HBX(path_file)

	if os.path.splitext(path_file)[1] == '.xml':
		if TA(path_file) == "weapon":
			WXV(path_file)
		if TA(path_file) == "human":
			HXV(path_file)
			HXB(path_file)
		# operator = input('is it a weapon? | 是武器吗？ (y/n): ')
		# if operator == 'y':
		# 	WXV(path_file)
		# else:
		# 	HXV(path_file)
		# 	HXB(path_file)  

	if os.path.splitext(path_file)[1] == '.vox':
		if TA(path_file) == "weapon":
			WVX(path_file)
		if TA(path_file) == "human" and os.path.splitext(key)[1] != '.bnd':
			HVX(path_file)
		if TA(path_file) == "human" and os.path.splitext(key)[1] == '.bnd':
			HBX(path_file)
		# operator = input('is it a weapon? | 是武器吗？ (y/n): ')
		# if operator == 'y':
		# 	WVX(path_file)

		# else:
		# 	HVX(path_file)   


def main():
	num_argv = len(sys.argv)
	print('Author: Xe-No')
	if num_argv == 1:
		while 1:
			operator = input('''
What do you want?
1. Import all models in work folder | 导入模型 (.xml -> .vox   /   .xml -> .vox + .bnd.vox)
2. Export all models in work folder | 导出模型 (.vox -> .xml   /   .bnd.vox + .vox -> .xml)
3. Exit | 退出
Enter a number: ''')
			operator = int(operator)
			if operator == 1:
				list_file = getFileName('./', ".xml")
				print(list_file)
				for path_file in list_file:
					ConvertFile(path_file)  
			if operator == 2:
				list_file = getFileName('./', ".vox")
				print(list_file)
				for path_file in list_file:
					ConvertFile(path_file)  
					
				list_file = getFileName('./', ".bnd.vox")
				print(list_file)
				for path_file in list_file:
					ConvertFile(path_file)    
			if operator == 3:
				sys.exit()
				
					
			if operator not in [1,2,3]:
				print('invalid number')


	elif num_argv == 2:
		path_file = sys.argv[1]
		ConvertFile(path_file)             


	elif num_argv == 3:
		path_file = sys.argv[2]
		parameter = sys.argv[1] 
		if parameter == "-wxv":
			WXV(path_file)
		if parameter == "-wvx":
			WVX(path_file)
		if parameter == "-hbx":
			HBX(path_file)
		if parameter == "-hvx":
			HVX(path_file)
		if parameter == "-hxb":
			HXB(path_file)
		if parameter == "-hvb":
			HVB(path_file)



	else:
		print('Invalid argument number')
		sys.exit()

	input('Complete!')

def Test():
	ConvertFile("nazrin-maid.xml")
	ConvertFile("nazrin-maid.vox")
	ConvertFile("nazrin-maid.bnd.vox")



if __name__ == '__main__':
	main()