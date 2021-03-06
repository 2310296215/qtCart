from abc import ABC


class WarnAlert(ABC):
    warn_message = 'abstract warning'
    warn_color = None
    alertIndex = 99

    @classmethod
    def yellowAlert(cls):
        cls.warn_color = 'yellow'

    @classmethod
    def redAlert(cls):
        cls.warn_color = 'red'


class PedestrianFrontAlert(WarnAlert):
    warn_message = '注意前方行人'
    warn_file = 'sound/pedestrian_front.wav'


class PedestrianRearAlert(WarnAlert):
    warn_message = '注意後方行人'
    warn_file = 'sound/pedestrian_rear.wav'


class DriverAlert(WarnAlert):
    warn_message = '駕駛注意'
    warn_file = 'sound/driver_focus.wav'


class NoPhoneAlert(WarnAlert):
    warn_message = '請勿使用手機'
    warn_file = 'sound/no_phone.wav'

class NoHelmetAlert(WarnAlert):
    warn_message = '請配戴安全帽'
    warn_file = 'sound/no_helmet.wav'