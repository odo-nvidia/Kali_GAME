# 🛡️ KALI_GAME_v04

> 🇵🇱 Gra terminalowa po polsku do nauki Kali Linux i cyberbezpieczeństwa  
> 🇬🇧 Terminal game in Polish to learn Kali Linux and cybersecurity  

[![Python 3](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Engine-blue?logo=docker)](https://docker.com)
[![tmux](https://img.shields.io/badge/tmux-enabled-green.svg)](https://github.com/tmux/tmux)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PL/EN](https://img.shields.io/badge/lang-PL%2FEN-red.svg)]()
[![Kali ARM64](https://img.shields.io/badge/Target-Kali%20ARM64-purple.svg)](https://kali.org)
[![82 missions](https://img.shields.io/badge/Missions-82-brightgreen.svg)]()

---

## 🎮 O GRZE / ABOUT THE GAME

**PL:**  
`Kali_GAME` to lokalna, terminalowa gra edukacyjna w dwóch panelach `tmux`. Gracz rozwiązuje **82 misje na 13 poziomach** wewnątrz izolowanych kontenerów Docker (Debian, nie-root, bez sieci hosta). Nauka przez praktykę: `find`, `grep`, `nmap`, `tshark`, `tcpdump`, `whatweb`, `curl`, `file`, `sha256sum`, `strings`, `xxd`, `exiftool`, `jq`, `yara` i wiele innych.

**EN:**  
`Kali_GAME` is a local terminal educational game in two `tmux` panels. Player solves **82 missions on 13 levels** inside isolated Docker containers (Debian, non-root, no host network). Learn by doing: `find`, `grep`, `nmap`, `tshark`, `tcpdump`, `whatweb`, `curl`, `file`, `sha256sum`, `strings`, `xxd`, `exiftool`, `jq`, `yara` and more.

---

## 🖥️ PODGLĄD / PREVIEW

```
    _/    _/            _/  _/    _/_/_/    _/_/    _/      _/  _/_/_/_/   
   _/  _/      _/_/_/  _/      _/        _/    _/  _/_/  _/_/  _/          
  _/_/      _/    _/  _/  _/  _/  _/_/  _/_/_/_/  _/  _/  _/  _/_/_/       
 _/  _/    _/    _/  _/  _/  _/    _/  _/    _/  _/      _/  _/            
_/    _/    _/_/_/  _/  _/    _/_/_/  _/    _/  _/      _/  _/_/_/_/       
                                                                           
                      _/_/_/_/_/                                     
                                                      
     🛡️  Kali_GAME — Learn Kali Linux by playing  🛡️
```

**PL:** Gra otwiera sesję `tmux`. Lewy panel: menu misji. Prawy panel: lab w kontenerze.  
**EN:** Game opens a `tmux` session. Left panel: mission menu. Right panel: container lab.

---

## 🚀 SZYBKI START / QUICK START

### Wymagania / Requirements
- Kali Linux ARM64 (Parallels zalecane)
- Python 3, `tmux`, Docker Engine (ARM64)
- Internet przy pierwszym budowie obrazu labu

### Instalacja / Install
```bash
sudo apt update && sudo apt install -y python3 tmux docker.io
sudo systemctl enable --now docker
```

### Uruchomienie / Run
```bash
git clone https://github.com/odo-nvidia/Kali_GAME.git
cd Kali_GAME
python3 kali_game.py
```

Przy pierwszym labie buduje się obraz `kali-game-lab:0.1`.  
Tryb podglądu bez zapisu postępu:
```bash
python3 kali_game.py --check
python3 kali_game.py --test-mode
```

Docker bez członkostwa w grupie:
```bash
KALI_GAME_DOCKER_SUDO=1 python3 kali_game.py --check
KALI_GAME_DOCKER_SUDO=1 python3 kali_game.py --test-mode
KALI_GAME_DOCKER_SUDO=1 python3 kali_game.py
```

---

## 📋 POZIOMY I MISJE / LEVELS & MISSIONS

| Poziom / Level | Temat / Topic | Narzędzia / Tools |
|---|---|---|
| 0 | Granice labu, uprawnienia | `ls`, `chmod`, `whoami` |
| 1 | Nazwy ze spacjami, kody wyjścia | `find`, `echo`, `exit` |
| 2 | Procesy, właściciele, pakiety | `ps`, `dpkg`, `stat` |
| 3 | Listenery, DNS TTL, transport | `ss`, `ip`, `netstat` |
| 4 | Unikalne wartości, walidacja CSV | `cut`, `awk`, `sort` |
| 5 | Konfiguracja vs baseline, alerty | `diff`, `grep`, `sed` |
| 6 | Atrybuty cookie, remediacja | `curl`, `file` |
| 7 | Oś czasu, raportowanie | `strings`, `xxd`, `sha256sum` |
| 8 | Typy, sumy, metadanea, YARA | `file`, `exiftool`, `yara`, `jq` |
| 9 | Nmap na loopback | `nmap 127.0.0.1` |
| 10 | PCAP offline | `tshark -r`, `tcpdump -r` |
| 11 | Aplikacja HTTP lokalna | `whatweb`, `curl` |
| 12 | Triage, integralność, oś czasu | `yara`, `sha256sum`, `stat` |

**Razem: 82 misje, 13 poziomów, 100% syntetyczne dane.**  
**Total: 82 missions, 13 levels, 100% synthetic data.**

---

## 🤝 DOŁĄCZ DO SPOŁECZNOŚCI / COMMUNITY CALL

**PL:**  
Chcesz dodać własną grę, poziom lub misję? Ten projekt jest otwarty na wkład społeczności!

1. Fork repozytorium
2. Dodaj nowy poziom w `content.py` (lub nowy plik z misjami)
3. Użyj syntetycznych danych — żadnych prawdziwych celów, haseł ani kluczy
4. Uruchom testy: `python3 -m unittest discover -s tests -v`
5. Otwórz Pull Request z opisem: co dodałeś, jak się gra, jakie narzędzia ćwiczy

**EN:**  
Want to add your own game, level, or mission? This project is open to community contributions!

1. Fork the repository
2. Add a new level in `content.py` (or a new missions file)
3. Use synthetic data only — no real targets, passwords, or keys
4. Run tests: `python3 -m unittest discover -s tests -v`
5. Open a Pull Request describing: what you added, how to play, which tools it trains

### Szablon misji / Mission Template (Python)
```python
{
    "id": "l13-m1",
    "title": "Nazwa misji / Mission title",
    "level": 13,
    "goal": "Co gracz musi zrobić / What the player must do",
    "hint": "Stopniowa podpowiedź / Graduated hint",
    "tools": ["grep", "find"],
    "check": lambda ctx: True,  # walidacja odpowiedzi / answer validation
    "synthetic": True           # MUST be True — no real data
}
```

Każdy współtwórca pojawia się w sekcji **Contributors** i otrzymuje rolę **🛡️ Game Builder**.  
Every contributor appears in the **Contributors** section and gets the **🛡️ Game Builder** role.

---

## 🏗️ ARCHITEKTURA / ARCHITECTURE

```
kali_game.py      → punkt startowy / entry point
runtime.py        → argumenty, tmux, środowisko
game.py           → menu, przebieg misji
lab_manager.py    → kontenery Docker, panele terminala
content.py        → 82 misje, 13 poziomów
command_guide.py  → karty komend (find, grep, curl, chmod...)
mentor.py         → integracja OpenRouter (nemotron-3.5-super-vl:free)
progress.py       → lokalny zapis postępu (~/.local/share/Kali_GAME/)
config.py         → ścieżki, ID wersji
lab/              → Dockerfile, init_lab.py, local_web.py
tests/            → testy jednostkowe
```

---

## 🔒 BEZPIECZEŃSTWO / SECURITY

- Wszystkie misje działają w kontenerze bez sieci hosta  
- Kontener działa jako nie-root, tylko tymczasowa przestrzeń  
- Żadne dane z hosta nie są montowane do labu  
- Mentor (OpenRouter) nie zapisuje kluczy ani odpowiedzi na dysku
- Chcesz zmienić dostawce API oraz model (plik ./mentor.py "MODEL", "ENDPOINT")  
- Tryb `--test-mode` nie zmienia zapisu postępu  

- All missions run in a container without host network  
- Container runs as non-root, temporary workspace only  
- No host data is mounted into the lab  
- Mentor (OpenRouter) does not save keys or answers to disk
- Want to change API distribution (file ./mentor.py "MODEL", "ENDPOINT")  
- `--test-mode` does not modify progress  

---

## 🗺️ ROADMAP

- [ ] v0.2 — nowy poziom sieci web (SQLi, XSS syntetyczne)  
- [ ] v0.3 — tryb rywalizacji (leaderboard lokalny)  
- [ ] v0.4 — wsparcie dla własnych obrazów labu od społeczności  
- [ ] v1.0 — stabilna wersja z 100+ misjami  

- [ ] v0.2 — new web level (synthetic SQLi, XSS)  
- [ ] v0.3 — competition mode (local leaderboard)  
- [ ] v0.4 — support for community lab images  
- [ ] v1.0 — stable version with 100+ missions  

---

## 📄 LICENCJA / LICENSE

MIT License. Zobacz plik `LICENSE`.  
MIT License. See `LICENSE` file.

---

## 👨‍💻 AUTOR / AUTHOR

**odo-nvidia** — founder  
GitHub: [github.com/odo-nvidia](https://github.com/odo-nvidia)

---

## ⭐ WSPIERJ PROJEKT / SUPPORT THE PROJECT

Jeśli gra się podoba — daj gwiazdkę ⭐, fork repo i dodaj własny poziom!  
If you like the game — star ⭐, fork the repo and add your own level!

```text
   ⭐  Star this repo   🍴  Fork it   🛡️  Build a game
```

---

## 📣 SHARE / UDOSTĘPNIJ

**PL:** Udostępniaj wiedzę! Wrzuć zrzut ekranu z gry i oznacz `#KaliGame #CyberSecurity #KaliLinux #PolishHackers`  
**EN:** Share the knowledge! Post a screenshot and tag `#KaliGame #CyberSecurity #KaliLinux #PolishHackers`

Gotowy tweet / Ready-to-tweet:
> Just built a terminal game to learn Kali Linux with 82 missions on 13 levels. 🛡️ Docker + tmux + synthetic labs. Open for community contributions! #KaliGame #CyberSec #OpenSource
