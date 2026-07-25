@echo off
setlocal enabledelayedexpansion
title AetherNet - PyInstaller Production Build Script

echo =======================================================================
echo               ⚡ AETHERNET - OPTIMIZED BUILD SYSTEM ⚡
echo =======================================================================
echo.
echo Lutfen Derleme Modunu Secin:
echo.
echo  [1] Standart Derleme (Mevcut .env ve config/ yapilandirmalarini KORUR)
echo  [2] Tam Temiz Derleme (Tum build/dist/spec/cache/env dosyalarini SIFIRLAR)
echo.
set /p CHOICE="Seciminiz (1 veya 2): "

if "%CHOICE%"=="1" goto BUILD_STANDARD
if "%CHOICE%"=="2" goto BUILD_CLEAN
echo [!] Gecersiz secim. Cikiliyor...
pause
exit /b 1

:BUILD_STANDARD
echo.
echo [*] Standart Derleme Baslatiliyor (Konfigurasoynlar korunuyor)...
echo.
goto RUN_PYINSTALLER

:BUILD_CLEAN
echo.
echo [*] Tam Temiz Derleme Yapiliyor...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo [+] Temizlik tamamlandi.
goto RUN_PYINSTALLER

:RUN_PYINSTALLER
echo.
echo [*] Varlıklar ve Icon Kontrol Ediliyor...
if not exist "assets\icon.ico" (
    echo [*] Icon bulunamadi, varliklar olusturuluyor...
    python scripts/generate_assets.py
)

echo.
echo [*] PyInstaller ile Yuksek Optimizasyonlu .exe Derleniyor...
echo.

pyinstaller --noconfirm --clean --onefile --noconsole ^
    --name="AetherNet" ^
    --icon="assets/icon.ico" ^
    --add-data="config;config" ^
    --add-data="assets;assets" ^
    --exclude-module="tkinter" ^
    --exclude-module="matplotlib" ^
    --exclude-module="IPython" ^
    --exclude-module="PIL._imagingtk" ^
    --paths="src" ^
    src/aethernet/main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =======================================================================
    echo [✓] BASARILI: AetherNet.exe basariyla derlendi!
    echo [>] Konum: dist\AetherNet.exe
    echo =======================================================================
) else (
    echo.
    echo [X] HATA: PyInstaller derleme sirasinda bir sorunla karsilasti.
)

echo.
pause
