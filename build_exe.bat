@echo off
REM Genera el ejecutable en dist\CriaturasPOO.exe
cd /d "%~dp0"
echo Compilando CriaturasPOO...
pyinstaller --clean --noconfirm CriaturasPOO.spec
if %ERRORLEVEL% equ 0 (
    echo.
    echo Listo: dist\CriaturasPOO.exe
    echo La partida se guarda como partida.json junto al .exe
) else (
    echo Error en la compilacion.
    exit /b 1
)
