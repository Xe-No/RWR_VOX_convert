# -*- mode: python -*-

block_cipher = None


a = Analysis(['RWRvox2xml.py'],
             pathex=['C:\\Users\\Xereal Hu\\Documents\\GitHub\\RWR_VOX_convert'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='RWRvox2xml',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
