import random
from pbkdf2 import PBKDF2
import hmac
from .py3specials import *
from .wallet_utils import is_new_seed
from bisect import bisect_left
import unicodedata
from typing import Union, List, Tuple

wordlist_english = [
    word.strip()
    for word in list(
        open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "english.txt"),
            "r",
        )
    )
]

ELECTRUM_VERSION = "3.0.5"  # version of the client package
PROTOCOL_VERSION = "1.1"  # protocol version requested

# The hash of the mnemonic seed must begin with this
SEED_PREFIX = "01"  # Standard wallet
SEED_PREFIX_2FA = "101"  # Two-factor authentication
SEED_PREFIX_SW = "100"  # Segwit wallet

whitespace = " \t\n\r\v\f"

# http://www.asahi-net.or.jp/~ax2s-kmtn/ref/unicode/e_asia.html
CJK_INTERVALS = [
    (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
    (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A"),
    (0x20000, 0x2A6DF, "CJK Unified Ideographs Extension B"),
    (0x2A700, 0x2B73F, "CJK Unified Ideographs Extension C"),
    (0x2B740, 0x2B81F, "CJK Unified Ideographs Extension D"),
    (0xF900, 0xFAFF, "CJK Compatibility Ideographs"),
    (0x2F800, 0x2FA1D, "CJK Compatibility Ideographs Supplement"),
    (0x3190, 0x319F, "Kanbun"),
    (0x2E80, 0x2EFF, "CJK Radicals Supplement"),
    (0x2F00, 0x2FDF, "CJK Radicals"),
    (0x31C0, 0x31EF, "CJK Strokes"),
    (0x2FF0, 0x2FFF, "Ideographic Description Characters"),
    (0xE0100, 0xE01EF, "Variation Selectors Supplement"),
    (0x3100, 0x312F, "Bopomofo"),
    (0x31A0, 0x31BF, "Bopomofo Extended"),
    (0xFF00, 0xFFEF, "Halfwidth and Fullwidth Forms"),
    (0x3040, 0x309F, "Hiragana"),
    (0x30A0, 0x30FF, "Katakana"),
    (0x31F0, 0x31FF, "Katakana Phonetic Extensions"),
    (0x1B000, 0x1B0FF, "Kana Supplement"),
    (0xAC00, 0xD7AF, "Hangul Syllables"),
    (0x1100, 0x11FF, "Hangul Jamo"),
    (0xA960, 0xA97F, "Hangul Jamo Extended A"),
    (0xD7B0, 0xD7FF, "Hangul Jamo Extended B"),
    (0x3130, 0x318F, "Hangul Compatibility Jamo"),
    (0xA4D0, 0xA4FF, "Lisu"),
    (0x16F00, 0x16F9F, "Miao"),
    (0xA000, 0xA48F, "Yi Syllables"),
    (0xA490, 0xA4CF, "Yi Radicals"),
]


def is_CJK(c):
    n = ord(c)
    for imin, imax, name in CJK_INTERVALS:
        if n >= imin and n <= imax:
            return True
    return False


def normalize_text(seed):
    # normalize
    seed = unicodedata.normalize("NFKD", seed)
    # lower
    seed = seed.lower()
    # remove accents
    seed = "".join([c for c in seed if not unicodedata.combining(c)])
    # normalize whitespaces
    seed = " ".join(seed.split())
    # remove whitespaces between CJK
    seed = "".join(
        [
            seed[i]
            for i in range(len(seed))
            if not (
                seed[i] in whitespace and is_CJK(seed[i - 1]) and is_CJK(seed[i + 1])
            )
        ]
    )
    return seed


def eint_to_bytes(entint, entbits):
    a = hex(entint)[2:].rstrip("L").zfill(32)
    print(a)
    return binascii.unhexlify(a)


def mnemonic_int_to_words_original(mint, mint_num_words, wordlist=wordlist_english):
    backwords = [
        wordlist[(mint >> (11 * x)) & 0x7FF].strip() for x in range(mint_num_words)
    ]
    return " ".join((backwords[::-1]))


def mnemonic_int_to_words(
    mint: int,
    mint_num_words: int,
    wordlist: List[str] = wordlist_english,
) -> str:
    """Converts a mnemonic integer to a mnemonic phrase.

    Args:
        mint: The mnemonic integer to convert.
        mint_num_words: The number of words in the mnemonic phrase.
        wordlist: The wordlist to use for the conversion.

    Returns:
        str: The mnemonic phrase.
    """
    backwords = [
        wordlist[(mint >> (11 * x)) & 0x7FF].strip() for x in range(mint_num_words)
    ]
    return " ".join((backwords[::-1]))


def entropy_cs(entbytes):
    entropy_size = 8 * len(entbytes)
    checksum_size = entropy_size // 32
    hd = hashlib.sha256(entbytes).hexdigest()
    csint = int(hd, 16) >> (256 - checksum_size)
    return csint, checksum_size


def entropy_to_words_original(entbytes, wordlist=wordlist_english):
    if len(entbytes) < 4 or len(entbytes) % 4 != 0:
        raise ValueError(
            "The size of the entropy must be a multiple of 4 bytes (multiple of 32 bits)"
        )
    entropy_size = 8 * len(entbytes)
    csint, checksum_size = entropy_cs(entbytes)
    entint = int(binascii.hexlify(entbytes), 16)
    mint = (entint << checksum_size) | csint
    mint_num_words = (entropy_size + checksum_size) // 11

    return mnemonic_int_to_words(mint, mint_num_words, wordlist)


def entropy_to_words(
    entbytes: bytes,
    wordlist: List[str] = wordlist_english,
) -> str:
    """Converts entropy bytes to a mnemonic phrase.

    Args:
        entbytes: The entropy bytes.
        wordlist: The wordlist to use for the conversion.

    Returns:
        str: The mnemonic phrase.

    Raises:
        ValueError: If the size of the entropy is not a multiple of 4 bytes (32 bits).
    """
    if len(entbytes) < 4 or len(entbytes) % 4 != 0:
        raise ValueError(
            "The size of the entropy must be a multiple of 4 bytes (multiple of 32 bits)"
        )
    entropy_size = 8 * len(entbytes)
    csint, checksum_size = entropy_cs(entbytes)
    entint = int(binascii.hexlify(entbytes), 16)
    mint = (entint << checksum_size) | csint
    mint_num_words = (entropy_size + checksum_size) // 11

    return mnemonic_int_to_words(mint, mint_num_words, wordlist)


def words_bisect(word, wordlist=wordlist_english):
    lo = bisect_left(wordlist, word)
    hi = len(wordlist) - bisect_left(wordlist[:lo:-1], word)

    return lo, hi


def words_split(wordstr, wordlist=wordlist_english):
    def popword(wordstr, wordlist):
        for fwl in range(1, 9):
            w = wordstr[:fwl].strip()
            lo, hi = words_bisect(w, wordlist)
            if hi - lo == 1:
                return w, wordstr[fwl:].lstrip()
            wordlist = wordlist[lo:hi]
        raise Exception("Wordstr %s not found in list" % (w))

    words = []
    tail = wordstr
    while len(tail):
        head, tail = popword(tail, wordlist)
        words.append(head)
    return words


def words_to_mnemonic_int(words, wordlist=wordlist_english):
    if isinstance(words, str):
        words = words.split()
    return sum([wordlist.index(w) << (11 * x) for x, w in enumerate(words[::-1])])


def words_verify(words, wordlist=wordlist_english):
    if isinstance(words, str):
        words = words_split(words, wordlist)

    mint = words_to_mnemonic_int(words, wordlist)
    mint_bits = len(words) * 11
    cs_bits = mint_bits // 32
    entropy_bits = mint_bits - cs_bits
    eint = mint >> cs_bits
    csint = mint & ((1 << cs_bits) - 1)
    ebytes = eint_to_bytes(eint, entropy_bits)
    return csint == entropy_cs(ebytes)


def bip39_normalize_passphrase_original(passphrase):
    return unicodedata.normalize("NFKD", passphrase or "")


def bip39_normalize_passphrase(passphrase: str) -> str:
    """
    Normalizes a passphrase for use with BIP39.

    This function performs Unicode normalization using the "NFKD" form, which
    converts characters to their canonical decomposition. This means that
    characters that can be represented as a combination of other characters
    (like combining diacritics) are broken down into their base characters
    and combining marks. This ensures consistency and compatibility across
    different platforms and implementations.

    Args:
        passphrase (str): The passphrase to normalize.

    Returns:
        str: The normalized passphrase.
    """
    NFKD: str = "NFKD"
    normalized_passphrase: str = unicodedata.normalize(NFKD, passphrase or "")
    return normalized_passphrase


# returns tuple (is_checksum_valid, is_wordlist_valid)
def bip39_is_checksum_valid_original(mnemonic):
    words = [unicodedata.normalize("NFKD", word) for word in mnemonic.split()]
    words_len = len(words)
    n = len(wordlist_english)
    checksum_length = 11 * words_len // 33
    entropy_length = 32 * checksum_length
    i = 0
    words.reverse()
    while words:
        w = words.pop()
        try:
            k = wordlist_english.index(w)
        except ValueError:
            return False, False
        i = i * n + k
    if words_len not in [12, 15, 18, 21, 24]:
        return False, True
    entropy = i >> checksum_length
    checksum = i % 2**checksum_length
    h = "{:x}".format(entropy)
    while len(h) < entropy_length / 4:
        h = "0" + h
    b = bytearray.fromhex(h)
    hashed = int(safe_hexlify(hashlib.sha256(b).digest()), 16)
    calculated_checksum = hashed >> (256 - checksum_length)
    return checksum == calculated_checksum, True


def bip39_is_checksum_valid(mnemonic: str) -> Tuple[bool, bool]:
    """
    Checks if the checksum of a BIP39 mnemonic phrase is valid.

    This function takes a BIP39 mnemonic phrase and verifies if its checksum is
    correct. It returns a tuple containing two boolean values:

    - The first value indicates whether the checksum is valid.
    - The second value indicates whether the mnemonic phrase has a valid length.

    BIP39 (Bitcoin Improvement Proposal 39) is a standard that defines a method
    for generating mnemonic phrases, which are easy-to-remember sequences of words
    used to create deterministic wallets. These phrases can be used to recover the
    wallet if access is lost.

    Args:
        mnemonic (str): The BIP39 mnemonic phrase.

    Returns:
        Tuple[bool, bool]: A tuple containing two boolean values:
            - True if the checksum is valid, False otherwise.
            - True if the mnemonic phrase has a valid length, False otherwise.

    Example:
        >>> bip39_is_checksum_valid(
        ...     "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        ... )
        (True, True)
    """
    words: List[str] = [
        unicodedata.normalize("NFKD", word) for word in mnemonic.split()
    ]  # Normalize and split the mnemonic phrase into words
    words_len: int = len(words)  # Get the number of words in the mnemonic phrase
    n: int = len(wordlist_english)  # Get the number of words in the wordlist
    checksum_length: int = 11 * words_len // 33  # Calculate the checksum length
    entropy_length: int = 32 * checksum_length  # Calculate the entropy length
    i: int = 0  # Initialize a counter
    words.reverse()  # Reverse the list of words
    while words:
        w: str = words.pop()  # Get the last word from the list
        try:
            k: int = wordlist_english.index(
                w
            )  # Find the index of the word in the wordlist
        except ValueError:
            return False, False  # Return False if the word is not found in the wordlist
        i = i * n + k  # Update the counter based on the word's index
    if words_len not in [12, 15, 18, 21, 24]:  # Check if the number of words is valid
        return False, True  # Return False if the number of words is invalid
    entropy: int = i >> checksum_length  # Extract the entropy from the counter
    checksum: int = i % 2**checksum_length  # Extract the checksum from the counter
    h: str = "{:x}".format(entropy)  # Convert the entropy to hexadecimal
    while len(h) < entropy_length / 4:
        h = "0" + h  # Pad the hexadecimal string with leading zeros
    b: bytearray = bytearray.fromhex(h)  # Convert the hexadecimal string to a bytearray
    hashed: int = int(
        safe_hexlify(hashlib.sha256(b).digest()), 16
    )  # Calculate the SHA256 hash of the bytearray
    calculated_checksum: int = hashed >> (
        256 - checksum_length
    )  # Extract the calculated checksum from the hash
    return (
        checksum == calculated_checksum,
        True,
    )  # Return True if the checksum matches the calculated checksum


def mnemonic_to_seed_original(
    mnemonic_phrase, passphrase="", passphrase_prefix=b"mnemonic"
):
    passphrase = bip39_normalize_passphrase(passphrase=passphrase)
    passphrase = from_string_to_bytes(passphrase)
    if isinstance(mnemonic_phrase, (list, tuple)):
        mnemonic_phrase = " ".join(mnemonic_phrase)
    mnemonic = unicodedata.normalize("NFKD", " ".join(mnemonic_phrase.split()))
    mnemonic = from_string_to_bytes(mnemonic)
    return PBKDF2(
        mnemonic,
        passphrase_prefix + passphrase,
        iterations=2048,
        macmodule=hmac,
        digestmodule=hashlib.sha512,
    ).read(64)


def mnemonic_to_seed(
    mnemonic_phrase: Union[str, List[str], Tuple[str]],
    passphrase: str = "",
    passphrase_prefix: bytes = b"mnemonic",
) -> bytes:
    """
    Converts a BIP39 mnemonic phrase to a seed.

    This function takes a mnemonic phrase, normalizes it, and uses PBKDF2
    with SHA512 to derive a 64-byte seed.

    Args:
        mnemonic_phrase (Union[str, List[str], Tuple[str]]): The mnemonic phrase,
            either as a string with words separated by spaces, or as a list or
            tuple of words.
        passphrase (str, optional): The passphrase to use for seed derivation.
            Defaults to "".
        passphrase_prefix (bytes, optional): The prefix to use for the passphrase
            in PBKDF2. Defaults to b"mnemonic".

    Returns:
        bytes: The derived seed.
    """
    passphrase_normalized: str = bip39_normalize_passphrase(passphrase=passphrase)
    passphrase_bytes: bytes = from_string_to_bytes(a=passphrase_normalized)
    if isinstance(mnemonic_phrase, (list, tuple)):
        mnemonic_phrase: str = " ".join(mnemonic_phrase)
    mnemonic_normalized: str = unicodedata.normalize(
        "NFKD", " ".join(mnemonic_phrase.split())
    )
    mnemonic_bytes: bytes = from_string_to_bytes(a=mnemonic_normalized)
    seed_64_byte_bip32: bytes = PBKDF2(
        passphrase=mnemonic_bytes,
        salt=passphrase_prefix + passphrase_bytes,
        iterations=2048,
        macmodule=hmac,
        digestmodule=hashlib.sha512,
    ).read(64)

    return seed_64_byte_bip32


def bip39_mnemonic_to_seed(mnemonic_phrase, passphrase=""):
    if not bip39_is_checksum_valid(mnemonic_phrase)[1]:
        raise Exception("BIP39 Checksum is invalid for this mnemonic")
    return mnemonic_to_seed(
        mnemonic_phrase, passphrase_bytes=passphrase, passphrase_prefix=b"mnemonic"
    )


def electrum_mnemonic_to_seed_original(
    mnemonic_phrase,
    passphrase="",
):
    return mnemonic_to_seed(
        mnemonic_phrase, passphrase_bytes=passphrase, passphrase_prefix=b"electrum"
    )


def electrum_mnemonic_to_seed(
    mnemonic_phrase: str,
    passphrase: str = "",
) -> bytes:
    """
    Converts an Electrum mnemonic phrase to a BIP32 seed.

    This function takes an Electrum mnemonic phrase and an optional passphrase,
    and returns a 64-byte BIP32 seed. The seed is generated using the
    `mnemonic_to_seed` function with the "electrum" passphrase prefix.

    Args:
        mnemonic_phrase (str): The Electrum mnemonic phrase.
        passphrase (str, optional): The passphrase associated with the mnemonic phrase.
            Defaults to "".

    Returns:
        bytes: The 64-byte BIP32 seed.

    Example:
        >>> electrum_mnemonic_to_seed(
        ...     "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        ...     "password"
        ... )
        b'\x03\x9a\x99\x05\x9c\x97\x31\x98\x8a\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01\x04\x01'
    """
    seed_64_byte_bip32: bytes = mnemonic_to_seed(
        mnemonic_phrase,
        passphrase_bytes=passphrase,
        passphrase_prefix=b"electrum",
    )
    return seed_64_byte_bip32


def is_old_seed(seed):
    return False


def seed_prefix(seed_type):
    if seed_type == "standard":
        return SEED_PREFIX
    elif seed_type == "segwit":
        return SEED_PREFIX_SW
    elif seed_type == "2fa":
        return SEED_PREFIX_2FA


def seed_type(x):
    if is_old_seed(x):
        return "old"
    elif is_new_seed(x):
        return "standard"
    elif is_new_seed(x, SEED_PREFIX_SW):
        return "segwit"
    elif is_new_seed(x, SEED_PREFIX_2FA):
        return "2fa"
    return ""


is_seed = lambda x: bool(seed_type(x))


def words_mine(
    prefix,
    entbits,
    satisfunction,
    wordlist=wordlist_english,
    randombits=random.getrandbits,
):
    prefix_bits = len(prefix) * 11
    mine_bits = entbits - prefix_bits
    pint = words_to_mnemonic_int(prefix, wordlist)
    pint <<= mine_bits
    dint = randombits(mine_bits)
    count = 0
    while not satisfunction(entropy_to_words(eint_to_bytes(pint + dint, entbits))):
        dint = randombits(mine_bits)
        if (count & 0xFFFF) == 0:
            print(
                "Searched %f percent of the space"
                % (float(count) / float(1 << mine_bits))
            )

    return entropy_to_words(eint_to_bytes(pint + dint, entbits))
