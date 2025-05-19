@echo off
chcp 65001
echo 清理打包環境...

rd /s /q build
rd /s /q dist

echo 開始打包...

pyinstaller --onefile --noconsole --add-data ".;." GameMenu.py

pause