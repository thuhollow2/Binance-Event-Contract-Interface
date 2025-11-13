@echo off
echo ================================
echo Android环境设置完成后的重启指南
echo ================================
echo.
echo 请按照以下步骤操作:
echo.
echo 1. 关闭所有PowerShell窗口 (包括运行Appium的窗口)
echo 2. 重新打开PowerShell窗口
echo 3. 导航到项目目录:
echo    cd "C:\Users\BinBin\Documents\GitHub\Binance-Event-Contract-Interface"
echo.
echo 4. 验证环境变量:
echo    echo %%ANDROID_HOME%%
echo    echo %%ANDROID_SDK_ROOT%%
echo.
echo 5. 启动Appium服务器:
echo    appium
echo.
echo 6. 在新的PowerShell窗口中运行控制器:
echo    python simple_controller.py
echo.
echo 环境变量已设置为:
echo ANDROID_HOME = C:\Users\BinBin\Documents\GitHub\Binance-Event-Contract-Interface\android-tools
echo ANDROID_SDK_ROOT = C:\Users\BinBin\Documents\GitHub\Binance-Event-Contract-Interface\android-tools
echo.
pause