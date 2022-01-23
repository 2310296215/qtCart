import depthai as dai
from pathlib import Path
import yaml

home_dir = Path(__file__).resolve().parent.parent.resolve()
config_path = Path(home_dir, 'config.yml').resolve().absolute()

with open(config_path, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


def check_str(s: str):
    spl = s.split(".")
    if len(spl) != 4:
        raise ValueError(f"Entered value {s} doesn't contain 3 dots. Value has to be in the following format: '255.255.255.255'")
    for num in spl:
        if 255 < int(num):
            raise ValueError("Entered values can't be above 255!")
    return s

def set_ip():
    cam_ip_input = input("輸入現在相機的設定：左(l) 右(r) 前(f)")

    ip_dict = {
        'l': config["LEFT_CAMERA_ID"],
        'r': config["RIGHT_CAMERA_ID"],
        'f': config["FRONT_CAMERA_ID"]
    }

    cam_ip_to_set = ip_dict.get(cam_ip_input.lower(), None)

    return cam_ip_to_set


def main():

    print("GO")
    # print(dai.Device.getAllAvailableDevices())
    (found, info) = dai.DeviceBootloader.getFirstAvailableDevice()
    # print(dir(info))
    # print(info.getMxId())
    # print(found, info)
    if not found:
        raise Exception("沒有找到相機 請檢查網路設定")

    print(f"目前相機ip為:{info.getMxId()}")
    # print(f'Found device with name: {info.desc.name}')
    # print('-------------------------------------')
    # print('"1" to set a static IPv4 address')
    # print('"2" to set a dynamic IPv4 address')
    # print('"3" to clear the config')
    # key = input('Enter the number: ').strip()
    # print('-------------------------------------')
    # if int(key) < 1 or 3 < int(key):
    #     raise ValueError("Entered value should either be '1', '2' or '3'!")

    cam_ip_to_set = set_ip()

    if cam_ip_to_set is None:
        print("選項錯誤!!")
        return

    with dai.DeviceBootloader(info) as bl:
        # if key in ['1', '2']:
        ipv4 = check_str(cam_ip_to_set)
        mask = check_str("255.255.255.0")
        gateway = check_str("255.255.255.255")
        mode = 'static' ## if key == '1' else 'dynamic'
        val = input(f"現在要把相機設定為 {mode} IPv4 {ipv4}, mask {mask}, gateway {gateway} to the POE device. Enter 'y' to confirm. ").strip()
        if val != 'y':
            raise Exception("Flashing aborted.")

        conf = dai.DeviceBootloader.Config()

        conf.setStaticIPv4(ipv4, mask, gateway)
            # elif key == '2': conf.setDynamicIPv4(ipv4, mask, gateway)
        (success, error) = bl.flashConfig(conf)
        # elif key == '3':
        #     (success, error) = bl.flashConfigClear()

        if not success:
            print(f"Flashing failed: {error}")
        else:
            print(f"Flashing successful.")


if __name__ == '__main__':
    main()