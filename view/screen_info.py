class ScreenInfo:  # nopep8
    """Class for screen info."""
    resize_ratio: float
    """Ratio between model coordinate and screen size."""
    screen_size: tuple[int, int]
    initialized: bool = False

    @classmethod
    def set_screen_info(cls, resize_ratio: float, screen_size: tuple[int, int]):
        assert not cls.initialized, "You can't set screen info twice."
        cls.resize_ratio = resize_ratio
        cls.screen_size = screen_size
        cls.initialized = True
