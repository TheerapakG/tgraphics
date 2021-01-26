import pyglet

from ...pygame import _PreRenderHooks

class _PygletClockBinder:
    def __init__(self) -> None:
        self.players = set()

    def add_player(self, player):
        if not self.players:
            _PreRenderHooks.add(pyglet.clock.tick)
        self.players.add(player)

    def remove_player(self, player):
        self.players.discard(player)
        if not self.players:
            _PreRenderHooks.discard(pyglet.clock.tick)

pyglet_clock_binder = _PygletClockBinder()
