from model.AlertModel import PedestrianFrontAlert, PedestrianRearAlert, DriverAlert, NoPhoneAlert, NoHelmetAlert
from enum import IntEnum

AlertList = [
    PedestrianFrontAlert(),
    PedestrianRearAlert(),
    DriverAlert(),
    NoPhoneAlert(),
    NoHelmetAlert()
]


class AlertEnum(IntEnum):
    NoAlert = 99
    PedestrianFront = 0
    PedestrianRear = 1
    DriverFocus = 2
    NoPhone = 3
    NoHelmet = 4


AlertDict = {
    AlertEnum.PedestrianFront: PedestrianFrontAlert(),
    AlertEnum.PedestrianRear: PedestrianRearAlert(),
    AlertEnum.DriverFocus: DriverAlert(),
    AlertEnum.NoPhone: NoPhoneAlert(),
    AlertEnum.NoHelmet: NoHelmetAlert()
}
