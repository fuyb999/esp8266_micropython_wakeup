@echo on

::目录保存到参数init_path中,等号前后不要有空格
set init_path=%cd%
set build_path=%init_path%\build\
set src_path=%init_path%\src\

set COM=COM4

::创建build文件夹
mkdir %build_path%

::编译libs并移动到build中
cd ../libs
for /f "delims=.*" %%i in ('"dir /s/ON/B *.py*"') do (
python -m mpy_cross "%%i.py"
::move to build
move "%%i.mpy" %build_path%\
)

::返回主目录
cd %init_path%
::编译主目录移动到build中
for /f "delims=.*" %%i in ('"dir /s/ON/B *.py*"') do (
python -m mpy_cross "%%i.py"
::move to build
move "%%i.mpy" %build_path%
)

::删除boot和main
del "%build_path%\boot.mpy"
del "%build_path%\main.mpy"

::上传文件到单片机
for /f "delims=.*" %%i in ('"dir /s/ON/B *.mpy*"') do (
python ..\scripts\microupload.py -C %build_path% -v %COM% "%%i.mpy"
del %%i.mpy
)

cd ..
python scripts\microupload.py -C %cd%\libs -v %COM% "boot.py"
python scripts\microupload.py -C %cd%\libs -v %COM% "main.py"
