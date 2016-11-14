@echo off
SET OSGEO4W_ROOT=C:\OSGeo4W64
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
call "%OSGEO4W_ROOT%"\apps\grass\grass-7.0.4\etc\env.bat
@echo off
path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\bin
path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass-7.0.4\lib

set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python;
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python;
set PYTHONPATH=%PYTHONPATH%;C:\OSGeo4W64\apps\qgis\python\plugins
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr

start "PyCharm with access to QGIS libraries" /B "C:\Program Files (x86)\JetBrains\PyCharm Community Edition 5.0.1\bin\pycharm.exe" %*