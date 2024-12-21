@echo off
setlocal enabledelayedexpansion

rem ==============================================================================
rem -- Set up environment --------------------------------------------------------
rem ==============================================================================

set REPLACE_LATEST=true
set AWS_COPY=aws s3 cp
#定义用于执行AWS S3复制操作的命令字符串
rem ==============================================================================
rem -- Parse arguments -----------------------------------------------------------
rem ==============================================================================

set DOC_STRING=Upload latest build to S3
#定义文档字符串，用于描述脚本的主要功能，即上传最新构建到S3
set USAGE_STRING="Usage: $0 [-h|--help] [--replace-latest] [--dry-run]"
#定义使用说明字符串，展示脚本的正确使用方式
:arg-parse
if not "%1"=="" (
    if "%1"=="--replace-latest" (
        set REPLACE_LATEST=true
    )

    if "%1"=="--dry-run" (
      set AWS_COPY=rem aws s3 cp
    )

    if "%1"=="--help" (
        echo %DOC_STRING%
        echo %USAGE_STRING%
        GOTO :eof
    )

    shift
    goto :arg-parse
)

rem Get repository version
for /f %%i in ('git describe --tags --dirty --always') do set REPOSITORY_TAG=%%i
if not defined REPOSITORY_TAG goto error_carla_version
echo REPOSITORY_TAG = !REPOSITORY_TAG!
#如果版本号变量未定义，跳转到error_carla_version标签处处理错误情况
rem Last package data
set CARLA_DIST_FOLDER=%~dp0\Build\UE4Carla
rem 设置CARLA分发文件夹的路径，%~dp0是批处理文件所在的目录

set PACKAGE=CARLA_%REPOSITORY_TAG%.zip
rem 设置CARLA包的名称，包含仓库标签

set PACKAGE_PATH=%CARLA_DIST_FOLDER%\%PACKAGE%
rem 设置CARLA包的完整路径

set PACKAGE2=AdditionalMaps_%REPOSITORY_TAG%.zip
rem 设置附加地图包的名称，同样包含仓库标签

set PACKAGE_PATH2=%CARLA_DIST_FOLDER%\%PACKAGE2%
rem 设置附加地图包的完整路径

set S3_PREFIX=s3://carla-releases/Windows
rem 设置S3存储桶的前缀，用于上传包

set LATEST_DEPLOY_URI=!S3_PREFIX!/Dev/CARLA_Latest.zip
set LATEST_DEPLOY_URI2=!S3_PREFIX!/Dev/AdditionalMaps_Latest.zip
rem 设置最新部署URI，但这里使用了变量延迟展开的错误语法（应使用!变量!而不是%变量%，但需要在启用延迟展开后）

rem Check for TAG version
echo %REPOSITORY_TAG% | findstr /R /C:"^[0-9]*\.[0-9]*\.[0-9]*.$" 1>nul
rem 检查仓库标签是否符合版本号格式（主版本号.次版本号.修订号）

if %errorlevel% == 0 (
  echo Detected release version with tag %REPOSITORY_TAG%
  set DEPLOY_NAME=CARLA_%REPOSITORY_TAG%.zip
  set DEPLOY_NAME2=AdditionalMaps_%REPOSITORY_TAG%.zip
) else (
  echo Detected non-release version with tag %REPOSITORY_TAG%
  set S3_PREFIX=!S3_PREFIX!/Dev
  rem 注意：这里再次设置了S3_PREFIX，但之前的设置并未在if块外部使用，可能是个错误
  git log --pretty=format:%%cd_%%h --date=format:%%Y%%m%%d -n 1 > tempo1234
  rem 获取最近的git提交信息，并保存到临时文件
  set /p DEPLOY_NAME= < tempo1234
  rem 从临时文件读取提交信息（日期和哈希），但这里缺少了.zip后缀的添加逻辑
  del tempo1234
  rem 删除临时文件
  
  rem 修正：需要手动添加.zip后缀和启用延迟变量展开
  setlocal enabledelayedexpansion
  set DEPLOY_NAME=!DEPLOY_NAME:.zip=!.zip
  endlocal & set DEPLOY_NAME=%DEPLOY_NAME%
  rem 注意：上面的行试图修正.zip后缀的添加，但方法不正确。正确的做法是在读取后立即添加。
  
  echo deploy name = !DEPLOY_NAME!
  rem 注意：这里再次使用了错误的变量展开语法（!DEPLOY_NAME!应在启用延迟展开后使用）
)

  git log --pretty=format:%%h -n 1 > tempo1234
  set /p DEPLOY_NAME2= < tempo1234
  del tempo1234
  set DEPLOY_NAME2=AdditionalMaps_!DEPLOY_NAME2!.zip
  echo deploy name2 = !DEPLOY_NAME2!
)
echo Version detected: %REPOSITORY_TAG%
echo Using package %PACKAGE% as %DEPLOY_NAME%

if not exist "%PACKAGE_PATH%" (
  echo Latest package not found, please run 'make package'
  goto :bad_exit
)

rem ==============================================================================
rem -- Upload --------------------------------------------------------------------
rem ==============================================================================

set DEPLOY_URI=!S3_PREFIX!/%DEPLOY_NAME%
%AWS_COPY% %PACKAGE_PATH% %DEPLOY_URI%
echo Latest build uploaded to %DEPLOY_URI%

set DEPLOY_URI2=!S3_PREFIX!/%DEPLOY_NAME2%
%AWS_COPY% %PACKAGE_PATH2% %DEPLOY_URI2%
echo Latest build uploaded to %DEPLOY_URI2%

rem ==============================================================================
rem -- Replace Latest ------------------------------------------------------------
rem ==============================================================================

if %REPLACE_LATEST%==true (
  %AWS_COPY% %DEPLOY_URI% %LATEST_DEPLOY_URI%
  echo Latest build updated as %LATEST_DEPLOY_URI%
  %AWS_COPY% %DEPLOY_URI2% %LATEST_DEPLOY_URI2%
  echo Latest build updated as %LATEST_DEPLOY_URI2%
)

rem ==============================================================================
rem -- ...and we are done --------------------------------------------------------
rem ==============================================================================

echo Success!

:success
    echo.
    goto good_exit
#成功结束的标签，输出空行后跳转到good_exit标签处结束脚本并返回成功码0
:error_carla_version
    echo.
    echo %FILE_N% [ERROR] Carla Version is not set
    goto bad_exit
#处理Carla版本未设置的错误情况，输出错误信息后跳转到bad_exit标签处结束脚本并返回错误码1
:good_exit
    endlocal
    exit /b 0
#正常结束脚本的标签，结束局部变量作用域并以成功码0退出脚本
:bad_exit
    endlocal
    exit /b 1
#错误结束脚本的标签，结束局部变量作用域并以错误码1退出脚本
