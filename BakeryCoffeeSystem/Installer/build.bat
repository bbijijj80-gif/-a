@echo off
chcp 65001 > nul
title Сборщик системы Пекарня-Кофейня

echo ================================================
echo    СБОРЩИК СИСТЕМЫ УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ
echo ================================================
echo.

:: Проверка наличия .NET SDK
echo [1/4] Проверка наличия .NET SDK...
dotnet --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: .NET SDK не найден!
    echo Установите .NET SDK 6.0 или выше с https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo .NET SDK найден. Версия:
dotnet --version
echo.

:: Проверка наличия Visual Studio Build Tools для C++
echo [2/4] Проверка компилятора C++...
where cl > nul 2>&1
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Компилятор MSVC (cl.exe) не найден в PATH
    echo Для компиляции C++ части установите Visual Studio с поддержкой C++
    echo или Visual Studio Build Tools
    echo.
    echo Продолжаем только сборку ядра C#...
    set BUILD_CPP=0
) else (
    echo Компилятор C++ найден.
    set BUILD_CPP=1
)
echo.

:: Создание выходной папки
echo [3/4] Создание структуры папок...
set OUTPUT_DIR=%~dp0Build
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%\Core"
mkdir "%OUTPUT_DIR%\App"
echo Выходная папка создана: %OUTPUT_DIR%
echo.

:: Сборка ядра на C#
echo [4/4] Сборка ядра системы (C#)...
cd /d "%~dp0Core"
echo Компиляция ядра...
dotnet build -c Release -o "%OUTPUT_DIR%\Core"
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось собрать ядро!
    pause
    exit /b 1
)
echo Ядро успешно собрано!
echo.

:: Копирование DLL ядра в папку приложения
echo Копирование ядра в папку приложения...
copy "%OUTPUT_DIR%\Core\BakeryCoffeeCore.dll" "%OUTPUT_DIR%\App\" > nul
copy "%OUTPUT_DIR%\Core\BakeryCoffeeCore.pdb" "%OUTPUT_DIR%\App\" > nul 2>&1
echo.

:: Сборка C++ приложения (если возможен)
if %BUILD_CPP% equ 1 (
    echo ================================================
    echo    СБОРКА C++ ПРИЛОЖЕНИЯ
    echo ================================================
    echo.
    
    cd /d "%~dp0App"
    
    :: Находим путь к Visual Studio
    for /f "tokens=*" %%i in ('vswhere -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2^>nul') do set VS_PATH=%%i
    
    if defined VS_PATH (
        call "%VS_PATH%\Common7\Tools\VsDevCmd.bat"
    ) else (
        echo Попытка использования стандартного пути MSVC...
        if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
            call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
        ) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
            call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
        ) else (
            echo НЕ УДАЛОСЬ найти среду компиляции MSVC
            echo Пропускаем компиляцию C++
            goto :SKIP_CPP
        )
    )
    
    echo Компиляция C++ приложения...
    cl /EHsc /O2 /Fe:"%OUTPUT_DIR%\App\BakeryCoffeeApp.exe" main.cpp kernel32.lib user32.lib
    if %errorlevel% neq 0 (
        echo ОШИБКА: Не удалось скомпилировать C++ приложение!
        echo Но ядро собрано успешно.
        goto :SKIP_CPP
    )
    echo C++ приложение успешно скомпилировано!
    echo.
    
    :SKIP_CPP
) else (
    echo ================================================
    echo    ПРОПУСК СБОРКИ C++ ПРИЛОЖЕНИЯ
    echo ================================================
    echo.
    echo Для сборки C++ части установите:
    echo - Visual Studio 2019/2022 с компонентом "Разработка на C++"
    echo - ИЛИ Visual Studio Build Tools
    echo.
    echo После установки запустите этот скрипт снова.
    echo.
)

:: Создание файла запуска
echo ================================================
echo    СОЗДАНИЕ ФАЙЛА ЗАПУСКА
echo ================================================
echo.

(
echo @echo off
echo chcp 65001 ^> nul
echo title Пекарня-Кофейня - Рабочее место продавца
echo.
echo Запуск системы...
echo.
echo CD /D "%%~dp0App"
echo BakeryCoffeeApp.exe
echo if %errorlevel% neq 0 ^(
echo     echo.
echo     echo ОШИБКА ЗАПУСКА ПРИЛОЖЕНИЯ
echo     echo Убедитесь, что все файлы на месте
echo     pause
echo ^)
) > "%OUTPUT_DIR%\START.bat"

echo Файл запуска создан: START.bat
echo.

:: Создание README
(
echo СИСТЕМА УПРАВЛЕНИЯ ПЕКАРНЕЙ-КОФЕЙНЕЙ
echo =====================================
echo.
echo Структура:
echo - Core/ - Ядро системы на C# (.NET 6)
echo - App/  - Приложение на C++
echo.
echo ВАЖНО: Ядро является обязательным компонентом!
echo Без файла BakeryCoffeeCore.dll приложение не запустится.
echo.
echo Запуск:
echo 1. Дважды кликните на START.bat
echo 2. Или запустите App/BakeryCoffeeApp.exe напрямую
echo.
echo Требования:
echo - .NET 6.0 Runtime (для ядра)
echo - Windows 7 и выше
echo.
) > "%OUTPUT_DIR%\README.txt"

echo README создан.
echo.

:: Итог
echo ================================================
echo    СБОРКА ЗАВЕРШЕНА!
echo ================================================
echo.
echo Выходная папка: %OUTPUT_DIR%
echo.
echo Содержимое:
dir /b "%OUTPUT_DIR%"
echo.
dir /b "%OUTPUT_DIR%\App"
echo.
dir /b "%OUTPUT_DIR%\Core"
echo.
echo Для запуска программы:
echo   1. Скопируйте папку Build в нужное место
echo   2. Запустите START.bat
echo.
echo ================================================

pause
