import re
from typing import List

BULLET_GLYPHS = {
    '•', '●', '○', '■', '▪', '▫', '◆', '◇', '➢', '➤', '★', '☆', '–', '—', '*', '-'
}

BULLET_START_REGEX = re.compile(
    r'^[\s\t]*(?:[•●○■▪▫◆◇➢➤★☆–—*-]|\u2022|\u25cf|\u25cb|\u25aa|\ufffd|\d+\.|\([0-9a-zA-Z]\))\s+'
)

def is_bullet_start(line: str, prev_indent: float = 0.0, current_indent: float = 0.0) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if BULLET_START_REGEX.match(line):
        return True
    if stripped[0] in BULLET_GLYPHS and len(stripped) > 1 and stripped[1] in ' \t':
        return True
    return False


def strip_bullet_glyph(line: str) -> str:
    cleaned = BULLET_START_REGEX.sub('', line.strip())
    cleaned = re.sub(r'^[•●○■▪▫◆◇➢➤★☆–—*\ufffd\s\t-]+\s*', '', cleaned)
    return cleaned.strip()


def rejoin_hyphenation(prev_line: str, next_line: str) -> str:
    if prev_line.endswith('-'):
        # If prev_line ends with hyphen and next line starts with a word, rejoin directly
        return f"{prev_line}{next_line}"
    return f"{prev_line} {next_line}"


def rebuild_bullet_list(raw_lines: List[str]) -> List[str]:
    bullets: List[str] = []
    current_bullet: str = ""

    for line in raw_lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        if is_bullet_start(clean_line):
            if current_bullet:
                bullets.append(current_bullet.strip())
            current_bullet = strip_bullet_glyph(clean_line)
        else:
            if current_bullet:
                current_bullet = rejoin_hyphenation(current_bullet, clean_line)
            else:
                current_bullet = clean_line

    if current_bullet:
        bullets.append(current_bullet.strip())

    return bullets
