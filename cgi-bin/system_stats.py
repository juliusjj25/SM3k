#!/usr/bin/env python3
import os
import shutil
import psutil
import json

print("Content-Type: application/json\n")

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except Exception as e:
        return None

try:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    data = {
        "cpu": psutil.cpu_percent(interval=0.5),
        "mem": mem.percent,
        "mem_used": mem.used / (1024 *1024),
        "mem_total": mem.total / (1024 * 1024),
        "disk": disk.percent,
        "disk_used": disk.used,
        "disk_total": disk.total,
        "temp": get_cpu_temp()
    }
    print(json.dumps(data))
except Exception as e:
    print(json.dumps({ "error": str(e) }))
