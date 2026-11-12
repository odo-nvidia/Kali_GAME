"""Explicit, one-request-at-a-time OpenRouter mentor integration."""

import json
import re
import urllib.error
import urllib.request


MODEL = "nvidia/nemotron-3.5-super-vl:free"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)\S+"),
    re.compile(r"(?i)((?:password|passwd|token|secret|api[_-]?key)\s*[:=]\s*)\S+"),
)


def redact_context(text: str) -> str:
    """Remove common credential patterns; this is not a guarantee of secrecy."""
    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(r"\1[REDACTED]", redacted)
    return redacted[-6000:]


def build_user_message(mission, question: str, terminal_snapshot: str) -> str:
    context = redact_context(terminal_snapshot)
    return (
        f"Misja: {mission.title}\nCel: {mission.goal}\n"
        f"Zadanie: {mission.task}\n"
        f"Narzędzia: {', '.join(mission.tools) or '(standardowe narzędzia powłoki)'}\n"
        f"Pytanie gracza: {question.strip() or '(brak)'}\n"
        f"Wybrany kontekst terminala:\n{context or '(gracz nie dołączył fragmentu terminala)'}"
    )


def ask_mentor(api_key: str, mission, question: str, terminal_snapshot: str, model: str = MODEL) -> str:
    user_message = build_user_message(mission, question, terminal_snapshot)
    body = json.dumps(
        {
            "model": model,
            "temperature": 0.2,
            "max_tokens": 450,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Jesteś polskojęzycznym mentorem w lokalnym, autoryzowanym labie edukacyjnym. "
                        "Ucz myślenia: najpierw zadaj krótkie pytanie o dowody i hipotezę, potem podaj "
                        "jedną stopniowaną wskazówkę. Nie ujawniaj od razu odpowiedzi ani gotowego "
                        "rozwiązania, chyba że gracz wyraźnie o nie prosi. Nie wykonuj poleceń i nie "
                        "sugeruj testowania systemów poza tym labem. Nazwy komend i narzędzi zostaw po angielsku."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(800).decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter zwrócił HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Nie udało się połączyć z OpenRouter: {exc}") from exc

    try:
        return payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise RuntimeError("OpenRouter zwrócił odpowiedź w nierozpoznanym formacie.") from exc
