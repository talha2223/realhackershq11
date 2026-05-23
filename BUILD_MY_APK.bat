@echo off
echo ========================================
echo Real Hackers HQ - A-Dex APK Builder
echo ========================================
echo.
echo Preparing to build your live stealth APK...
echo.

cd A-Dex/android-app

if not exist "%ANDROID_HOME%" (
    echo [ERROR] ANDROID_HOME environment variable not found.
    echo Please ensure Android Studio is installed and the SDK path is set.
    pause
    exit /b
)

echo [1/2] Cleaning project...
call gradlew.bat clean

echo [2/2] Building Release APK...
call gradlew.bat assembleRelease

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Your APK is ready!
    echo Location: A-Dex\android-app\app\build\outputs\apk\release\app-release.apk
) else (
    echo.
    echo [FAILED] Build failed. Please check the errors above.
)

pause
