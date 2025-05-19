@echo off
chcp 65001 > nul
title 网易云音乐VIP歌曲提取工具
color 0A
cd /d "%~dp0"
echo 正在启动网易云音乐VIP歌曲提取工具...
echo.

:: 检查extract_vip_fixed.py是否存在
if not exist extract_vip.py (
    echo 错误：未找到extract_vip.py文件�?    echo 请确保此批处理文件与extract_vip.py在同一目录�?    pause
    exit /b
)

:: 检查是否有虚拟环境
if exist "venv\Scripts\python.exe" (
    echo 找到虚拟环境，使用虚拟环境中的Python...
    "venv\Scripts\python.exe" extract_vip.py
    goto check_result
)

:: 尝试使用py启动�?优先)
echo 尝试使用py启动�?..
py -3 extract_vip.py 2>nul
if %errorlevel% equ 0 goto end

:: 尝试使用python命令
echo 尝试使用python命令...
python extract_vip.py 2>nul
if %errorlevel% equ 0 goto end

:: 尝试使用python3命令
echo 尝试使用python3命令...
python3 extract_vip.py 2>nul
if %errorlevel% equ 0 goto end

:: 尝试从常见安装位置查找Python
echo 尝试在常见安装位置查找Python...
for %%p in (
    C:\Python39\python.exe
    C:\Python38\python.exe
    C:\Python37\python.exe
    C:\Python36\python.exe
    C:\Python310\python.exe
    C:\Python311\python.exe
    C:\Python312\python.exe
    C:\Program Files\Python39\python.exe
    C:\Program Files\Python38\python.exe
    C:\Program Files\Python37\python.exe
    C:\Program Files\Python36\python.exe
    C:\Program Files\Python310\python.exe
    C:\Program Files\Python311\python.exe
    C:\Program Files\Python312\python.exe
    %LOCALAPPDATA%\Programs\Python\Python39\python.exe
    %LOCALAPPDATA%\Programs\Python\Python38\python.exe
    %LOCALAPPDATA%\Programs\Python\Python37\python.exe
    %LOCALAPPDATA%\Programs\Python\Python36\python.exe
    %LOCALAPPDATA%\Programs\Python\Python310\python.exe
    %LOCALAPPDATA%\Programs\Python\Python311\python.exe
    %LOCALAPPDATA%\Programs\Python\Python312\python.exe
) do (
    if exist "%%p" (
        echo 找到Python: %%p
        "%%p" extract_vip.py
        goto check_result
    )
)

:: 如果都失败，提示安装Python
echo.
echo 无法启动Python！请确保已安装Python 3.6或更高版本�?echo 您可以从 https://www.python.org/downloads/ 下载Python�?echo 安装时请勾�?Add Python to PATH"选项�?echo.
echo 如果您已经安装了Python，请尝试使用"直接启动.bat"文件�?pause
exit /b

:check_result
:: 如果脚本异常退出，等待用户按键
if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出，请查看上方错误信息�?    pause
)

:end
exit 
