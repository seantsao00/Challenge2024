from const.pause_menu import PauseMainMenuOption

PAUSE_MENU_BACKGROUND_COLOR = (200, 200, 200, 230)
PAUSE_MENU_TEXT_COLOR = 'black'
PAUSE_MENU_TITLE_POSITION = (225, 80)
PAUSE_MENU_OPTION_INTERVAL = 30
PAUSE_MENU_TITLE_TEXT = 'Paused'
PAUSE_MENU_UNDERLINE_COLOR = 'darkblue'
PAUSE_MENU_UNDERLINE_THICKNESS = 2
PAUSE_MENU_UNDERLINE_OFFSET = 2
PAUSE_MAIN_MENU_TEXT: dict[PauseMainMenuOption, str] = {
    PauseMainMenuOption.RESUME_GAME: 'Resume',
    PauseMainMenuOption.OPEN_CREDIT_BOARD: 'Credit',
    PauseMainMenuOption.QUIT_GAME: 'Quit'
}
