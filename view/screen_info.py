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

    @classmethod
    def scale(cls, coord: int | float | tuple | list):
        if isinstance(coord, int):
            return int(coord * cls.resize_ratio)
        elif isinstance(coord, float):
            return coord * cls.resize_ratio
        converted = [cls.scale(x) for x in coord]
        if isinstance(coord, tuple):
            return tuple(converted)
        return converted

    @classmethod
    def translate(cls, coord: tuple[int, int], shift: tuple[int, int] = (0, 0)):
        coord = cls.scale(coord)
        shift = cls.scale(shift)
        return (coord[0] + shift[0], coord[1] + shift[1])
