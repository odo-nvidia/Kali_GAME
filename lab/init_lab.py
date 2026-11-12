#!/usr/bin/env python3
"""Populate one synthetic mission workspace, then keep its container alive."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/opt/kali_game")
from content import mission_by_id  # noqa: E402


def write_training_capture(destination: Path) -> None:
    from scapy.all import DNS, DNSQR, DNSRR, Ether, IP, Raw, TCP, UDP, wrpcap

    client_mac = "02:00:00:00:00:10"
    server_mac = "02:00:00:00:00:53"
    client_ip = "10.10.0.10"
    dns_ip = "10.10.0.53"
    web_ip = "10.10.0.32"
    packets = []

    for index, (name, address, dns_id) in enumerate(
        (("files.lab", web_ip, 0x2041), ("updates.lab", "10.10.0.40", 0x2042))
    ):
        query = DNS(id=dns_id, rd=1, qd=DNSQR(qname=name))
        answer = DNS(
            id=dns_id,
            qr=1,
            aa=1,
            rd=1,
            ra=1,
            qd=DNSQR(qname=name),
            an=DNSRR(rrname=f"{name}.", type="A", ttl=300, rdata=address),
        )
        packets.extend(
            (
                Ether(src=client_mac, dst=server_mac)
                / IP(src=client_ip, dst=dns_ip)
                / UDP(sport=53000 + index, dport=53)
                / query,
                Ether(src=server_mac, dst=client_mac)
                / IP(src=dns_ip, dst=client_ip)
                / UDP(sport=53, dport=53000 + index)
                / answer,
            )
        )

    request = b"GET /reports/status HTTP/1.1\r\nHost: files.lab\r\n\r\n"
    response = b"HTTP/1.1 302 Found\r\nServer: TrainingServer\r\nLocation: /login\r\nContent-Length: 0\r\n\r\n"
    packets.extend(
        (
            Ether(src=client_mac, dst=server_mac)
            / IP(src=client_ip, dst=web_ip)
            / TCP(sport=45000, dport=80, seq=1, ack=1, flags="PA")
            / Raw(load=request),
            Ether(src=server_mac, dst=client_mac)
            / IP(src=web_ip, dst=client_ip)
            / TCP(sport=80, dport=45000, seq=1, ack=1 + len(request), flags="PA")
            / Raw(load=response),
        )
    )

    for index, packet in enumerate(packets):
        packet.time = 1_780_000_000 + index
    destination.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(destination), packets)


def start_local_web(port: int, workspace: Path) -> None:
    if port not in {8080, 8081}:
        raise ValueError("Mission service port is outside the local allowlist")
    web_root = workspace / "www"
    web_root.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [
            sys.executable,
            "/usr/local/bin/local_web.py",
            "--port",
            str(port),
            "--directory",
            str(web_root),
        ],
        cwd=workspace,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(30):
        if process.poll() is not None:
            raise RuntimeError("Local training service stopped during startup")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                return
        except OSError:
            time.sleep(0.1)
    process.terminate()
    raise RuntimeError("Local training service did not become ready")


def main() -> None:
    mission_id = os.environ.get("KALI_GAME_MISSION") or (sys.argv[1] if len(sys.argv) > 1 else "")
    mission = mission_by_id(mission_id)
    workspace = Path.home() / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    for relative_path, text in mission.files.items():
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe fixture path in mission manifest")
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        destination.chmod(0o644)

    if mission.packet_capture:
        write_training_capture(workspace / "captures" / "training.pcap")
    for port in mission.service_ports:
        start_local_web(port, workspace)

    os.execlp("sleep", "sleep", "infinity")


if __name__ == "__main__":
    main()
