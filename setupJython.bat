REM This script gathers information about the HEC-WAT folder in a HEC-WAT installation
REM Call this batch file from another batch file.
REM This second batch file runs the Jython interpreter and Jython script.

REM --------------- NOTES ---------------
REM UNC paths are not supported in cmd. If accessing a network drive, need to map to a letter first.

REM @ECHO off

REM add new DSS locations to the list starting on line 12
set dssLocations=^
	"C:\Programs\HEC-DSSVue-win-3.2.9"

REM determine how many of the DSS locations exist on this user's computer
set counter=0
for %%i in (!dssLocations!) do (
    if exist %%i (
        set /a counter+=1
    )
)

REM Iterate through DSS locations again
REM If more than one DSS location is found, prompt user to ask which DSS to user
REM If one DSS location is found, use this one
REM If no DSS locations are found, exit
for %%i in (!dssLocations!) do (
    if exist %%i (
        ECHO File found: %%i
        if !counter! GTR 1 (
            set fileFound=
            set /p fileFound="Is this your DSS installation? (Y/N)"
            if not '!fileFound!'=='' set fileFound=!fileFound:~0,1!
            if '!fileFound!'=='y' (
            set hecDssDirectory=%%i
            goto :endofloop
            )
        ) else (
            set hecDssDirectory=%%i
            goto :endofloop
        )
    )
)

:endofloop
if '%hecDssDirectory%'=='' goto failed
ECHO Using DSS located at: %hecDssDirectory%
goto end

:failed
exit /b 1

:end
cd /d %hecDssDirectory%