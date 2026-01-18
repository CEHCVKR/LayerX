@echo off
REM Test two transceiver instances on same machine

echo Creating second identity...
echo This will create a second test user for peer discovery testing

REM Backup original identity
if exist my_identity.json (
    copy my_identity.json my_identity_backup.json >nul
    echo Original identity backed up
)

REM Create test identity directory
mkdir test_peer 2>nul
cd test_peer

REM Copy necessary files
copy ..\transceiver.py . >nul 2>&1
copy ..\*.py . >nul 2>&1

echo.
echo ============================================================
echo Instructions:
echo ============================================================
echo 1. Keep your current transceiver.py running in the first terminal
echo 2. Open a NEW terminal window
echo 3. Run: cd H:\LAYERX\test_peer
echo 4. Run: python transceiver.py
echo 5. Enter a DIFFERENT username (e.g., "TestUser2")
echo.
echo Both instances should now discover each other!
echo ============================================================
echo.
pause
