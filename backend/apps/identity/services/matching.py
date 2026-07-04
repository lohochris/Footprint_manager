import re
from decimal import Decimal


def normalize_email(email: str) -> str:
    """Normalize email: strip, lowercase, and clean standard providers' sub-addresses/dots."""
    if not email:
        return ""
    email = email.strip().lower()
    if "@" not in email:
        return email

    local_part, domain = email.rsplit("@", 1)

    # Clean standard providers (gmail.com, googlemail.com)
    if domain in ("gmail.com", "googlemail.com"):
        # Strip sub-address (e.g. user+suffix -> user)
        local_part = local_part.split("+")[0]
        # Strip dots
        local_part = local_part.replace(".", "")
        domain = "gmail.com"

    return f"{local_part}@{domain}"


def normalize_phone(phone: str) -> str:
    """Normalize phone number to digits only, preserving leading plus for E.164."""
    if not phone:
        return ""
    phone = phone.strip()
    has_plus = phone.startswith("+")
    digits = re.sub(r"\D", "", phone)
    return f"+{digits}" if has_plus else digits


def normalize_username(username: str) -> str:
    """Normalize username: lowercase, strip @ character and outer spaces."""
    if not username:
        return ""
    username = username.strip().lower()
    if username.startswith("@"):
        username = username[1:]
    return username


def normalize_domain(domain: str) -> str:
    """Normalize domain: extract FQDN, lowercase, strip leading www."""
    if not domain:
        return ""
    domain = domain.strip().lower()
    # Remove protocol prefix if exists
    domain = re.sub(r"^https?://", "", domain)
    # Remove path, query params, etc.
    domain = domain.split("/")[0]
    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def normalize_text(text: str) -> str:
    """General text normalization: lowercase, strip, condense whitespaces."""
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def levenshtein_similarity(s1: str, s2: str) -> Decimal:
    """Calculate normalized Levenshtein similarity between two strings."""
    if not s1 or not s2:
        return Decimal("0.000")
    if s1 == s2:
        return Decimal("1.000")
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )
    max_len = max(m, n)
    score = 1.0 - (dp[m][n] / max_len)
    return Decimal(str(round(score, 3)))


def jaro_similarity(s1: str, s2: str) -> float:
    """Helper to calculate Jaro similarity."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(len2, i + match_distance + 1)
        for j in range(start, end):
            if not s2_matches[j] and s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(len1):
        if s1_matches[i]:
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
    transpositions //= 2
    return (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1, max_l: int = 4) -> Decimal:
    """Calculate Jaro-Winkler similarity between two strings."""
    j = jaro_similarity(s1, s2)
    if j < 0.7:
        return Decimal(str(round(j, 3)))
    prefix = 0
    for c1, c2 in zip(s1[:max_l], s2[:max_l], strict=False):
        if c1 == c2:
            prefix += 1
        else:
            break
    score = j + prefix * p * (1.0 - j)
    return Decimal(str(round(score, 3)))
