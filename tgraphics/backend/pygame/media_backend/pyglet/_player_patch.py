# ----------------------------------------------------------------------------
# Copyright (c) 2006-2008 Alex Holkner
# Copyright (c) 2008-2020 pyglet contributors
# Copyright (c) 2021 TheerapakG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import pyglet

from ._pyglet_clock_binder import pyglet_clock_binder

class PatchedPlayer(pyglet.media.Player):
    def __init__(self, tgraphics_player):
        self._tplayer = tgraphics_player
        super().__init__()

    def play(self, window):
        pyglet_clock_binder.add_player(self, window=window)
        super().play()

    def pause(self):
        super().pause()
        pyglet_clock_binder.remove_player(self)

    def delete(self):
        pyglet_clock_binder.remove_player(self)
        super().delete()

    # @TheerapakG: a hack to make update_texture store image in memory instead of
    # uploading to the opengl driver
    def update_texture(self, dt=None):
        """Manually update the texture from the current source.
        This happens automatically, so you shouldn't need to call this method.
        Args:
            dt (float): The time elapsed since the last call to
                ``update_texture``.
        """
        source = self.source
        time = self.time

        frame_rate = source.video_format.frame_rate
        frame_duration = 1 / frame_rate
        ts = source.get_next_video_timestamp()
        # Allow up to frame_duration difference
        while ts is not None and ts + frame_duration < time:
            source.get_next_video_frame()  # Discard frame
            ts = source.get_next_video_timestamp()

        if ts is None:
            # No more video frames to show. End of video stream.

            pyglet.clock.schedule_once(self._video_finished, 0)
            return

        image = source.get_next_video_frame()
        if image is not None:
            self._tplayer._image = image

        ts = source.get_next_video_timestamp()
        if ts is None:
            delay = frame_duration
        else:
            delay = ts - time

        delay = max(0.0, delay)
        pyglet.clock.schedule_once(self.update_texture, delay)

