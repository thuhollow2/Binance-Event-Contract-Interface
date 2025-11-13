@echo off
echo 正在设置Android SDK环境变量...
echo.

REM 获取当前目录
set CURRENT_DIR=%CD%
set ANDROID_TOOLS_PATH=%CURRENT_DIR%\android-tools\platform-tools

echo 当前目录: %CURRENT_DIR%
echo Android工具路径: %ANDROID_TOOLS_PATH%

REM 设置环境变量
echo 设置ANDROID_HOME环境变量...
setx ANDROID_HOME "%CURRENT_DIR%\android-tools" /M 2>nul
if errorlevel 1 (
    echo 管理员权限设置失败，使用用户权限设置...
    setx ANDROID_HOME "%CURRENT_DIR%\android-tools"
)

echo 设置ANDROID_SDK_ROOT环境变量...
setx ANDROID_SDK_ROOT "%CURRENT_DIR%\android-tools" /M 2>nul
if errorlevel 1 (
    echo 管理员权限设置失败，使用用户权限设置...
    setx ANDROID_SDK_ROOT "%CURRENT_DIR%\android-tools"
)

echo 添加ADB到PATH...
setx PATH "%PATH%;%ANDROID_TOOLS_PATH%" /M 2>nul
if errorlevel 1 (
    echo 管理员权限设置失败，使用用户权限设置...
    setx PATH "%PATH%;%ANDROID_TOOLS_PATH%"
)

echo.
echo 环境变量设置完成！
echo ANDROID_HOME = %CURRENT_DIR%\android-tools
echo ANDROID_SDK_ROOT = %CURRENT_DIR%\android-tools
echo PATH 已添加: %ANDROID_TOOLS_PATH%
echo.
echo 重要：请关闭所有PowerShell窗口，然后重新打开新的PowerShell窗口
echo 这样环境变量才能生效。
echo.
pause