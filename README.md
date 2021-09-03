# RWR VOX convertor

## Download 
github: https://github.com/Xe-No/RWR_VOX_convert/releases

dropbox: https://www.dropbox.com/s/ozrqv7ef84lwwr3/rwrvc.exe?dl=0

## Feature
支持了任意小于等于256尺寸的vox到xml转化，原点仍然为底面中心（人物），体心（物体），可兼容旧版99尺寸vox模型。

智能模式：人物和物体的自动转化判定为高度，大于42格为人物，否则为物体。

## Usage
Drag *.xml or *.vox to rwrvc.exe to convert to each other.

Drag edited *.bnd.vox to rwrvc.exe to assign skeleton bindings.

用法：共分为三种用法，双击，拖动以及命令行
一、双击后直接出现界面，按提示进行数字选择，以智能模式转换文件夹中多数文件
二、拖动文件到rwrvc.exe，以智能模式转换单个文件
三、使用命令行以强制模式进行转换（内附两个.bat文件作为例子，拖动文件到.bat文件以进行转换）：
物体模式：
xml转vox
rwrvc.exe -wxv file.xml   
vox转xml
rwrvc.exe -wvx file.vox
人物模式：
bnd.vox绑定
rwrvc.exe -hbx file.bnd.vox
xml转vox
rwrvc.exe -hvx file.vox
xml转bnd.vox
rwrvc.exe -hxb file.xml
vox转bnd.vox
rwrvc.exe -hvb file.vox

骨骼：
在同一目录下加入human.skl，可以改变骨骼，默认为原版士兵骨骼。