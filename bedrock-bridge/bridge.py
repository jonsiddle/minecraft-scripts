#!/usr/bin/env python3
import secrets
import socket
import struct
import time
import docker
import sys
import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s %(levelname)s] %(message)s")


servers = []

docker_client = docker.from_env()

for cnt in docker_client.containers.list():
    if cnt.labels.get("minecraft.broadcast", "").lower() == "true":
        server_ip = [*cnt.attrs["NetworkSettings"]["Networks"].values()][0]["IPAddress"]

        for keyval in cnt.attrs["Config"]["Env"]:
            server_port = None
            key = "SERVER_PORT"
            if keyval.startswith(f"{key}="):
                server_port = int(keyval[len(key)+1:])
                break

        if server_ip is not None and server_port is not None:
            servers.append((server_ip, server_port))

logging.info("Servers:")
for server_ip, server_port in servers:
    logging.info(f"- {server_ip}:{server_port}")

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")

CLIENT_GUID = secrets.randbits(63)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_ping(server_ip, server_port):
    ts = int(time.time() * 1000)
    payload = b"\x01"+ struct.pack(">Q", ts) + MAGIC + struct.pack(">Q", CLIENT_GUID)
    sock.sendto(payload, (server_ip, server_port))
    logging.info(f"Sent discovery request to {server_ip}:{server_port}")
    data, client = sock.recvfrom(2048)
    return data


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 19132))


while True:
    data, client = sock.recvfrom(2048)

    logging.debug("Recevied packet")
    logging.debug(data)

    if len(data) < 33:
        logging.warning("ERROR: Short package")
        continue

    if data[0] not in (0x01, 0x02):
        logging.warning(f"ERROR: {hex(data[0])} not in 0x01, 0x02'")
        continue

    if data[9:25] != MAGIC:
        logging.warning(f"ERROR: Bad magic: {hex(data[9:25])}")
        continue

    logging.info(f"Recevied discovery request from {client}")

    for server_ip, server_port in servers:
        pong = send_ping(server_ip, server_port)

        # Newer servers have extra - currently undocumented fields
        # which seem to be broken by default. This is a hack to
        # make it work until I figure out what they actually mean.
        if pong.endswith(b"0;0;0;"):
            pong = pong[:-6] + b"0;1;0;"


        logging.info(f"Relaying response to {client}")
        logging.debug(pong)

        sock.sendto(pong, client)
