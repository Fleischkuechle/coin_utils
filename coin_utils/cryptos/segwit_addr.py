# Copyright (c) 2017 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Reference implementation for Bech32/Bech32m and segwit addresses."""

from enum import Enum
from typing import Tuple, Optional, Sequence, NamedTuple, List

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_CHARSET_INVERSE = {x: CHARSET.find(x) for x in CHARSET}

BECH32_CONST = 1
BECH32M_CONST = 0x2BC830A3


class Encoding(Enum):
    """Enumeration type to list the various supported encodings."""

    BECH32 = 1
    BECH32M = 2


class DecodedBech32(NamedTuple):
    encoding: Optional[Encoding]
    hrp: Optional[str]
    data: Optional[Sequence[int]]  # 5-bit ints


def bech32_polymod_original(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_polymod(values: list[int]) -> int:
    """
    Internal function that computes the Bech32 checksum.

    This function calculates the checksum for a Bech32 encoded string.
    It takes a list of integers representing the data
    and HRP (human-readable part) as input. The checksum is computed
    using a specific polynomial modulo operation.

    The function uses a generator polynomial defined by the constants `generator` and
    performs a series of bitwise operations
    on the input values. The result is a 32-bit checksum that is used in the Bech32
    encoding process.

    Args:
        values (list[int]): A list of integers representing the data and HRP.

    Returns:
        int: The calculated Bech32 checksum as an integer.
    """
    generator: list[int] = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk: int = 1
    for value in values:
        top: int = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand_original(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_hrp_expand(hrp: str) -> list[int]:
    """
    Expand the HRP into values for checksum computation.

    This function takes a human-readable part (HRP) as input and expands it into a list of integers.
    The expansion process involves converting each character in the HRP to its ASCII code, then splitting the code into two parts:
    - The first part (higher 5 bits) is shifted right by 5 bits.
    - The second part (lower 5 bits) is masked with 31 (0x1F).

    The expanded list of integers is then used in the checksum calculation for Bech32 encoding.

    Args:
        hrp (str): The human-readable part of the Bech32 string.

    Returns:
        list[int]: The expanded list of integers representing the HRP.
    """
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_verify_checksum_original(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    check = bech32_polymod(bech32_hrp_expand(hrp) + data)
    if check == BECH32_CONST:
        return Encoding.BECH32
    elif check == BECH32M_CONST:
        return Encoding.BECH32M
    else:
        return None


def bech32_verify_checksum(
    hrp: str,
    data: list[int],
) -> Encoding | None:
    """
    Verify a checksum given HRP and converted data characters.

    This function checks the validity of a Bech32 encoded string by
    comparing the computed checksum with the expected
    checksum values for Bech32 and Bech32m encoding.

    Args:
        hrp (str): The human-readable part of the Bech32 encoded string.
        data (list[int]): A list of integers representing the data part of the Bech32 encoded string.

    Returns:
        Encoding | None: Returns the `Encoding` enum value (BECH32 or BECH32M) if the checksum is valid, otherwise returns `None`.
    """
    Bech32_checksum_int: int = bech32_polymod(values=bech32_hrp_expand(hrp) + data)
    if Bech32_checksum_int == BECH32_CONST:
        return Encoding.BECH32
    elif Bech32_checksum_int == BECH32M_CONST:
        return Encoding.BECH32M
    else:
        return None


def bech32_create_checksum(encoding: Encoding, hrp: str, data: List[int]) -> List[int]:
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    const = BECH32M_CONST if encoding == Encoding.BECH32M else BECH32_CONST
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_encode_original(encoding: Encoding, hrp: str, data: List[int]) -> str:
    """Compute a Bech32 or Bech32m string given HRP and data values."""
    combined = data + bech32_create_checksum(encoding, hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in combined])


def bech32_encode(
    encoding: Encoding,
    hrp: str,
    data: List[int],
) -> str:
    """
    Compute a Bech32 or Bech32m string given HRP and data values.

    This function takes an encoding type (`encoding`), a human-readable part (`hrp`),
    and a list of data values (`data`) as input.
    It then calculates a checksum based on the encoding, HRP, and data,
    combines the data with the checksum, and encodes it using the Bech32 character set.
    Finally, it returns the complete Bech32 or Bech32m string.

    The HRP (Human-Readable Part) is a prefix that identifies the type of data
    being encoded in a Bech32 string.
    It helps distinguish between different networks or types of addresses.
    For example, in Bitcoin, "bc" is used for mainnet addresses,
    while "tb" is used for testnet addresses.

    Args:
        encoding (Encoding): The encoding type (Bech32 or Bech32m).
        hrp (str): The human-readable part of the Bech32 string.
        data (List[int]): The data values to encode.

    Returns:
        str: The Bech32 or Bech32m encoded string.
    """
    combined = data + bech32_create_checksum(encoding, hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in combined])


def bech32_decode(bech: str, *, ignore_long_length=False) -> DecodedBech32:
    """Validate a Bech32/Bech32m string, and determine HRP and data."""
    bech_lower = bech.lower()
    if bech_lower != bech and bech.upper() != bech:
        return DecodedBech32(None, None, None)
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or (not ignore_long_length and len(bech) > 90):
        return DecodedBech32(None, None, None)
    # check that HRP only consists of sane ASCII chars
    if any(ord(x) < 33 or ord(x) > 126 for x in bech[: pos + 1]):
        return DecodedBech32(None, None, None)
    bech = bech_lower
    hrp = bech[:pos]
    try:
        data = [_CHARSET_INVERSE[x] for x in bech[pos + 1 :]]
    except KeyError:
        return DecodedBech32(None, None, None)
    encoding = bech32_verify_checksum(hrp, data)
    if encoding is None:
        return DecodedBech32(None, None, None)
    return DecodedBech32(encoding=encoding, hrp=hrp, data=data[:-6])


def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def decode_segwit_address(
    hrp: str, addr: Optional[str]
) -> Tuple[Optional[int], Optional[Sequence[int]]]:
    """Decode a segwit address."""
    if addr is None:
        return (None, None)
    encoding, hrpgot, data = bech32_decode(addr)
    if hrpgot != hrp:
        return (None, None)
    decoded = convertbits(data[1:], 5, 8, False)
    if decoded is None or len(decoded) < 2 or len(decoded) > 40:
        return (None, None)
    if data[0] > 16:
        return (None, None)
    if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
        return (None, None)
    if (data[0] == 0 and encoding != Encoding.BECH32) or (
        data[0] != 0 and encoding != Encoding.BECH32M
    ):
        return (None, None)
    return (data[0], decoded)


def encode_segwit_address_original(
    hrp: str, witver: int, witprog: bytes
) -> Optional[str]:
    """Encode a segwit address."""
    encoding = Encoding.BECH32 if witver == 0 else Encoding.BECH32M
    ret = bech32_encode(encoding, hrp, [witver] + convertbits(witprog, 8, 5))
    if decode_segwit_address(hrp, ret) == (None, None):
        return None
    return ret


def encode_segwit_address(
    hrp: str,
    witver: int,
    witprog: bytes,
) -> Optional[str]:
    """Encode a segwit address."""
    encoding = Encoding.BECH32 if witver == 0 else Encoding.BECH32M
    ret = bech32_encode(encoding, hrp, [witver] + convertbits(witprog, 8, 5))
    if decode_segwit_address(hrp, ret) == (None, None):
        return None
    return ret
