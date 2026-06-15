@echo off
title Telegram Marketing Bot — 24/7 Runner
color 0A

:: ============================================================
::  run.bat  — Auto-restart wrapper for main.py
::  Double-click this file to start the bot.
::  If the script crashes or exits for any reason,
::  it will restart automatically after 60 seconds.
::  To STOP permanently: close this window.
:: ============================================================

:start
cls
echo.
echo  ============================================================
echo    TELEGRAM MARKETING BOT  ^|  24/7 Auto Runner
echo  ============================================================
echo.
echo  Bot is starting...
echo  To stop permanently: close this window or press Ctrl+C twice
echo.
echo  ============================================================
echo.

python main.py

echo.
echo  ============================================================
echo   Bot stopped (crash or Ctrl+C).
echo   Restarting in 60 seconds...
echo   Close this window NOW if you want to stop completely.
echo  ============================================================
echo.

timeout /t 60 /nobreak
goto start