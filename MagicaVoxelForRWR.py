import RWRvox2xml as vx
import RWRxml2vox as xv
import os
path = sys.argv[1]
# path = "test.xml"

print("version 0.2")

xv.TranslateXMLtoVOX(path)

line = "MagicaVoxel.exe" + " \"" + path + ".vox\""
print(line)
os.system(line)

vx.TranslateVOXtoXML(path + ".vox")

os.remove(path + ".vox")
os.remove(path + ".skl")
os.remove(path + ".bnd")


input("Press enter to exit.")