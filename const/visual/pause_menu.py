from const.pause_menu import PauseMainMenuOption

PAUSE_MENU_BACKGROUND_COLOR = (200, 200, 200, 230)
PAUSE_MENU_TEXT_COLOR = 'black'
PAUSE_MENU_TITLE_POSITION = (125, 20)
PAUSE_MENU_OPTION_INTERVAL = 8
PAUSE_MENU_TITLE_TEXT = 'Paused'
PAUSE_MAIN_MENU_TEXT: dict[PauseMainMenuOption, str] = {
    PauseMainMenuOption.RESUME_GAME: 'Resume',
    PauseMainMenuOption.OPEN_CREDIT_BOARD: 'Credit',
    PauseMainMenuOption.QUIT_GAME: 'Quit'
}
