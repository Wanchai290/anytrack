@echo off
rem i'm not a win cmd developer
rem don't expect fancy stuff here

py -m pip install -r requirements.txt
if %errorlevel%==0 (
    echo Requirements installed successfully !
) else (
    echo Error while installing requirements
)
pause