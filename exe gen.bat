:: Created by HUNTER
@echo off
goto makeFolder
:makeFolder
echo ############################################
echo            Created by :- HUNTER
echo     2021 Software Developer VTASL Batch 1
echo ############################################
	set /P id=Enter Your File Name : 
    echo ############################################
	set name="%id%"
	pyinstaller --onefile %name%.py
    pause
cls