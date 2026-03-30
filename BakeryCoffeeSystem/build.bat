@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Система сборки Пекарня-Кофейня
echo ============================================
echo.

REM Проверка наличия .NET SDK
echo [1/5] Проверка .NET SDK...
where dotnet >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: .NET SDK не найден!
    echo Установите .NET 6.0 SDK с https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo .NET SDK найден

REM Проверка наличия MinGW/g++
echo.
echo [2/5] Проверка компилятора C++...
where g++ >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Компилятор g++ не найден!
    echo Установите MinGW-w64 с https://www.mingw-w64.org/
    echo Или используйте MSYS2
    pause
    exit /b 1
)
echo Компилятор g++ найден: 
g++ --version | findstr /C:"g++"

REM Создание структуры папок
echo.
echo [3/5] Создание структуры папок...
if not exist "build" mkdir build
if not exist "build\data" mkdir build\data
if not exist "build\Core" mkdir build\Core
echo Папки созданы

REM Сборка ядра на C#
echo.
echo [4/5] Сборка ядра C#...
cd Core
call dotnet restore
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось выполнить restore для ядра
    cd ..
    pause
    exit /b 1
)

call dotnet build -c Release
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось собрать ядро
    cd ..
    pause
    exit /b 1
)

REM Копирование DLL ядра в папку сборки
if exist "bin\Release\net6.0-windows\BakeryCoffeeCore.dll" (
    copy /Y "bin\Release\net6.0-windows\BakeryCoffeeCore.dll" "..\build\Core\"
    echo Ядро собрано и скопировано
) else if exist "bin\Release\net6.0\BakeryCoffeeCore.dll" (
    copy /Y "bin\Release\net6.0\BakeryCoffeeCore.dll" "..\build\Core\"
    echo Ядро собрано и скопировано
) else (
    echo ПРЕДУПРЕЖДЕНИЕ: DLL ядра не найдена в ожидаемом месте
    dir /s /b *.dll
)
cd ..

REM Сборка приложения на C++
echo.
echo [5/5] Сборка приложения C++...
g++ -o build\BakeryCoffeeApp.exe App\main.cpp -lws2_32 -static-libgcc -static-libstdc++ -municode
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось собрать приложение C++
    pause
    exit /b 1
)
echo Приложение собрано

REM Финальные шаги
echo.
echo ============================================
echo   Сборка завершена успешно!
echo ============================================
echo.
echo Результат в папке: build\
echo.
dir build
echo.
echo Структура папок:
echo   build\
echo     ├── BakeryCoffeeApp.exe  (основное приложение)
echo     ├── Core\
echo     │   └── BakeryCoffeeCore.dll  (ядро системы)
echo     └── data\  (данные будут созданы при запуске)
echo.
echo Для запуска программы:
echo   1. Перейдите в папку build
echo   2. Запустите BakeryCoffeeApp.exe
echo.
echo ВАЖНО: Без файла BakeryCoffeeCore.dll программа не запустится!
echo.
pause
