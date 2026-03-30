@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1
title Bakery Coffee System Builder

:: Set UTF-8 output mode for proper character display
for /f "tokens=2 delims=:," %%a in ('findstr /c:"OSLanguage" %windir%\System32\oobe\info\system\system.txt 2^>nul') do set OSLANG=%%a

echo ================================================
echo    BAKERY COFFEE SYSTEM BUILD TOOL
echo ================================================
echo.

:: Check for .NET SDK
echo [1/4] Checking for .NET SDK...
dotnet --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: .NET SDK not found!
    echo Please install .NET SDK 6.0 or higher from https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo .NET SDK found. Version:
dotnet --version
echo.

:: Check for C++ compiler
echo [2/4] Checking C++ compiler...
where cl > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: MSVC compiler (cl.exe) not found in PATH
    echo To compile C++ part, install Visual Studio with C++ support
    echo or Visual Studio Build Tools
    echo.
    echo Continuing with C# core build only...
    set BUILD_CPP=0
) else (
    echo C++ compiler found.
    set BUILD_CPP=1
)
echo.

:: Create output directory
echo [3/4] Creating folder structure...
set OUTPUT_DIR=%~dp0Build
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%\Core"
mkdir "%OUTPUT_DIR%\App"
echo Output directory created: %OUTPUT_DIR%
echo.

:: Build C# Core
echo [4/4] Building system core (C#)...
cd /d "%~dp0Core"
echo Compiling core...
dotnet build -c Release -o "%OUTPUT_DIR%\Core"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build core!
    pause
    exit /b 1
)
echo Core built successfully!
echo.

:: Copy core DLLs to app folder
echo Copying core DLLs to application folder...
copy "%OUTPUT_DIR%\Core\BakeryCoffeeCore.dll" "%OUTPUT_DIR%\App\" > nul
copy "%OUTPUT_DIR%\Core\BakeryCoffeeCore.pdb" "%OUTPUT_DIR%\App\" > nul 2>&1
echo.

:: Build C++ application (if possible)
if %BUILD_CPP% equ 1 (
    echo ================================================
    echo    BUILDING C++ APPLICATION
    echo ================================================
    echo.
    
    cd /d "%~dp0App"
    
    :: Try to find Visual Studio
    set VS_PATH=
    for /f "tokens=*" %%i in ('vswhere -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2^>nul') do set VS_PATH=%%i
    
    if defined VS_PATH (
        call "%VS_PATH%\Common7\Tools\VsDevCmd.bat"
    ) else (
        echo Trying standard MSVC paths...
        if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
            call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
        ) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
            call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
        ) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
            call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
        ) else (
            echo FAILED to find MSVC build environment
            echo Skipping C++ compilation
            goto :SKIP_CPP
        )
    )
    
    echo Compiling C++ application...
    cl /EHsc /O2 /Fe:"%OUTPUT_DIR%\App\BakeryCoffeeApp.exe" main.cpp kernel32.lib user32.lib
    if %errorlevel% neq 0 (
        echo ERROR: Failed to compile C++ application!
        echo But core was built successfully.
        goto :SKIP_CPP
    )
    echo C++ application compiled successfully!
    echo.
    
    :SKIP_CPP
) else (
    echo ================================================
    echo    SKIPPING C++ APPLICATION BUILD
    echo ================================================
    echo.
    echo To build C++ part, please install:
    echo - Visual Studio 2019/2022 with "Desktop development with C++"
    echo - OR Visual Studio Build Tools
    echo.
    echo After installation, run this script again.
    echo.
)

:: Create launcher file
echo ================================================
echo    CREATING LAUNCHER FILE
echo ================================================
echo.

(
echo @echo off
echo chcp 65001 ^> nul 2>&1
echo title Bakery Coffee - Seller Workstation
echo.
echo Starting system...
echo.
echo CD /D "%%~dp0App"
echo BakeryCoffeeApp.exe
echo if %%errorlevel%% neq 0 ^(
echo     echo.
echo     echo APPLICATION START ERROR
echo     echo Make sure all files are in place
echo     pause
echo ^)
) > "%OUTPUT_DIR%\START.bat"

echo Launcher file created: START.bat
echo.

:: Create README
(
echo BAKERY COFFEE MANAGEMENT SYSTEM
echo =====================================
echo.
echo Structure:
echo - Core/ - System core written in C# (.NET 6)
echo - App/  - Application written in C++
echo.
echo IMPORTANT: Core is a mandatory component!
echo Without BakeryCoffeeCore.dll the application will not start.
echo.
echo Launch:
echo 1. Double-click START.bat
echo 2. Or run App/BakeryCoffeeApp.exe directly
echo.
echo Requirements:
echo - .NET 6.0 Runtime (for core)
echo - Windows 7 or higher
echo.
) > "%OUTPUT_DIR%\README.txt"

echo README created.
echo.

:: Summary
echo ================================================
echo    BUILD COMPLETED!
echo ================================================
echo.
echo Output directory: %OUTPUT_DIR%
echo.
echo Contents:
dir /b "%OUTPUT_DIR%"
echo.
dir /b "%OUTPUT_DIR%\App"
echo.
dir /b "%OUTPUT_DIR%\Core"
echo.
echo To run the program:
echo   1. Copy the Build folder to desired location
echo   2. Run START.bat
echo.
echo ================================================

pause
