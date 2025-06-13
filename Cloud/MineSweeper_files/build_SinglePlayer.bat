pyinstaller --onefile --noconsole ^
  --add-data "Images;Images" ^
  --add-data "minesweeper.db;." ^
  --add-data "MineSweeper_Difficulty.py;." ^
  --add-data "MineSweeper_GameBoard.py;." ^
  --add-data "MineSweeper_Timer.py;." ^
  --add-data "MineSweeper_RankingPage.py;." ^
  --add-data "MineSweeper_Database.py;." ^
  --add-data "MineSweeper_Event.py;." ^
  MineSweeper_SinglePlayer.py