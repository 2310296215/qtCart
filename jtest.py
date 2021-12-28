from jtop import jtop
import json, datetime

jetson = jtop()

while True:
    tmp = jetson.stats 
    print(tmp)
    if jetson.ok():
        tmp = jetson.stats 
        print(tmp)
        # time and uptime are proved as time objects. These needed to be converted before passing as a JSON string,
        tmp["time"] = str(tmp["time"].strftime('%m/%d/%Y'))
        tmp["uptime"] = str(tmp["uptime"])
        # We then convert our dict -> Json string
        influx_json= {"jetson": tmp}
        print(json.dumps(influx_json))

    else:
        print("stat")