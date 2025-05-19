pyinstaller --onefile --noconsole ^
  --add-data "Images;Images" ^
  --add-data "MineSweeper_Difficulty.py;." ^
  --add-data "MineSweeper_BoardManager.py;." ^
  --add-data "MineSweeper_GameBoard.py;." ^
  --add-data "MineSweeper_NetworkManager.py;." ^
  --add-data "MineSweeper_GameMessage.py;." ^
  --add-data "MineSweeper_ChatManager.py;." ^
  --add-data "MineSweeper_Timer.py;." ^
  --add-data "MineSweeper_Event.py;." ^
  MineSweeper.py