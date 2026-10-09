#!/usr/bin/env python3

import time
import docker
import subprocess

BACKUP_CHECK_INTERVAL=60
BACKUP_INTERVAL_DEFAULT=86400 # 24h

servers = []

docker_client = docker.from_env()

volume_map = {}

for v in docker_client.volumes.list():
    if v.attrs["Options"]["o"] == "bind":
       volume_map[v.name] = v.attrs["Options"]["device"]

print(volume_map)

last_backups = {}

while True:
    for cnt in docker_client.containers.list():
        last_backup = last_backups.setdefault(cnt.name, 0)

        backup_interval = int(cnt.labels.get("minecraft.backup.interval", BACKUP_INTERVAL_DEFAULT))

        if time.time() - last_backup > backup_interval:
            backup_dest = cnt.labels.get("minecraft.backup.dest")

            if backup_dest is not None or True:
                volume_path = None
                for m in cnt.attrs["Mounts"]:
                    if m["Destination"] == "/data":
                        volume_path = volume_map[m["Name"]]
                        break

                if volume_path is not None:
                    worlds_path = volume_path + "/worlds"
                    print(f"Backing up {cnt.name} from {worlds_path} to {backup_dest}...")
                    cmd = ["./mcbak", "docker", cnt.name, worlds_path, backup_dest]
                    p = subprocess.Popen(cmd)
                    p.wait()

            last_backups[cnt.name] = time.time()

    time.sleep(BACKUP_CHECK_INTERVAL)
