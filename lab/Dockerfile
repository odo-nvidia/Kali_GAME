FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bash binutils ca-certificates coreutils curl findutils file gawk grep iproute2 \
       iputils-ping jq less libimage-exiftool-perl nmap procps python3 \
       python3-scapy sed tcpdump tshark whatweb xxd yara \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /bin/bash learner \
    && mkdir -p /home/learner/workspace /home/learner/.config /home/learner/.cache /opt/kali_game \
    && chown -R learner:learner /home/learner

COPY content.py /opt/kali_game/content.py
COPY lab/init_lab.py /usr/local/bin/init_lab.py
COPY lab/local_web.py /usr/local/bin/local_web.py

USER 1000:1000
WORKDIR /home/learner/workspace
ENTRYPOINT ["python3", "/usr/local/bin/init_lab.py"]
CMD ["l0-m1"]
