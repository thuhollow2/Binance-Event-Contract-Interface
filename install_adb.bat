@echo off
echo 正在下载Android SDK Platform Tools...
echo.

REM 创建android-tools目录
if not exist "android-tools" mkdir android-tools
cd android-tools

REM 下载platform-tools
echo 下载中，请稍候...
powershell -Command "Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile 'platform-tools.zip'"

if exist platform-tools.zip (
    echo 下载完成，正在解压...
    powershell -Command "Expand-Archive -Path 'platform-tools.zip' -DestinationPath '.' -Force"
    
    if exist platform-tools (
        echo 解压完成！
        echo.
        echo ADB工具已安装到: %CD%\platform-tools
        echo.
        echo 正在测试ADB连接...
        platform-tools\adb.exe version
        echo.
        echo 检查连接的设备:
        platform-tools\adb.exe devices
        echo.
        echo 安装完成！你现在可以使用以下命令:
        echo %CD%\platform-tools\adb.exe devices
        echo.
        pause
    ) else (
        echo 解压失败！
    )
    
    del platform-tools.zip
) else (
    echo 下载失败！请检查网络连接
    pause
)

cd ..