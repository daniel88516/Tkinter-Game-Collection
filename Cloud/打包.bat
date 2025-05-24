@echo off
chcp 65001

:: 關閉 GameMenu.exe 避免鎖檔
taskkill /f /im GameMenu.exe >nul 2>nul
timeout /t 1 >nul

echo 清理打包環境...
rd /s /q build
rd /s /q dist

echo 開始打包...

set SQLITE_PYD=C:/Users/danie/AppData/Local/Programs/Python/Python312/DLLs/_sqlite3.pyd

pyinstaller ^
  --onefile ^
  --hidden-import=sqlite3 ^
  --hidden-import=requests ^
  --hidden-import=tkinter.simpledialog ^
  --add-binary "%SQLITE_PYD%";. ^
  --add-data ".";. ^
  GameMenu.py

echo ✅ 打包完成！
start dist\GameMenu.exe
pause
