@echo off
setlocal enabledelayedexpansion
title AetherNet - PyInstaller Production Build System

echo =======================================================================
echo               ⚡ AETHERNET - OPTIMIZED BUILD SYSTEM ⚡
echo =======================================================================
echo.
echo Lutfen Derleme Modunu Secin:
echo.
echo  [1] Standart Derleme (Hizli - Mevcut gecici klasorleri korur)
echo  [2] Tam Temiz Derleme (Sifirdan temizlik ve optimizasyonlu derleme)
echo.
set /p CHOICE="Seciminiz (1 veya 2, varsayilan: 2): "

if "%CHOICE%"=="" set CHOICE=2
if "%CHOICE%"=="1" goto BUILD_STANDARD
if "%CHOICE%"=="2" goto BUILD_CLEAN

echo [!] Gecersiz secim yapildi, Tam Temiz Derleme (2) seciliyor...
goto BUILD_CLEAN

:BUILD_STANDARD
echo.
echo [*] Standart Derleme Baslatiliyor...
goto RUN_PYINSTALLER

:BUILD_CLEAN
echo.
echo [*] Tam Temiz Derleme Yapiliyor (build, dist, cache temizleniyor)...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo [+] Temizlik tamamlandi.

:RUN_PYINSTALLER
echo.
echo [*] Varliklar ve Icon Kontrol Ediliyor...
if not exist "assets\icon.ico" (
    echo [*] Icon bulunamadi, varliklar olusturuluyor...
    python scripts/generate_assets.py
)

echo.
echo [*] PyInstaller ile Yuksek Optimizasyonlu .exe Derleniyor...
echo.

pyinstaller --noconfirm --clean AetherNet.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =======================================================================
    echo [✓] BASARILI: AetherNet.exe basariyla derlendi!
    echo [>] Konum: dist\AetherNet.exe
    echo =======================================================================
) else (
    echo.
    echo [X] HATA: PyInstaller derleme sirasinda bir sorunla karsilasti.
    exit /b %ERRORLEVEL%
)

echo.
