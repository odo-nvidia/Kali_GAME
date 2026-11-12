# Źródła i zasady projektowania misji

Sprawdzone 10 listopada 2026. Link do kursu nie oznacza zgody na kopiowanie jego zadań. Scenariusze, opisy i syntetyczne pliki v0.2-v0.4 zostały napisane od zera; z platform szkoleniowych wykorzystano wyłącznie ogólne pomysły pedagogiczne i strukturę ćwiczeń.

## Wzorce z oficjalnych platform

| Źródło | Wzorzec, który zaobserwowano | Jak zastosowano w v0.2 |
| --- | --- | --- |
| [HTB Academy: Linux Fundamentals](https://academy.hackthebox.com/course/preview/linux-fundamentals) | Kurs dzieli fundamenty na odrębne sekcje: shell, nawigacja, pliki, administracja, usługi i uprawnienia; sekcje zawierają ćwiczenia praktyczne, a moduł kończy się oceną umiejętności. | Poziomy w grze mają małe cele, ćwiczenia na syntetycznych plikach i lokalną walidację. Misje l0-m3 do l2-m5 sprawdzają myślenie o zakresie, ścieżkach, statusach, procesach i uprawnieniach własnymi przykładami. |
| [OverTheWire: Bandit, Level 0](https://overthewire.org/wargames/bandit/bandit0.html) | Strona oddziela cel poziomu od przydatnych poleceń i materiałów do czytania; wyzwanie jest częścią sekwencji poziomów. | Gra pokazuje cel każdej misji, daje stopniowane hinty i odblokowuje kolejne poziomy. Nie używa SSH do Bandit, jego danych logowania, plików ani konkretnych zadań. |
| [PortSwigger: Getting started](https://portswigger.net/web-security/getting-started) i [learning paths](https://portswigger.net/web-security/learning-paths) | Ścieżka łączy materiały do czytania, praktyczne laby i śledzenie postępów, pozwalając uczyć się we własnym tempie. | Każda misja ma własny debrief i zapis ukończenia. Poziomy webowe używają nowych tekstowych artefaktów, a nie kopii PortSwigger labs. |
| [TryHackMe: Linux Fundamentals Part 1](https://tryhackme.com/room/linuxfundamentalspart1) | Wyniki wyszukiwania wskazywały ćwiczenia na nawigację, `find` i `grep`, ale bezpośrednia strona pokoju pokazała checkpoint Vercel podczas tej weryfikacji. | Traktowano tylko jako trop do ogólnego wzorca „wprowadzenie → praca w terminalu”; nie korzystano z tekstów, flag ani rozwiązań tej misji. |
| [OWASP Web Security Testing Guide](https://github.com/OWASP/wstg) | Przewodnik porządkuje testowanie aplikacji w rozpoznawalne kategorie i procedury. Repozytorium deklaruje CC BY-SA 4.0. | W v0.2 nie skopiowano treści WSTG. Użyto ogólnej idei: misja webowa ma prowadzić od obserwacji do uzasadnionej rekomendacji; przyszła adaptacja wymaga attribution, oznaczenia zmian i zachowania ShareAlike. |

## Jak ułożono nowe misje

- Poziom 0: granice labu, najmniejsze uprawnienia, reset i integralność artefaktów.
- Poziom 1: nazwy ze spacjami, deduplikacja oraz kody zakończenia w powłoce.
- Poziom 2: czytanie raportu procesów, właścicieli/grup i wersji pakietów.
- Poziom 3: analiza przygotowanych tabel listenerów, DNS TTL i zestawienia transportu; brak rzeczywistego skanowania lub ruchu sieciowego.
- Poziom 4: analiza unikalnych wartości i walidacja wadliwego rekordu CSV.
- Poziom 5: porównanie konfiguracji z baseline i priorytetyzacja syntetycznych alertów.
- Poziom 6: przegląd atrybutów cookie oraz wybór defensywnej remediacji.
- Poziom 7: budowanie osi czasu i kompletność raportu z ćwiczeniowych artefaktów.
- Poziom 8: lokalny przegląd typów, sum, ciągów, metadanych i syntetycznych znaczników.
- Poziom 9: ograniczona inwentaryzacja Nmap wyłącznie na loopback kontenera.
- Poziom 10: analiza wygenerowanego PCAP przez `tshark` i `tcpdump -r`, bez przechwytywania ruchu na żywo.
- Poziom 11: przegląd syntetycznej aplikacji HTTP dostępnej tylko pod `127.0.0.1`.
- Poziom 12: defensywny triage, integralność dowodów, oś czasu i raportowanie.

## Narzędzia i materiały w v0.3/v0.4

Nowe poziomy wykorzystują `file`, `sha256sum`, `strings`, `xxd`, ExifTool, `jq`, YARA, Nmap, WhatWeb, `curl`, `tshark`, `tcpdump` i Scapy. Scapy generuje pliki PCAP lokalnie; `tshark` i `tcpdump` odczytują je z `-r`. Nmap jest ograniczony do `127.0.0.1` i portów 8080/8081. Żadne zadanie nie instruuje skanowania publicznych hostów ani przechwytywania ruchu hosta.

v0.4 dodaje autorskie karty do nawigacji, plików, filtrowania tekstu, uprawnień, procesów, lokalnej inspekcji sieci i sum kontrolnych. Karty obejmują m.in. `find`, `grep`, `pwd`, `cd`, `mkdir`, `touch`, `cp`, `mv`, `rm`, `file`, `stat`, `du`, `df`, `cut`, `awk`, `sed`, `chmod`, `ps`, `ip`, `ss`, `curl`, `sha256sum`, `diff` i `man`. Przykłady usuwania są oznaczone jako destrukcyjne, a przykłady HTTP wskazują wyłącznie lokalny serwer labu. Syntetyczne ćwiczenia `find`/`grep` są umieszczone na początku kampanii i nie powielają zadań z Bandit ani innych kursów.

Dokumentacja narzędzi do dalszej nauki:

- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [TShark manual](https://www.wireshark.org/docs/man-pages/tshark.html) i [Wireshark display filters](https://www.wireshark.org/docs/dfref/)
- [Scapy usage](https://scapy.readthedocs.io/en/latest/usage.html)
- [YARA documentation](https://yara.readthedocs.io/en/stable/)
- [ExifTool](https://exiftool.org/)
- [WhatWeb](https://github.com/urbanadventurer/WhatWeb)
- [GNU findutils manual](https://www.gnu.org/software/findutils/manual/html_mono/find.html)
- [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html)
- [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/)
- [GNU Awk manual](https://www.gnu.org/software/gawk/manual/)
- [GNU sed manual](https://www.gnu.org/software/sed/manual/)

Misje są oryginalnymi scenariuszami, a nie kopiami przykładów z dokumentacji. Narzędzia są instalowane w osobnym obrazie Debiana; host Kali pozostaje bez zmian.

## Wykorzystanie materiałów i licencje

- [OWASP WSTG: licencja](https://github.com/OWASP/wstg/blob/master/LICENSE) — CC BY-SA 4.0; ewentualna przyszła adaptacja wymaga spełnienia warunków licencji i sprawdzenia materiałów zewnętrznych.
- [OWASP Juice Shop: licencja MIT](https://github.com/juice-shop/juice-shop/blob/master/LICENSE) — może być kandydatem na późniejszy lokalny cel labowy, z zachowaniem wymaganych notice; nie jest dodany do v0.4.
- [OverTheWire: Rules](https://overthewire.org/rules/) — oficjalne reguły zastrzegają prawa do zadań, konfiguracji i materiałów oraz zakazują reuse / redystrybucji bez pisemnej zgody.
- [TryHackMe: Terms of Use](https://tryhackme.com/legal/terms-of-use) — treści są zastrzeżone, a warunki ograniczają automatyczne pozyskiwanie / scraping.
- [PortSwigger: Website Terms](https://portswigger.net/web-security/certification/terms-and-conditions/website-terms-of-use) — prawa do materiałów witryny są zastrzeżone; Academy może służyć jako link do dalszej nauki.
- [Kali Linux Documentation](https://www.kali.org/docs/) i [Docker Debian install](https://docs.docker.com/engine/install/debian/) — oficjalna dokumentacja referencyjna; w grze nie osadzono jej pełnych tekstów.

Darmowy dostęp, prywatny użytek ani samo podanie autora nie zastępują licencji lub zgody. Pakiet może linkować do źródeł; treść włączamy lokalnie tylko wtedy, gdy jej licencja na to pozwala.
