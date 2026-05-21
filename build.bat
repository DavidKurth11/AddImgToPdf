@echo off
echo ========================================
echo   RECREAR EXE SIN VENTANA DE CMD
echo ========================================
echo.
echo Este script limpiara los archivos anteriores
echo y creara un nuevo .exe sin ventana de CMD
echo.
pause

echo.
echo [1/3] Limpiando archivos anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist InsertarImagenPDF.spec del /q InsertarImagenPDF.spec
echo Limpieza completada

echo.
echo [2/3] Creando nuevo ejecutable
echo (Puede tardar 1-2 minutos)
echo.

REM Agregar Scripts al PATH temporal
for /f "delims=" %%i in ('py -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
for %%i in ("%PYTHON_PATH%") do set PYTHON_DIR=%%~dpi
set PATH=%PYTHON_DIR%Scripts;%PATH%

REM Crear el ejecutable con --windowed (sin consola)
py -m PyInstaller --onefile --windowed --name="AddImgToPdf" AddImgToPdf.py

if errorlevel 1 (
    echo.
    echo ERROR al crear el ejecutable
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando el ejecutable...
if exist dist\AddImgToPdf.exe (
    echo EXITO: Ejecutable creado correctamente
) else (
    echo ERROR: No se encontro el ejecutable
    pause
    exit /b 1
)

echo.
echo ========================================
echo   EJECUTABLE CREADO EXITOSAMENTE
echo ========================================
echo.
echo Tu nuevo .exe esta en: dist\AddImgToPdf.exe
echo.
echo AHORA SIN VENTANA DE CMD
echo.
echo Al ejecutar InsertarImagenPDF.exe se abrira
echo SOLO la interfaz grafica, sin CMD.
echo.
echo Puedes copiar ese archivo a cualquier PC
echo con Windows y funcionara sin instalar nada.
echo.
pause