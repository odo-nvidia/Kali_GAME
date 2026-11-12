"""Short Polish reference cards for commands used in the early course."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandCard:
    name: str
    purpose: str
    syntax: str
    options: tuple[tuple[str, str], ...]
    examples: tuple[str, ...]
    notes: tuple[str, ...] = ()


COMMAND_CARDS = (
    CommandCard(
        "find",
        "Wyszukuje pliki i katalogi według właściwości.",
        "find KATALOG [WARUNKI] [AKCJA]",
        (
            (".", "bieżący katalog jako punkt startowy"),
            ("-type f", "tylko zwykłe pliki; -type d wybiera katalogi"),
            ("-name 'WZORZEC'", "nazwa z globem, z rozróżnianiem wielkości liter"),
            ("-iname 'WZORZEC'", "nazwa bez rozróżniania wielkości liter"),
            ("-size 20c", "dokładnie 20 bajtów; c oznacza bajty"),
            ("-size +20c / -size -20c", "odpowiednio więcej / mniej niż 20 bajtów"),
            ("-maxdepth 2", "ogranicza głębokość przeszukiwania"),
            ("-print", "wypisuje znalezioną ścieżkę; to domyślna akcja"),
            ("-exec KOMENDA {} +", "uruchamia komendę dla znalezionych plików"),
        ),
        (
            "find . -type f -name '*.txt' -print",
            "find . -type f -size +100c -print",
            "find . -type f -name '*.log' -exec grep -n 'FAILED' {} +",
        ),
        (
            "Cudzysłowy chronią wzorzec *.txt przed rozwinięciem przez powłokę.",
            "Opcja -type f wyklucza katalog o nazwie pasującej do wzorca.",
            "Podawaj bezpieczny katalog startowy, np. . w labie.",
        ),
    ),
    CommandCard(
        "grep",
        "Wyszukuje pasujące wiersze w plikach lub katalogach.",
        "grep [OPCJE] 'TEKST_LUB_WZORZEC' PLIK_LUB_KATALOG",
        (
            ("-n", "dodaje numer wiersza"),
            ("-i", "ignoruje wielkość liter"),
            ("-r", "przeszukuje katalogi rekurencyjnie"),
            ("-l", "wypisuje tylko nazwy plików z dopasowaniem"),
            ("-c", "liczy pasujące wiersze w każdym pliku"),
            ("-F", "traktuje wzorzec jako zwykły tekst, nie wyrażenie regularne"),
            ("-E", "włącza rozszerzone wyrażenia regularne"),
            ("-w", "dopasowuje całe słowo"),
            ("-x", "wymaga dopasowania całego wiersza"),
            ("-v", "wypisuje wiersze, które nie pasują"),
            ("-A N / -B N / -C N", "pokazuje N wierszy po / przed / wokół dopasowania"),
        ),
        (
            "grep -n -F 'STATE=review' logs/review.log",
            "grep -ril 'maintenance window' reports/",
            "grep -n '^status=review$' audit.txt",
        ),
        (
            "grep -c liczy pasujące wiersze, nie liczbę wystąpień tekstu w wierszu.",
            "W wyrażeniu regularnym ^ oznacza początek, a $ koniec wiersza.",
        ),
    ),
    CommandCard(
        "ls",
        "Wyświetla zawartość katalogu.",
        "ls [OPCJE] [KATALOG]",
        (("-l", "szczegóły, m.in. uprawnienia i rozmiar"), ("-a", "także nazwy ukryte, zaczynające się kropką"), ("-h", "czytelne jednostki rozmiaru; zwykle z -l")),
        ("ls -la", "ls -lh notes/"),
    ),
    CommandCard(
        "cat",
        "Wyświetla zawartość pliku; przy długich plikach wygodniejszy jest less.",
        "cat PLIK",
        (("-n", "dodaje numery wierszy"),),
        ("cat notes/start.txt", "cat -n logs/review.log"),
    ),
    CommandCard(
        "less",
        "Pozwala wygodnie przeglądać długi plik.",
        "less PLIK",
        (("/tekst", "wyszukuje tekst po otwarciu; n przechodzi do następnego wyniku"), ("q", "zamyka przeglądarkę pliku")),
        ("less /var/log/auth.log",),
    ),
    CommandCard(
        "head / tail",
        "Pokazują początek lub koniec pliku.",
        "head -n LICZBA PLIK    |    tail -n LICZBA PLIK",
        (("-n N", "wyświetla N wierszy"), ("tail -f", "śledzi dopisywane wiersze; używaj tylko w świadomym, lokalnym labie")),
        ("head -n 5 notes/start.txt", "tail -n 10 logs/review.log"),
    ),
    CommandCard(
        "wc",
        "Liczy wiersze, słowa lub bajty.",
        "wc [OPCJA] PLIK    albo    KOMENDA | wc [OPCJA]",
        (("-l", "wiersze"), ("-w", "słowa"), ("-c", "bajty")),
        ("find . -type f -name '*.txt' | wc -l", "wc -c records/size-proof.bin"),
        ("Przy potoku końcowe wc -l policzy wiersze przekazane przez poprzednią komendę."),
    ),
    CommandCard(
        "sort / uniq",
        "Sortują dane i pomagają usuwać lub liczyć sąsiadujące duplikaty.",
        "sort PLIK | uniq [OPCJE]",
        (("sort -u", "sortuje i zostawia unikalne wiersze"), ("uniq -c", "zlicza sąsiadujące identyczne wiersze")),
        ("sort names.txt | uniq", "sort names.txt | uniq -c"),
        ("uniq porównuje sąsiadujące wiersze, dlatego zwykle poprzedź je sort."),
    ),
    CommandCard(
        "pwd / cd",
        "Pokazują bieżące miejsce i zmieniają katalog roboczy.",
        "pwd    |    cd KATALOG",
        (
            ("cd ..", "przechodzi do katalogu nadrzędnego"),
            ("cd ~", "przechodzi do katalogu domowego"),
            ("cd -", "wraca do poprzedniego katalogu"),
        ),
        ("pwd", "cd ../reports", "cd -"),
        ("cd jest poleceniem wbudowanym powłoki; zmienia katalog tej powłoki."),
    ),
    CommandCard(
        "mkdir / touch",
        "Tworzą katalogi i pliki do ćwiczeń.",
        "mkdir [OPCJE] KATALOG    |    touch PLIK",
        (
            ("mkdir -p", "tworzy też brakujące katalogi nadrzędne"),
            ("touch", "tworzy pusty plik albo aktualizuje czas istniejącego pliku"),
        ),
        ("mkdir -p work/notes", "touch work/notes/todo.txt"),
    ),
    CommandCard(
        "cp / mv / rm",
        "Kopiują, przenoszą i usuwają pliki w katalogu ćwiczenia.",
        "cp ŹRÓDŁO CEL    |    mv ŹRÓDŁO CEL    |    rm PLIK",
        (
            ("-i", "pyta przed nadpisaniem lub usunięciem"),
            ("cp -r", "kopiuje katalog wraz z zawartością"),
            ("rm -r", "usuwa katalog wraz z zawartością"),
        ),
        ("cp -i notes/a.txt notes/a.copy.txt", "mv -i notes/a.copy.txt archive/", "rm -i archive/a.copy.txt"),
        (
            "rm usuwa bez kosza; sprawdź ścieżkę przed zatwierdzeniem.",
            "Ćwicz tylko w labie. Nie używaj rm -rf ani nie usuwaj plików systemowych.",
        ),
    ),
    CommandCard(
        "file / stat",
        "Rozpoznają typ pliku i pokazują jego metadane.",
        "file PLIK    |    stat [OPCJE] PLIK",
        (
            ("file", "szacuje format na podstawie zawartości, nie tylko rozszerzenia"),
            ("stat -c FORMAT", "wybiera pola wyjściowe; %n to nazwa, %s to rozmiar w bajtach"),
        ),
        ("file evidence/readme.bin", "stat -c '%n %s bytes' evidence/readme.bin"),
        ("Wynik file nie gwarantuje, że plik jest bezpieczny."),
    ),
    CommandCard(
        "du / df",
        "Sprawdzają zajętość katalogu albo wolne miejsce systemu plików.",
        "du [OPCJE] KATALOG    |    df [OPCJE] ŚCIEŻKA",
        (
            ("du -s", "pokazuje łączny rozmiar zamiast każdego elementu"),
            ("-h", "używa czytelnych jednostek, np. KiB i MiB"),
            ("df", "pokazuje miejsce na systemie plików zawierającym ścieżkę"),
        ),
        ("du -sh reports/", "df -h ."),
    ),
    CommandCard(
        "cut",
        "Wyciąga wybrane pola z prostych wierszy tekstowych.",
        "cut -dSEPARATOR -fNUMERY PLIK",
        (
            ("-d,", "ustawia przecinek jako separator pól"),
            ("-f 1,3", "wybiera pola o numerach 1 i 3"),
            ("-c 1-8", "wybiera zakres pozycji znaków"),
        ),
        ("cut -d, -f2 data/inventory.csv", "cut -d: -f1 data/simple-list.txt"),
        ("cut nie obsługuje pełnego formatu CSV z polami cytowanymi i przecinkami w środku."),
    ),
    CommandCard(
        "awk",
        "Przetwarza wiersze tekstu i wybiera wskazane kolumny.",
        "awk [OPCJE] 'WARUNEK { AKCJA }' PLIK",
        (
            ("-F,", "ustawia przecinek jako separator pól"),
            ("NR", "numer bieżącego wiersza"),
            ("$1, $2, $NF", "pierwsze, drugie i ostatnie pole wiersza"),
        ),
        ("awk -F, 'NR > 1 { print $2 }' data/inventory.csv",),
        ("Ten prosty przykład zakłada pola rozdzielone przecinkami bez cytowanych przecinków."),
    ),
    CommandCard(
        "sed",
        "Wybiera wiersze albo wykonuje podmiany tekstu w wyjściu.",
        "sed [OPCJE] 'WYRAŻENIE' PLIK",
        (
            ("-n", "domyślnie nie wypisuje wierszy; pokaż tylko wybrane"),
            ("s/stare/nowe/g", "podmienia wszystkie dopasowania w każdym wierszu"),
            ("-i", "edytuje plik w miejscu zamiast tylko pokazać wynik"),
        ),
        ("sed -n '2,4p' notes/start.txt", "sed 's/INFO/REVIEW/g' logs/sample.log"),
        ("Najpierw sprawdź wynik bez -i; edycja w miejscu może nadpisać dane."),
    ),
    CommandCard(
        "chmod",
        "Zmienia uprawnienia pliku.",
        "chmod TRYB PLIK",
        (
            ("u+x", "dodaje właścicielowi prawo uruchamiania"),
            ("640", "właściciel: odczyt/zapis; grupa: odczyt; inni: brak"),
            ("r=4, w=2, x=1", "wartości sumuje się osobno dla właściciela, grupy i innych"),
        ),
        ("chmod u+x scripts/check.sh", "chmod 640 notes/private.txt"),
        ("Zmieniaj tylko uprawnienia plików w labie; unikaj chmod 777."),
    ),
    CommandCard(
        "whoami / id",
        "Pokazują bieżącego użytkownika i jego identyfikatory grup.",
        "whoami    |    id [OPCJE]",
        (
            ("id -u", "numeryczny identyfikator użytkownika"),
            ("id -G", "numeryczne identyfikatory grup"),
            ("id -nG", "nazwy grup bieżącego użytkownika"),
        ),
        ("whoami", "id", "id -nG"),
    ),
    CommandCard(
        "ps / pgrep",
        "Pokazują procesy działające w systemie.",
        "ps [OPCJE]    |    pgrep [OPCJE] WZORZEC",
        (
            ("ps -ef", "pełna lista procesów w formacie System V"),
            ("pgrep -a", "szuka procesu po nazwie i pokazuje pełny wiersz polecenia"),
            ("pgrep -u USER", "ogranicza wynik do wskazanego użytkownika"),
        ),
        ("ps -ef", "pgrep -a python3"),
        ("To migawka procesów, nie pełna historia ich działania."),
    ),
    CommandCard(
        "ip / ss",
        "Pokazują lokalną konfigurację sieci i gniazda nasłuchujące.",
        "ip [OBIEKT]    |    ss [OPCJE]",
        (
            ("ip -brief addr", "krótka lista interfejsów i adresów"),
            ("ip route", "lokalna tabela tras"),
            ("ss -lnt", "nasłuchujące gniazda TCP w postaci numerycznej"),
            ("ss -lun", "nasłuchujące gniazda UDP w postaci numerycznej"),
        ),
        ("ip -brief addr", "ip route", "ss -lnt"),
        ("Używaj do inspekcji własnego labu; to nie jest polecenie do skanowania celów."),
    ),
    CommandCard(
        "curl",
        "Wysyła żądanie HTTP i odczytuje odpowiedź wskazanego serwera.",
        "curl [OPCJE] URL",
        (
            ("-s", "ogranicza komunikaty postępu"),
            ("-I", "pobiera same nagłówki odpowiedzi"),
            ("-o PLIK", "zapisuje treść odpowiedzi do pliku"),
            ("-w FORMAT", "wypisuje wskazane metadane, np. kod HTTP"),
        ),
        ("curl -sI http://127.0.0.1:8080/", "curl -s http://127.0.0.1:8080/status.json"),
        ("W tej grze używaj wyłącznie adresu lokalnego wskazanego w misji."),
    ),
    CommandCard(
        "sha256sum",
        "Oblicza lub sprawdza sumę SHA-256 pliku.",
        "sha256sum PLIK    |    sha256sum -c MANIFEST",
        (("-c", "sprawdza pliki względem zapisanych sum w manifeście"),),
        ("sha256sum evidence/policy.txt", "sha256sum -c evidence/SHA256SUMS"),
        ("Zgodna suma potwierdza zgodność bajtów z manifestem, nie zaufanie do źródła."),
    ),
    CommandCard(
        "diff",
        "Pokazuje różnice między dwoma plikami tekstowymi.",
        "diff [OPCJE] PLIK1 PLIK2",
        (
            ("-u", "czytelny kontekstowy format unified diff"),
            ("-q", "informuje tylko, czy pliki się różnią"),
        ),
        ("diff -u config/current.txt config/baseline.txt",),
        ("Kod zakończenia 1 zwykle oznacza znalezione różnice; kod 2 sygnalizuje błąd."),
    ),
    CommandCard(
        "man / --help",
        "Pomagają sprawdzić opcje polecenia i lokalną dokumentację.",
        "man KOMENDA    |    KOMENDA --help",
        (
            ("/TEKST", "szuka tekstu w otwartej stronie man"),
            ("n", "przechodzi do kolejnego wyniku wyszukiwania"),
            ("q", "zamyka stronę man"),
            ("--help", "często pokazuje krótką listę opcji"),
        ),
        ("man grep", "find --help"),
        ("Dokumentacja może różnić się między wersjami; sprawdź wersję zainstalowanego narzędzia."),
    ),
)


def command_cards(names: tuple[str, ...] | None = None) -> tuple[CommandCard, ...]:
    """Return all cards or just the requested command cards, in course order."""
    if names is None:
        return COMMAND_CARDS
    wanted = set(names)
    return tuple(
        card
        for card in COMMAND_CARDS
        if card.name in wanted or set(part.strip() for part in card.name.split("/")) & wanted
    )
