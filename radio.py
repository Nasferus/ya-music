from random import random

from yandex_music import Track


class Radio:
    def __init__(self, client):
        self.client = client
        self.station_id = None
        self.station_from = None

        self.play_id = None
        self.index = 0
        self.current_track = None
        self.station_tracks = None

        # already played tracks, so the user can step back through them
        self.history = []

    def start_radio(self, station_id, station_from) -> Track:
        self.station_id = station_id
        self.station_from = station_from

        # get first 5 tracks
        self.__update_radio_batch(None)

        # setup current track
        self.current_track = self.__update_current_track()
        return self.current_track

    def play_next(self) -> Track:
        # send prev track finalize info
        self.__send_play_end_track(self.current_track, self.play_id)
        self.__send_play_end_radio(self.current_track, self.station_tracks.batch_id)

        # remember what was playing, so play_previous can come back to it
        self.history.append((self.current_track, self.play_id, self.station_tracks.batch_id))

        # get next index
        self.index += 1
        if self.index >= len(self.station_tracks.sequence):
            # get next 5 tracks. Set index to 0
            self.__update_radio_batch(self.current_track.track_id)

        # setup next track
        self.current_track = self.__update_current_track()
        return self.current_track

    def can_play_previous(self) -> bool:
        return len(self.history) > 0

    def play_previous(self) -> Track:
        # the track being left is finalized, but as a skip: the user did not
        # listen it to the end, and the station should not count it as played
        self.__send_play_skip(self.current_track, self.station_tracks.batch_id)

        # note: the batch_id of the track being left is deliberately not
        # reused for the step back. Once the server has seen the skip it
        # rebuilds the queue around it, so the previous track belongs to the
        # batch the station is holding now: the history entry keeps the old
        # id only so the way forward stays consistent.

        track, play_id, batch_id = self.history.pop()
        self.current_track = track
        self.play_id = play_id

        self.__send_play_start_track(track, play_id)
        self.__send_play_start_radio(track, batch_id)
        return track

    def __update_radio_batch(self, queue=None):
        self.index = 0
        self.station_tracks = self.client.rotor_station_tracks(self.station_id, queue=queue)
        self.__send_start_radio(self.station_tracks.batch_id)

    def __update_current_track(self):
        self.play_id = self.__generate_play_id()
        track = self.client.tracks([self.station_tracks.sequence[self.index].track.track_id])[0]
        self.__send_play_start_track(track, self.play_id)
        self.__send_play_start_radio(track, self.station_tracks.batch_id)
        return track

    def __send_start_radio(self, batch_id):
        self.client.rotor_station_feedback_radio_started(
            station=self.station_id, from_=self.station_from, batch_id=batch_id
        )

    def __send_play_start_track(self, track, play_id):
        total_seconds = track.duration_ms / 1000
        self.client.play_audio(
            from_="desktop_win-home-playlist_of_the_day-playlist-default",
            track_id=track.id,
            album_id=track.albums[0].id,
            play_id=play_id,
            track_length_seconds=0,
            total_played_seconds=0,
            end_position_seconds=total_seconds,
        )

    def __send_play_start_radio(self, track, batch_id):
        self.client.rotor_station_feedback_track_started(station=self.station_id, track_id=track.id, batch_id=batch_id)

    def __send_play_end_track(self, track, play_id):
        played_seconds = self.__played_seconds(track)
        total_seconds = self.__played_seconds(track)
        self.client.play_audio(
            from_="desktop_win-home-playlist_of_the_day-playlist-default",
            track_id=track.id,
            album_id=track.albums[0].id,
            play_id=play_id,
            track_length_seconds=int(total_seconds),
            total_played_seconds=played_seconds,
            end_position_seconds=total_seconds,
        )

    def __send_play_end_radio(self, track, batch_id):
        played_seconds = track.duration_ms / 1000
        self.client.rotor_station_feedback_track_finished(
            station=self.station_id, track_id=track.id, total_played_seconds=played_seconds, batch_id=batch_id
        )
        pass

    def __send_play_skip(self, track, batch_id):
        """Report the track as skipped, not as listened to the end.

        The playing itself is not reported here: the skip replaces the end
        of the track, and a second play_audio for the same play_id is what
        used to make the server reject the feedback.
        """
        # total_played_seconds must stay a live number: the server rejects
        # the whole feedback with BadRequestError when the field that backs
        # it (TrackFinishedPlaying) comes through with no value at all,
        # which is exactly what a zero turns into on the wire
        played_seconds = self.__played_seconds(track)
        self.client.rotor_station_feedback_skip(
            station=self.station_id, track_id=track.id, total_played_seconds=played_seconds, batch_id=batch_id
        )

    @staticmethod
    def __played_seconds(track):
        """Duration of the track in seconds, never falsy for the API.

        The rotor feedback is rejected when total_played_seconds is missing
        from the payload (the server reports the backing field
        TrackFinishedPlaying as unparsed), so zero must not be sent.
        """
        duration = getattr(track, 'duration_ms', None) or 0
        seconds = round(float(duration) / 1000)
        return max(1, seconds)

    @staticmethod
    def __generate_play_id():
        return "%s-%s-%s" % (int(random() * 1000), int(random() * 1000), int(random() * 1000))
