@echo off
setlocal

echo =====================================================
echo  YouTube Downloader CN - One Click Build
 echo =====================================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo [1/3] Upgrading pip...
python -m pip install --upgrade pip

echo [2/3] Installing dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo [3/3] Building EXE...
pyinstaller --onefile --windowed --name=YouTubeDownloaderCN --hidden-import=yt_dlp youtube_gui_downloader_cn.py

if errorlevel 1 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo Build success.
echo Output: dist\YouTubeDownloaderCN.exe
pause
