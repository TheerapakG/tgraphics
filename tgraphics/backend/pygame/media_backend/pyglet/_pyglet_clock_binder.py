from collections import defaultdict
import pyglet

from ...pygame import current_renderer

class _PygletClockBinder:
    def __init__(self) -> None:
        self.players = defaultdict(set)
        self.windows = dict()

    def add_player(self, player, window):
        if not self.players[window]:
            window.event['on_draw'].add_listener(pyglet.clock.tick)
            window.event['on_destroy'].add_listener(player.delete)
        self.players[window].add(player)
        self.windows[player] = window

    def remove_player(self, player):
        try:
            window = self.windows[player]
        except KeyError:
            # already deleted
            return
        del self.windows[player]
        self.players[window].discard(player)
        if not self.players[window]:
            window.event['on_draw'].remove_listener(pyglet.clock.tick)
            window.event['on_destroy'].remove_listener(player.delete)

pyglet_clock_binder = _PygletClockBinder()
