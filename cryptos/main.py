#!/usr/bin/python

from typing import List, Optional, Tuple, AnyStr, Any, Union

# from blinker import ANY
# from numpy import byte


# from pybitcointools.cryptos.coins_async import BaseCoin


# coins = {c.coin_symbol: c for c in (Bitcoin, Litecoin, BitcoinCash, Dash, Doge)}


# # from pybitcointools.cryptos.coins_async import BaseCoin
# from pybitcointools.cryptos.py3specials import *
# from pybitcointools.cryptos.ripemd import *

from .types import PrivkeyType, PubKeyType

from .coins_async.base import BaseCoin
from .py3specials import *
import binascii
import hashlib
import re
import base64
import time
import random
import hmac

from .ripemd import *


from .types import PrivkeyType, PubKeyType

# Elliptic curve parameters (secp256k1)
# for more details look here
# https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf
# The secp256k1 curve parameters are defined in the SECG
# (Standards for Efficient Cryptography Group) document titled
# "SEC 2: Recommended Elliptic Curve Domain Parameters". This document lists the parameters
# for various elliptic curves, including secp256k1, which is used in Bitcoin.
# Yes, Bitcoin uses the secp256k1 elliptic curve for its public-key cryptography.
# This curve is specifically designed for efficient and secure cryptographic operations.
# It's a Koblitz curve, which means it has a special structure that
#     allows for faster scalar multiplications, making it suitable for
# use in Bitcoin's blockchain.


# P = 2**256 - 2**32 - 977
# N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
# A = 0
# B = 7
# Gx:int = 55066263022277343669578718895168534326250603453777594175500187360389116729240
# Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
# G: Tuple[int, int] = (Gx, Gy)

P: int = 2**256 - 2**32 - 977
N: int = 115792089237316195423570985008687907852837564279074904382605163141518161494337
A: int = 0
B: int = 7
Gx: int = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy: int = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G: Tuple[int, int] = (Gx, Gy)


def change_curve(p, n, a, b, gx, gy):
    global P, N, A, B, Gx, Gy, G
    P, N, A, B, Gx, Gy = p, n, a, b, gx, gy
    G = (Gx, Gy)


def getG():
    return G


def magicbyte_to_prefix(magicbyte) -> List[str]:
    first = bin_to_b58check(hash160Low, magicbyte=magicbyte)[0]
    last = bin_to_b58check(hash160High, magicbyte=magicbyte)[0]
    if first == last:
        return [first]
    return [first, last]


# Extended Euclidean Algorithm


def inv(a, n):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n


# JSON access (for pybtctool convenience)


def access(obj, prop):
    if isinstance(obj, dict):
        if prop in obj:
            return obj[prop]
        elif "." in prop:
            return obj[float(prop)]
        else:
            return obj[int(prop)]
    else:
        return obj[int(prop)]


def multiaccess(obj, prop):
    return [access(o, prop) for o in obj]


def slice(obj, start=0, end=2**200):
    return obj[int(start) : int(end)]


def count(obj):
    return len(obj)


_sum = sum


def sum(obj):
    return _sum(obj)


def isinf(p):
    return p[0] == 0 and p[1] == 0


def to_jacobian(p: Tuple[int, int]) -> Tuple[int, int, float]:
    """
    Converts a point in affine coordinates to Jacobian coordinates.

    This function takes a point represented in affine coordinates (x, y) and converts it to
    Jacobian coordinates (X, Y, Z). Jacobian coordinates are a projective coordinate system
    used in elliptic curve cryptography for efficient point addition and doubling operations.

    In Jacobian coordinates, a point (x, y) is represented as (X, Y, Z) where:

    - x = X / Z²
    - y = Y / Z³

    This representation allows for faster point addition and doubling operations by avoiding
    expensive field inversions.

    Args:
        p (tuple): A tuple representing the point in affine coordinates (x, y).

    Returns:
        tuple: A tuple representing the point in Jacobian coordinates (X, Y, Z).

    More:
        Initial Value: When you convert a point from affine coordinates (x, y) to Jacobian coordinates (X, Y, Z), the initial value of Z is set to 1.
        Purpose: This initial value of 1 ensures that the conversion back to affine coordinates using the formulas x = X / Z² and y = Y / Z³ results in the original x and y values.
        Think of it like this:

        You start with a point (x, y) in affine coordinates.
        You convert it to Jacobian coordinates (X, Y, Z) with Z initially set to 1.
        When you convert back to affine coordinates, dividing by Z² (which is 1²) and Z³ (which is 1³) doesn't change the values of X and Y, effectively preserving the original point.
        Important Note: The value of Z can change during point addition and doubling operations on the elliptic curve. However, the conversion formulas between affine and Jacobian coordinates always use the current value of Z to maintain consistency.

        So, when you hear "normalized" in elliptic curve cryptography,
        it usually refers to points represented
        in affine coordinates, which are essentially a
        "normalized" form of projective coordinates.  (maybe its kind of a uv coordinate im not sure. like a uv unwrap in blender)
    """
    o: Tuple[int, int, float] = (p[0], p[1], 1)
    return o


def jacobian_double_original(p):
    if not p[1]:
        return (0, 0, 0)
    ysq = (p[1] ** 2) % P
    S = (4 * p[0] * ysq) % P
    M = (3 * p[0] ** 2 + A * p[2] ** 4) % P
    nx = (M**2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq**2) % P
    nz = (2 * p[1] * p[2]) % P
    return (nx, ny, nz)


def jacobian_double(p: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    Doubles a point in Jacobian coordinates on an elliptic curve.

    This function performs point doubling on an elliptic curve in Jacobian coordinates. It takes a point represented as a tuple (x, y, z) in Jacobian coordinates and returns the doubled point in the same coordinate system.

    Args:
        p (tuple[int, int, int]): The point to be doubled in Jacobian coordinates (x, y, z).

    Returns:
        tuple[int, int, int]: The doubled point in Jacobian coordinates (x', y', z').

    Example:
        >>> jacobian_double((1, 2, 3))
        (10, 20, 6)
    """
    if not p[1]:
        return (0, 0, 0)
    ysq = (p[1] ** 2) % P
    S = (4 * p[0] * ysq) % P
    M = (3 * p[0] ** 2 + A * p[2] ** 4) % P
    nx = (M**2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq**2) % P
    nz = (2 * p[1] * p[2]) % P
    return (nx, ny, nz)


def jacobian_add_original(p, q):
    if not p[1]:
        return q
    if not q[1]:
        return p
    U1 = (p[0] * q[2] ** 2) % P
    U2 = (q[0] * p[2] ** 2) % P
    S1 = (p[1] * q[2] ** 3) % P
    S2 = (q[1] * p[2] ** 3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobian_double(p=p)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R**2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * p[2] * q[2]) % P
    return (nx, ny, nz)


def jacobian_add(
    p: tuple[int, int, int],
    q: tuple[int, int, int],
) -> tuple[int, int, int]:
    """
    Adds two points in Jacobian coordinates on an elliptic curve.

    This function performs point addition on an elliptic curve in Jacobian coordinates.
    It takes two points represented as tuples (x1, y1, z1) and (x2, y2, z2)
    in Jacobian coordinates and returns their sum in the same coordinate system.

    Args:
        p (tuple[int, int, int]): The first point in Jacobian coordinates (x1, y1, z1).
        q (tuple[int, int, int]): The second point in Jacobian coordinates (x2, y2, z2).

    Returns:
        tuple[int, int, int]: The sum of the two points in Jacobian coordinates (x', y', z').

    Example:
        >>> jacobian_add((1, 2, 3), (4, 5, 6))
        (10, 20, 30)
    """
    if not p[1]:
        return q
    if not q[1]:
        return p
    U1 = (p[0] * q[2] ** 2) % P
    U2 = (q[0] * p[2] ** 2) % P
    S1 = (p[1] * q[2] ** 3) % P
    S2 = (q[1] * p[2] ** 3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobian_double(p=p)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R**2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * p[2] * q[2]) % P
    return (nx, ny, nz)


def from_jacobian_original(p):
    """
    Converts a point in Jacobian coordinates to standard affine coordinates.

    This function takes a point represented in Jacobian coordinates (x, y, z) and converts it to standard affine coordinates (x', y').
    It uses the inverse of the z-coordinate (z^-1) to perform the conversion.

    Args:
        p (tuple): A tuple representing a point in Jacobian coordinates (x, y, z).

    Returns:
        tuple: A tuple representing the point in standard affine coordinates (x', y').

    Example:
        >>> from_jacobian((1, 2, 3))
        (1/9, 2/27)
    """
    z = inv(p[2], P)
    return ((p[0] * z**2) % P, (p[1] * z**3) % P)


def from_jacobian(p: tuple[int, int]) -> tuple[int, int]:
    """
    Converts a point in Jacobian coordinates to standard affine coordinates.

    This function takes a point represented in Jacobian coordinates (x, y, z) and converts it to standard affine coordinates (x', y').
    It uses the inverse of the z-coordinate (z^-1) to perform the conversion.

    Args:
        p (tuple(int,int)): A tuple representing a point in Jacobian coordinates (x, y, z).

    Returns:
        tuple(int,int): A tuple representing the point in standard affine coordinates (x', y').

    Example:
        >>> from_jacobian((1, 2, 3))
        (1/9, 2/27)
    """
    z = inv(p[2], P)
    return ((p[0] * z**2) % P, (p[1] * z**3) % P)


def jacobian_multiply(
    a: Tuple[int, int, int],
    n: int,
) -> Tuple[int, int, int]:
    """
    Performs scalar multiplication on a point in Jacobian coordinates.

    This function implements the double-and-add algorithm for scalar multiplication
    on elliptic curves in Jacobian coordinates. It efficiently calculates the product
    of a point `a` and a scalar `n`.

    Args:
        a (Tuple[int, int, int]): The point in Jacobian coordinates (x, y, z).
        n (int): The scalar multiplier.

    Returns:
        Tuple[int, int, int]: The resulting point in Jacobian coordinates.
    """
    result: Tuple[int, int, int] = (0, 0, 0)
    if a[1] == 0 or n == 0:
        return (0, 0, 1)
    if n == 1:
        return a
    if n < 0 or n >= N:
        return jacobian_multiply(a, n % N)
    if (n % 2) == 0:
        return jacobian_double(jacobian_multiply(a, n // 2))
    if (n % 2) == 1:
        return jacobian_add(jacobian_double(jacobian_multiply(a, n // 2)), a)
    return result


def fast_multiply_original(a: int, n: int):
    """
    Performs fast multiplication of an integer 'a' by an integer 'n' using Jacobian coordinates.

    This function leverages the efficiency of Jacobian coordinates for point multiplication on elliptic curves.
    It first converts the integer 'a' to Jacobian coordinates using the `to_jacobian` function.
    Then, it performs the multiplication using the `jacobian_multiply` function, which is optimized for Jacobian coordinates.
    Finally, it converts the result back to standard integer representation using the `from_jacobian` function.

    Args:
        a (int): The integer to be multiplied.
        n (int): The multiplier.

    Returns:
        int: The result of the multiplication, 'a * n'.

    Example:
        >>> fast_multiply(5, 3)
        15
    """
    jacobian_affine_coordinates: tuple[int, int] = from_jacobian(
        jacobian_multiply(a=to_jacobian(p=a), n=n)
    )
    return jacobian_affine_coordinates  # from_jacobian(jacobian_multiply(a=to_jacobian(p=a), n=n))


def fast_multiply(a: int, n: int) -> Tuple[int, int]:
    """
    Performs fast multiplication of an integer 'a' by an integer 'n' using Jacobian coordinates.

    This function leverages the efficiency of Jacobian coordinates for point multiplication on elliptic curves.
    It first converts the integer 'a' to Jacobian coordinates using the `to_jacobian` function.
    Then, it performs the multiplication using the `jacobian_multiply` function, which is optimized for Jacobian coordinates.
    Finally, it converts the result back to standard integer representation using the `from_jacobian` function.

    Args:
        a (int): The integer to be multiplied.
        n (int): The multiplier.

    Returns:
        Tuple[int, int]: The result of the multiplication, represented as a tuple of (x, y) coordinates.

    Example:
        >>> fast_multiply(2, 3)
        (6, 4)
    """
    jacobian_affine_coordinates: Tuple[int, int] = from_jacobian(
        jacobian_multiply(a=to_jacobian(p=a), n=n)
    )
    return jacobian_affine_coordinates


def fast_add(a, b):
    """
    Performs fast addition of two integers 'a' and 'b' using Jacobian coordinates.

    This function leverages the efficiency of Jacobian coordinates for point addition on elliptic curves.
    It first converts both integers 'a' and 'b' to Jacobian coordinates using the `to_jacobian` function.
    Then, it performs the addition using the `jacobian_add` function, which is optimized for Jacobian coordinates.
    Finally, it converts the result back to standard integer representation using the `from_jacobian` function.

    Args:
        a (int): The first integer to be added.
        b (int): The second integer to be added.

    Returns:
        int: The result of the addition, 'a + b'.

    Example:
        >>> fast_add(5, 3)
        8
    """
    return from_jacobian(jacobian_add(to_jacobian(p=a), to_jacobian(p=b)))


# Functions for handling pubkey and privkey formats


class UnrecognisedPublicKeyFormat(BaseException):
    pass


def get_pubkey_format_original(pub) -> str:
    two = 2
    three = 3
    four = 4

    if isinstance(pub, (tuple, list)):
        return "decimal"
    elif len(pub) == 65 and pub[0] == four:
        return "bin"
    elif len(pub) == 130 and pub[0:2] == "04":
        return "hex"
    elif len(pub) == 33 and pub[0] in [two, three]:
        return "bin_compressed"
    elif len(pub) == 66 and pub[0:2] in ["02", "03"]:
        return "hex_compressed"
    elif len(pub) == 64:
        return "bin_electrum"
    elif len(pub) == 128:
        return "hex_electrum"
    else:
        raise UnrecognisedPublicKeyFormat("Pubkey not in recognized format")


def get_pubkey_format_old(pub: Any) -> str:
    """
    Determines the format of a public key.

    This function analyzes the provided public key
    and identifies its format based on its length and content.
    It supports various public key formats commonly used in Bitcoin
    and other cryptocurrencies.

    Args:
        pub:
            The public key to analyze. It can be in various formats, including:
                - Binary: Raw bytes representing the public key.
                - Hexadecimal:  A string containing the hexadecimal representation of the public key.
                - Decimal: A tuple or list of integers representing the public key.
                - Compressed (Binary/Hex): A compressed version of the public key, where only the x-coordinate is stored.

    Returns:
        str:
            A string indicating the format of the public key. Possible values are:
                "decimal":
                    The public key is represented as a tuple or list of integers.
                "bin":
                    The public key is in binary format (uncompressed).
                "hex":
                    The public key is in hexadecimal format (uncompressed).
                "bin_compressed":
                    The public key is in binary format (compressed).
                "hex_compressed":
                    The public key is in hexadecimal format (compressed).
                "bin_electrum":
                    The public key is in binary format (Electrum format).
                "hex_electrum":
                    The public key is in hexadecimal format (Electrum format).

    Raises:
        UnrecognisedPublicKeyFormat:
            If the public key is not in a recognized format.
    """
    two: int = 2
    three: int = 3
    four: int = 4
    key_length: int = len(pub)
    if isinstance(pub, (tuple, list)):
        return "decimal"
    elif key_length == 65 and pub[0] == four:
        return "bin"
    elif key_length == 130 and pub[0:2] == "04":
        return "hex"
    elif key_length == 33 and pub[0] in [two, three]:
        return "bin_compressed"
    elif key_length == 66 and pub[0:2] in ["02", "03"]:
        return "hex_compressed"
    elif key_length == 64:
        return "bin_electrum"
    elif key_length == 128:
        return "hex_electrum"
    else:
        raise UnrecognisedPublicKeyFormat("Pubkey not in recognized format")


def get_pubkey_format(pub: Any) -> str:
    """
    Determines the format of a public key.

    This function analyzes the provided public key
    and identifies its format based on its length and content.
    It supports various public key formats commonly used in Bitcoin
    and other cryptocurrencies.

    Args:
        pub:
            The public key to analyze. It can be in various formats, including:
                - Binary: Raw bytes representing the public key.
                - Hexadecimal:  A string containing the hexadecimal representation of the public key.
                - Decimal: A tuple or list of integers representing the public key.
                - Compressed (Binary/Hex): A compressed version of the public key, where only the x-coordinate is stored.

    Returns:
        str:
            A string indicating the format of the public key. Possible values are:
                "decimal":
                    The public key is represented as a tuple or list of integers.
                "bin":
                    The public key is in binary format (uncompressed).
                "hex":
                    The public key is in hexadecimal format (uncompressed).
                "bin_compressed":
                    The public key is in binary format (compressed).
                "hex_compressed":
                    The public key is in hexadecimal format (compressed).
                "bin_electrum":
                    The public key is in binary format (Electrum format).
                "hex_electrum":
                    The public key is in hexadecimal format (Electrum format).

    Raises:
        UnrecognisedPublicKeyFormat:
            If the public key is not in a recognized format.
    """
    if isinstance(pub, (tuple, list)):
        return "decimal"
    elif isinstance(pub, bytes):
        key_length: int = len(pub)
        if key_length == 65 and pub[0] == 4:
            return "bin"
        elif key_length == 33 and pub[0] in [2, 3]:
            return "bin_compressed"
        elif key_length == 64:
            return "bin_electrum"
    elif isinstance(pub, str):
        key_length: int = len(pub)
        if key_length == 130 and pub[0:2] == "04":
            return "hex"
        elif key_length == 66 and pub[0:2] in ["02", "03"]:
            return "hex_compressed"
        elif key_length == 128:
            return "hex_electrum"
    raise UnrecognisedPublicKeyFormat(f"Pubkey not in recognized format {pub}")


def is_public_key_original(pub: str) -> bool:
    try:
        fmt: str = get_pubkey_format(pub=pub)
        return True
    except UnrecognisedPublicKeyFormat:
        return False


def is_public_key(pub: str) -> bool:
    """
    Checks if a given string represents a valid public key.

    This function attempts to determine the format of the provided string using the `get_pubkey_format` function. If the format is recognized, it returns `True`, indicating that the string is a valid public key. Otherwise, it returns `False`.

    Args:
        pub: The string to check for validity as a public key.

    Returns:
        bool: `True` if the string is a valid public key, `False` otherwise.
    """
    try:
        fmt: str = get_pubkey_format(pub=pub)
        return True
    except UnrecognisedPublicKeyFormat:
        return False


def encode_pubkey_original(pub, formt):
    if not isinstance(pub, (tuple, list)):
        pub = decode_pubkey(pub)
    if formt == "decimal":
        return pub
    elif formt == "bin":
        return b"\x04" + encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == "bin_compressed":
        return from_int_to_byte(2 + (pub[1] % 2)) + encode(pub[0], 256, 32)
    elif formt == "hex":
        return "04" + encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    elif formt == "hex_compressed":
        return "0" + str(2 + (pub[1] % 2)) + encode(pub[0], 16, 64)
    elif formt == "bin_electrum":
        return encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == "hex_electrum":
        return encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    else:
        raise Exception("Invalid format!")


def encode_pubkey(
    pub: Union[Tuple[int, int], str],
    formt: str,
) -> str:
    """
    Encodes a public key into a string representation in the specified format.

    This function takes a public key, which can be either a tuple of integers representing the X and Y coordinates or a string representation of the public key, and encodes it into a string representation in the specified format. It supports the following formats:

    * **`decimal`:** The public key is represented as a decimal string. This is simply returned as is.
    * **`bin`:** The public key is represented as a binary string, with the X and Y coordinates concatenated.
    * **`bin_compressed`:** The public key is represented as a compressed binary string, where the X coordinate is followed by a single byte indicating the parity of the Y coordinate.
    * **`hex`:** The public key is represented as a hexadecimal string, with the X and Y coordinates concatenated.
    * **`hex_compressed`:** The public key is represented as a compressed hexadecimal string, similar to `bin_compressed`.
    * **`bin_electrum`:** The public key is represented as a binary string in Electrum format, where the X and Y coordinates are concatenated.
    * **`hex_electrum`:** The public key is represented as a hexadecimal string in Electrum format, similar to `bin_electrum`.

    If the input `pub` is not a tuple or list, it is first decoded using the `decode_pubkey` function.

    Args:
        pub: The public key to encode, either as a tuple of integers (X, Y) or a string representation.
        formt: The desired format for the encoded public key.

    Returns:
        The encoded public key as a bytes object.

    Raises:
        Exception: If an invalid format is provided.
    """
    if not isinstance(pub, (tuple, list)):
        pub = decode_pubkey(pub)
    if formt == "decimal":
        return pub
    elif formt == "bin":
        return b"\x04" + encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == "bin_compressed":
        return from_int_to_byte(2 + (pub[1] % 2)) + encode(pub[0], 256, 32)
    elif formt == "hex":
        return "04" + encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    elif formt == "hex_compressed":
        return "0" + str(2 + (pub[1] % 2)) + encode(pub[0], 16, 64)
    elif formt == "bin_electrum":
        return encode(pub[0], 256, 32) + encode(pub[1], 256, 32)
    elif formt == "hex_electrum":
        return encode(pub[0], 16, 64) + encode(pub[1], 16, 64)
    else:
        raise Exception("Invalid format!")


def decode_pubkey_original(pub, formt=None):
    if not formt:
        formt = get_pubkey_format(pub=pub)
    if formt == "decimal":
        return pub
    elif formt == "bin":
        return (decode(string=pub[1:33], base=256), decode(string=pub[33:65], base=256))
    elif formt == "bin_compressed":
        x = decode(string=pub[1:33], base=256)
        beta = pow(int(x * x * x + A * x + B), int((P + 1) // 4), int(P))
        y = (P - beta) if ((beta + from_byte_to_int(pub[0])) % 2) else beta
        return (x, y)
    elif formt == "hex":
        return (decode(string=pub[2:66], base=16), decode(string=pub[66:130], base=16))
    elif formt == "hex_compressed":
        return decode_pubkey(safe_from_hex(s=pub), "bin_compressed")
    elif formt == "bin_electrum":
        return (decode(pub[:32], 256), decode(pub[32:64], 256))
    elif formt == "hex_electrum":
        return (decode(pub[:64], 16), decode(pub[64:128], 16))
    else:
        raise Exception("Invalid format!")


def decode_pubkey(pub: str, formt: str = None) -> Tuple[int, int]:
    """
    Decodes a public key string into a tuple of integers
    representing the X and Y coordinates.

    This function takes a public key string in various
    formats and converts it into a tuple of integers representing
    the X and Y coordinates of the corresponding point on the elliptic curve.
    It supports the following formats:

    * **`decimal`:** The public key is represented as a decimal string. This is simply returned as is.
    * **`bin`:** The public key is represented as a binary string, with the X and Y coordinates concatenated.
    * **`bin_compressed`:** The public key is represented as a compressed binary string, where the X coordinate is followed by a single byte indicating the parity of the Y coordinate.
    * **`hex`:** The public key is represented as a hexadecimal string, with the X and Y coordinates concatenated.
    * **`hex_compressed`:** The public key is represented as a compressed hexadecimal string, similar to `bin_compressed`.
    * **`bin_electrum`:** The public key is represented as a binary string in Electrum format, where the X and Y coordinates are concatenated.
    * **`hex_electrum`:** The public key is represented as a hexadecimal string in Electrum format, similar to `bin_electrum`.

    If the `formt` argument is not provided, the function attempts
    to automatically detect the format based on the input string.

    Args:
        pub: The public key string to decode.
        formt: The format of the public key string. If not provided,
        it will be automatically detected.

    Returns:
        A tuple containing the X and Y coordinates of the public key as integers.

    Raises:
        Exception: If an invalid format is provided.
    """
    if not formt:
        formt = get_pubkey_format(pub=pub)
    if formt == "decimal":
        return pub
    elif formt == "bin":
        return (decode(string=pub[1:33], base=256), decode(string=pub[33:65], base=256))
    elif formt == "bin_compressed":
        x = decode(string=pub[1:33], base=256)
        beta = pow(int(x * x * x + A * x + B), int((P + 1) // 4), int(P))
        y = (P - beta) if ((beta + from_byte_to_int(pub[0])) % 2) else beta
        return (x, y)
    elif formt == "hex":
        return (decode(string=pub[2:66], base=16), decode(string=pub[66:130], base=16))
    elif formt == "hex_compressed":
        return decode_pubkey(safe_from_hex(s=pub), "bin_compressed")
    elif formt == "bin_electrum":
        return (decode(pub[:32], 256), decode(pub[32:64], 256))
    elif formt == "hex_electrum":
        return (decode(pub[:64], 16), decode(pub[64:128], 16))
    else:
        raise Exception("Invalid format!")


def get_privkey_format(privkey: PrivkeyType) -> str:
    """
    Determines the format of a private key based on its length and type.

    Args:
        privkey (PrivkeyType): The private key to analyze. Can be an integer, a binary string,
                             a hexadecimal string, or a WIF(Wallet Import Format) string.

    Returns:
        str: A string representing the format of the private key. Possible values are:
            - "decimal": The private key is an integer.
            - "bin": The private key is a 32-byte binary string (uncompressed).
            - "bin_compressed": The private key is a 33-byte binary string (compressed).
            - "hex": The private key is a 64-character hexadecimal string (uncompressed).
            - "hex_compressed": The private key is a 66-character hexadecimal string (compressed).
            - "wif": The private key is a WIF(Wallet Import Format) string (uncompressed) len(bin_decode_privkey)= 32.
            - "wif_compressed": The private key is a WIF(Wallet Import Format) string (compressed) len(bin_decode_privkey)= 33.

    Raises:
        Exception: If the input is not a valid WIF(Wallet Import Format) string.
    """
    if isinstance(privkey, int_types):
        return "decimal"
    elif len(privkey) == 32:
        return "bin"
    elif len(privkey) == 33:
        return "bin_compressed"
    elif len(privkey) == 64:
        return "hex"
    elif len(privkey) == 66:
        return "hex_compressed"
    else:
        try:
            magicbyte, bin_decode_privkey = b58check_to_bin(inp=privkey)
        except ValueError as e:
            raise ValueError(
                f"at {__name__} in function {get_privkey_format.__name__} this error happend: {e}"
            )
        if len(bin_decode_privkey) == 32:
            return "wif"
        elif len(bin_decode_privkey) == 33:
            return "wif_compressed"
        else:
            raise Exception("WIF does not represent privkey")

    # elif self.is_valid_dogecoin_or_litecoin_address(address=addr):
    #         # Assuming Dogecoin or litecoin uses P2PKH
    #         return addr_to_pubkey_script(addr=addr)


def get_privkey_format_original(privkey: PrivkeyType) -> str:
    """
    Determines the format of a private key based on its length and type.

    Args:
        privkey (PrivkeyType): The private key to analyze. Can be an integer, a binary string,
                             a hexadecimal string, or a WIF(Wallet Import Format) string.

    Returns:
        str: A string representing the format of the private key. Possible values are:
            - "decimal": The private key is an integer.
            - "bin": The private key is a 32-byte binary string (uncompressed).
            - "bin_compressed": The private key is a 33-byte binary string (compressed).
            - "hex": The private key is a 64-character hexadecimal string (uncompressed).
            - "hex_compressed": The private key is a 66-character hexadecimal string (compressed).
            - "wif": The private key is a WIF(Wallet Import Format) string (uncompressed) len(bin_decode_privkey)= 32.
            - "wif_compressed": The private key is a WIF(Wallet Import Format) string (compressed) len(bin_decode_privkey)= 33.

    Raises:
        Exception: If the input is not a valid WIF(Wallet Import Format) string.
    """
    if isinstance(privkey, int_types):
        return "decimal"
    elif len(privkey) == 32:
        return "bin"
    elif len(privkey) == 33:
        return "bin_compressed"
    elif len(privkey) == 64:
        return "hex"
    elif len(privkey) == 66:
        return "hex_compressed"
    else:
        magicbyte, bin_decode_privkey = b58check_to_bin(inp=privkey)
        if len(bin_decode_privkey) == 32:
            return "wif"
        elif len(bin_decode_privkey) == 33:
            return "wif_compressed"
        else:
            raise Exception("WIF does not represent privkey")

    # elif self.is_valid_dogecoin_or_litecoin_address(address=addr):
    #         # Assuming Dogecoin or litecoin uses P2PKH
    #         return addr_to_pubkey_script(addr=addr)


def encode_privkey_original(
    priv: PrivkeyType,
    formt: str,
    vbyte: int = 128,
) -> PrivkeyType:
    if not isinstance(priv, int_types):
        return encode_privkey(decode_privkey(priv), formt, vbyte)
    if formt == "decimal":
        return priv
    elif formt == "bin":
        return encode(priv, 256, 32)
    elif formt == "bin_compressed":
        return encode(priv, 256, 32) + b"\x01"
    elif formt == "hex":
        return encode(priv, 16, 64)
    elif formt == "hex_compressed":
        return encode(priv, 16, 64) + "01"
    elif formt == "wif":
        return bin_to_b58check(encode(priv, 256, 32), int(vbyte))
    elif formt == "wif_compressed":
        return bin_to_b58check(encode(priv, 256, 32) + b"\x01", int(vbyte))
    else:
        raise Exception("Invalid format!")


def encode_privkey(
    priv: PrivkeyType,
    formt: str,
    vbyte: int = 128,
) -> PrivkeyType:
    """Encodes a private key into various formats.

    Args:
        priv (PrivkeyType): The private key to encode. It can be represented in one of the following ways:
            - **Integer:** The raw integer value of the private key.
            - **String:** A string representation of the private key in a supported format (e.g., hexadecimal, binary).
            - **Bytes:** A byte sequence representing the private key.
        formt (str): The desired format for the encoded private key.
            Supported formats:
                - "decimal": Integer representation of the private key.
                - "bin": Binary representation of the private key.
                - "bin_compressed": Compressed binary representation of the private key.
                - "hex": Hexadecimal representation of the private key.
                - "hex_compressed": Compressed hexadecimal representation of the private key.
                - "wif": Wallet Import Format (uncompressed)
                - "wif_compressed": Wallet Import Format (compressed)
        vbyte (int, optional): The version byte for WIF encoding. Defaults to 128.

    Returns:
        PrivkeyType: The encoded private key in the specified format.

    Raises:
        Exception: If an invalid format is specified.
    """
    if not isinstance(priv, int_types):
        return encode_privkey(decode_privkey(priv), formt, vbyte)
    if formt == "decimal":
        return priv
    elif formt == "bin":
        return encode(priv, 256, 32)
    elif formt == "bin_compressed":
        return encode(priv, 256, 32) + b"\x01"
    elif formt == "hex":
        return encode(val=priv, base=16, minlen=64)
    elif formt == "hex_compressed":
        return encode(val=priv, base=16, minlen=64) + "01"
    elif formt == "wif":
        return bin_to_b58check(encode(priv, 256, 32), int(vbyte))
    elif formt == "wif_compressed":
        return bin_to_b58check(encode(priv, 256, 32) + b"\x01", int(vbyte))
    else:
        raise Exception("Invalid format!")


def decode_privkey(
    privkey: PrivkeyType,
    formt: str = None,
) -> PrivkeyType:
    """
    Decodes a private key from various formats to a standard representation (likely binary).

    Args:
        privkey (PrivkeyType): The input private key. The type `PrivkeyType` is likely defined elsewhere and could be a string, bytes, or a specific class representing a private key.
        formt (str, optional): The format of the input private key. If not provided, the function tries to infer the format based on the input `priv`. Defaults to None.

    Returns:
        PrivkeyType: The decoded private key in a standard representation.

    Raises:
        Exception: If the format is not recognized or if the format is WIF but the input `priv` does not represent a private key.
    """
    if not formt:
        formt = get_privkey_format(privkey)
    if formt == "decimal":
        return privkey
    elif formt == "bin":
        return decode(privkey, 256)
    elif formt == "bin_compressed":
        return decode(privkey[:32], 256)
    elif formt == "hex":
        return decode(privkey, 16)
    elif formt == "hex_compressed":
        return decode(privkey[:64], 16)
    elif formt == "wif":
        return decode(b58check_to_bin(privkey)[1], 256)
    elif formt == "wif_compressed":
        return decode(b58check_to_bin(privkey)[1][:32], 256)
    else:
        raise Exception("WIF does not represent privkey")


def add_pubkeys(p1, p2):
    f1, f2 = get_pubkey_format(p1), get_pubkey_format(p2)
    return encode_pubkey(fast_add(decode_pubkey(p1, f1), decode_pubkey(p2, f2)), f1)


def add_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    return encode_privkey((decode_privkey(p1, f1) + decode_privkey(p2, f2)) % N, f1)


def mul_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    return encode_privkey((decode_privkey(p1, f1) * decode_privkey(p2, f2)) % N, f1)


def multiply(pubkey, privkey):
    f1, f2 = get_pubkey_format(pubkey), get_privkey_format(privkey)
    pubkey, privkey = decode_pubkey(pubkey, f1), decode_privkey(privkey, f2)
    # http://safecurves.cr.yp.to/twist.html
    if not isinf(pubkey) and (pubkey[0] ** 3 + B - pubkey[1] * pubkey[1]) % P != 0:
        raise Exception("Point not on curve")
    return encode_pubkey(fast_multiply(pubkey, privkey), f1)


def divide(pubkey, privkey):
    factor = inv(decode_privkey(privkey), N)
    return multiply(pubkey, factor)


def compress_original(pubkey: str) -> str:
    f = get_pubkey_format(pub=pubkey)
    if "compressed" in f:
        return pubkey
    elif f == "bin":
        return encode_pubkey(decode_pubkey(pubkey, f), "bin_compressed")
    elif f == "hex" or f == "decimal":
        return encode_pubkey(decode_pubkey(pubkey, f), "hex_compressed")
    return pubkey


def compress(pubkey: str) -> str:
    format: str = get_pubkey_format(pub=pubkey)
    if "compressed" in format:
        return pubkey
    elif format == "bin":

        return encode_pubkey(decode_pubkey(pubkey, format), "bin_compressed")
    elif format == "hex" or format == "decimal":
        return encode_pubkey(decode_pubkey(pubkey, format), "hex_compressed")
    return pubkey


def decompress(pubkey: str) -> str:
    f = get_pubkey_format(pubkey)
    if "compressed" not in f:
        return pubkey
    elif f == "bin_compressed":
        return encode_pubkey(decode_pubkey(pubkey, f), "bin")
    elif f == "hex_compressed" or f == "decimal":
        return encode_pubkey(decode_pubkey(pubkey, f), "hex")
    return pubkey


def privkey_to_pubkey_original(privkey: Union[int, str]) -> str:
    f = get_privkey_format(privkey)
    privkey = decode_privkey(privkey, f)
    if privkey >= N:
        raise Exception("Invalid privkey")
    if f in ["bin", "bin_compressed", "hex", "hex_compressed", "decimal"]:
        return encode_pubkey(fast_multiply(G, privkey), f)
    return encode_pubkey(fast_multiply(G, privkey), f.replace("wif", "hex"))


def privkey_to_pubkey_old(privkey: Union[int, str]) -> str:
    """
    Derives the public key from a given private key.

    This function takes a private key in various formats and converts it to its corresponding
    public key. It handles different private key formats (decimal, binary, hexadecimal, WIF)
    and ensures the private key is within the valid range.

    Args:
        privkey (Union[int, str]): The private key to convert. It can be an integer, a binary string,
                            a hexadecimal string, or a WIF string.

    Returns:
        str: The public key in the same format as the input private key, if possible.
            For WIF input, the output is in hexadecimal format.

    Raises:
        Exception: If the private key is invalid (e.g., outside the valid range).
    """
    format: str = get_privkey_format(privkey=privkey)
    privkey_decoded: int = decode_privkey(privkey=privkey, formt=format)
    encoded_pubkey_bytes: bytes = bytes()
    if privkey_decoded >= N:
        raise Exception("Invalid privkey")
    if format in ["bin", "bin_compressed", "hex", "hex_compressed", "decimal"]:
        encoded_pubkey_bytes: bytes = encode_pubkey(
            pub=fast_multiply(a=G, n=privkey_decoded), formt=format
        )
        return encoded_pubkey_bytes  # encode_pubkey(pub=fast_multiply(a=G, n=privkey_decoded), formt=format)

    encoded_pubkey_bytes: bytes = encode_pubkey(
        fast_multiply(G, privkey_decoded), format.replace("wif", "hex")
    )
    return encoded_pubkey_bytes  # encode_pubkey(fast_multiply(G, privkey_decoded), format.replace("wif", "hex"))


def privkey_to_pubkey(privkey: Union[int, str]) -> str:
    """
    Derives the public key from a given private key.

    This function takes a private key in various formats and converts it to its corresponding
    public key. It handles different private key formats (decimal, binary, hexadecimal, WIF(Wallet Import Format))
    and ensures the private key is within the valid range.

    Args:
        privkey (Union[int, str]): The private key to convert. It can be an integer, a binary string,
                            a hexadecimal string, or a WIF(Wallet Import Format) string.

    Returns:
        str: The public key in the same format as the input private key, if possible.
            For WIF(Wallet Import Format) input, the output is in hexadecimal format.

    Raises:
        Exception: If the private key is invalid (e.g., outside the valid range).
    """
    format: str = get_privkey_format(privkey=privkey)
    privkey_decoded: int = decode_privkey(privkey=privkey, formt=format)

    if privkey_decoded >= N:
        raise Exception("Invalid privkey")

    if format in ["bin", "bin_compressed", "hex", "hex_compressed", "decimal"]:
        encoded_pubkey_bytes: str = encode_pubkey(
            pub=fast_multiply(a=G, n=privkey_decoded), formt=format
        )
        return encoded_pubkey_bytes

    encoded_pubkey_bytes: bytes = encode_pubkey(
        fast_multiply(G, privkey_decoded), format.replace("wif", "hex")
    )
    return encoded_pubkey_bytes


privtopub = privkey_to_pubkey

# privtopub_ = privkey_to_pubkey


def privkey_to_address_original(priv: str, magicbyte: int = 0) -> str:

    return pubkey_to_address(privkey_to_pubkey(privkey=priv), magicbyte)


def privkey_to_address(priv: str, magicbyte: int = 0) -> str:
    """
    Derives a Bitcoin,doge.ltc.. address from a given private key.

    This function takes a private key in various formats (decimal, binary, hexadecimal, WIF)
    and converts it to its corresponding Bitcoin address. It uses the `privkey_to_pubkey` function
    to obtain the public key and then the `pubkey_to_address` function to derive the address.

    Args:
        priv (str): The private key to convert. It can be an integer, a binary string,
                    a hexadecimal string, or a WIF(Wallet Import Format) string.
        magicbyte (int, optional): The magic byte to use for the address. Defaults to 0.

    Returns:
        str: The Bitcoin address derived from the given private key.
    """
    pub_address_address_Base58_string: str = pubkey_to_address(
        privkey_to_pubkey(privkey=priv), magicbyte
    )
    return pub_address_address_Base58_string  # pubkey_to_address(privkey_to_pubkey(privkey=priv), magicbyte)


privtoaddr = privkey_to_address


def neg_pubkey(pubkey):
    f = get_pubkey_format(pubkey)
    pubkey = decode_pubkey(pubkey, f)
    return encode_pubkey((pubkey[0], (P - pubkey[1]) % P), f)


def neg_privkey(privkey):
    f = get_privkey_format(privkey)
    privkey = decode_privkey(privkey, f)
    return encode_privkey((N - privkey) % N, f)


def subtract_pubkeys(p1, p2):
    f1, f2 = get_pubkey_format(p1), get_pubkey_format(p2)
    k2 = decode_pubkey(p2, f2)
    return encode_pubkey(fast_add(decode_pubkey(p1, f1), (k2[0], (P - k2[1]) % P)), f1)


def subtract_privkeys(p1, p2):
    f1, f2 = get_privkey_format(p1), get_privkey_format(p2)
    k2 = decode_privkey(p2, f2)
    return encode_privkey((decode_privkey(p1, f1) - k2) % N, f1)


# Hashes


# def bin_sha256(string: str) -> bytes:
#     return hashlib.sha256(string).digest()


def bin_hash160_original(string):
    intermed = bin_sha256(string)
    digest = ""
    try:
        digest = hashlib.new("ripemd160", intermed).digest()
    except:
        digest = RIPEMD160(intermed).digest()
    return digest


def bin_hash160(string: bytes) -> bytes:
    """
    Calculates the RIPEMD-160 hash of a byte string.

    This function takes a byte string and calculates its RIPEMD-160 hash.
    It first performs a SHA-256 hash on the input string and then applies
    RIPEMD-160 to the SHA-256 hash result.

    Args:
        string (bytes): The byte string to hash.

    Returns:
        bytes: The RIPEMD-160 hash of the input string as a byte array.
    """
    sha_256_hash: bytes = bin_sha256(str_or_bytes=string)
    RIPEMD_160_hash: bytes = bytes()
    try:
        RIPEMD_160_hash = hashlib.new("ripemd160", sha_256_hash).digest()
    except:
        RIPEMD_160_hash = RIPEMD160(sha_256_hash).digest()
    return RIPEMD_160_hash


def hash160(string):
    return safe_hexlify(bin_hash160(string))


def hex_to_hash160(s_hex):
    return hash160(binascii.unhexlify(s_hex))


# def bin_sha256(string) -> bytes:
#     binary_data: bytes = string if isinstance(string, bytes) else bytes(string, "utf-8")
#     return hashlib.sha256(binary_data).digest()


# def sha256(string: str) -> str:
#     return bytes_to_hex_string(bin_sha256(string))


def bin_sha256_original(string) -> bytes:
    """
    Calculates the SHA-256 hash of a string in binary format.

    Args:
        string: The string to hash. Can be either a bytes object or a string.
            If a string is provided, it will be encoded to UTF-8.

    Returns:
        The SHA-256 hash of the string as a bytes object.
    """
    binary_data: bytes = string if isinstance(string, bytes) else bytes(string, "utf-8")
    return hashlib.sha256(binary_data).digest()


def bin_sha256(str_or_bytes: str | bytes) -> bytes:
    """
    Calculates the SHA-256 hash of a string in binary format.

    Args:
        str_or_bytes(str | bytes): The string to hash. Can be either a bytes object or a string.
            If a string is provided, it will be encoded to UTF-8.

    Returns:
        The SHA-256 hash(bytes) of the string as a bytes object.
    """
    # bytes like ('\x04\x1fv=\x81\x01\r\xb8\xba0&\')
    binary_data: bytes = (
        str_or_bytes
        if isinstance(str_or_bytes, bytes)
        else bytes(str_or_bytes, "utf-8")
    )
    sha256_hash_object: hashlib.SHA256 = hashlib.sha256(
        binary_data
    )  # Create a SHA-256 hash object
    sha256_hash: bytes = sha256_hash_object.digest()  # Calculate the hash and store it
    return sha256_hash


def sha256(string: str) -> str:
    """
    Calculates the SHA-256 hash of a string in hexadecimal format.

    Args:
        string: The string to hash.

    Returns:
        The SHA-256 hash of the string as a hexadecimal string.
    """
    return bytes_to_hex_string(bin_sha256(string))


def bin_ripemd160(string):
    try:
        digest = hashlib.new("ripemd160", string).digest()
    except:
        digest = RIPEMD160(string).digest()
    return digest


def ripemd160(string):
    return safe_hexlify(bin_ripemd160(string))


def bin_dbl_sha256_original(s):
    bytes_to_hash = from_string_to_bytes(s)
    return hashlib.sha256(hashlib.sha256(bytes_to_hash).digest()).digest()


def bin_dbl_sha256(s: AnyStr) -> bytes:
    """
    Calculates the double SHA-256 hash of a string or byte string.

    This function takes a string or byte string 's' and calculates its double SHA-256 hash.
    It first converts the input to bytes if it's not already in bytes format. Then, it performs two consecutive SHA-256 hash operations on the bytes.
    The result is the double SHA-256 hash of the input, returned as a byte string.

    Args:
        s (AnyStr): The string or byte string to be hashed.

    Returns:
        bytes: The double SHA-256 hash of the input, represented as a byte string.

    Example:
        bin_dbl_sha256('hello')
        \\xe3\\xb0\\xc4\\x42\\x98\\xfc\\x1c\\x14\\x9a\\xfb\\xf4\\xc8\\x99\\x6f\\x3b\\xdb\\x73\\x28\\x1a\\x7a\\xfc\\xde\\xd3\\x34\\x89\\xd7\\xc6\\x11\\x59\\xc2\\x00\\x9d
    """
    bytes_to_hash: bytes = from_string_to_bytes(a=s)
    double_hash: bytes = hashlib.sha256(hashlib.sha256(bytes_to_hash).digest()).digest()
    return double_hash


def dbl_sha256(string):
    return safe_hexlify(bin_dbl_sha256(string))


def bin_slowsha(string):
    string = from_string_to_bytes(string)
    orig_input = string
    for i in range(100000):
        string = hashlib.sha256(string + orig_input).digest()
    return string


def slowsha(string):
    return safe_hexlify(bin_slowsha(string))


def hash_to_int_original(x):
    if len(x) in [40, 64]:
        return decode(x, 16)
    return decode(x, 256)


def hash_to_int(x: Union[bytes, str]) -> int:
    """
    Converts a hexadecimal or binary hash string to an integer.

    This function takes a hash string as input, either in hexadecimal or binary format, and converts it to an integer.
    It supports hash strings of lengths 40 (for 160-bit hashes) and 64 (for 256-bit hashes) in hexadecimal format.
    For other lengths, it assumes the input is in binary format.

    Args:
        x (Union[bytes, str]): The hash string to be converted, either in hexadecimal or binary format.

    Returns:
        int: The integer representation of the hash string.

    Example:
        >>> hash_to_int("0000000000000000000000000000000000000000")  # Binary
        0
        >>> hash_to_int("0000000000000000000000000000000000000000000000000000000000000000")  # Hexadecimal
        0
    """
    if len(x) in [40, 64]:
        return decode(x, 16)
    return decode(x, 256)


def num_to_var_int_original(x):
    x = int(x)
    if x < 253:
        return from_int_to_byte(x)
    elif x < 65536:
        return from_int_to_byte(253) + encode(x, 256, 2)[::-1]
    elif x < 4294967296:
        return from_int_to_byte(254) + encode(x, 256, 4)[::-1]
    else:
        return from_int_to_byte(255) + encode(x, 256, 8)[::-1]


def num_to_var_int(x: int) -> bytes:
    """
    Encodes an integer as a variable-length integer (varint).

    This function takes an integer 'x' and encodes it using the varint encoding scheme.
    Varint encoding allows for efficient representation of integers of varying sizes,
    where smaller integers require fewer bytes.
    It is commonly used in Bitcoin and other blockchain protocols for encoding data lengths.

    Args:
        x (int): The integer to be encoded as a varint.

    Returns:
        bytes: The varint encoded representation of the input integer.

    Example:
        >>> num_to_var_int(10)
        b'\n'
        >>> num_to_var_int(256)
        b'\xfd\x01\x00'

    More:
        The varint encoding scheme:
            is a method used to encode integers in a
            variable-length format. This encoding is particularly useful in scenarios
            where the range of integer values can vary significantly, allowing for
            efficient storage and transmission of data. Here are some key points
        about varint encoding:

            Variable Length: Varints can use anywhere from 1 to 10 bytes
            to represent an integer, depending on its size. Smaller numbers
            take up less space, while larger numbers require more bytes.

        Encoding Process:

            The most significant bit (MSB) of each byte is used as a continuation bit.
            If the MSB is set to 1, it indicates that there are more bytes to follow.
            If it is 0, it indicates that this is the last byte of the integer.
            The remaining 7 bits of each byte are used to store the actual value of the integer.
            Concatenation: One of the advantages of varint encoding is that
            multiple varints can be concatenated together without any additional
            overhead, making it efficient for encoding sequences of integers.

        Common Usage:
            Varint encoding is widely used in various data serialization formats,
            such as Protocol Buffers (protobuf), which is a method developed by
            Google for serializing structured data.

        Example:

            The integer 300 would be encoded in varint format as two bytes:
            0xAC 0x02. The first byte (0xAC) has the MSB set to 1, indicating that more bytes follow, and the second byte (0x02) contains the remaining bits of the integer.
            In summary, varint encoding is a flexible
            and efficient way to represent integers, especially when dealing
            with a mix of small and large values. Its variable-length nature
            helps save space in data storage and transmission.

    """
    if x < 253:
        return from_int_to_byte(x)
    elif x < 65536:
        return from_int_to_byte(253) + encode(x, 256, 2)[::-1]
    elif x < 4294967296:
        return from_int_to_byte(254) + encode(x, 256, 4)[::-1]
    else:
        return from_int_to_byte(255) + encode(x, 256, 8)[::-1]


# WTF, Electrum?
def electrum_sig_hash_original(message):
    padded = (
        b"\x18Bitcoin Signed Message:\n"
        + num_to_var_int(len(message))
        + from_string_to_bytes(message)
    )
    return bin_dbl_sha256(padded)


def electrum_sig_hash(message: bytes) -> bytes:
    """
    Calculates the Electrum signature hash for a given message.

    This function implements the Electrum signature hash algorithm,
    which is used to generate a unique hash of a message for signing purposes.
    It pre-pends a specific header to the message,
    including the message length encoded as a variable-length integer,
    and then applies double SHA-256 hashing.
    The resulting hash is used in the Electrum protocol
    for verifying signatures.

    Args:
        message (bytes): The message to be hashed.

    Returns:
        bytes: The Electrum signature hash of the message.

    Example:
        >>> message = b"Hello, world!"
        >>> sig_hash = electrum_sig_hash(message)
        >>> print(sig_hash.hex())
    """
    padded = (
        b"\x18Bitcoin Signed Message:\n"
        + num_to_var_int(len(message))
        + from_string_to_bytes(message)
    )
    return bin_dbl_sha256(padded)


def random_key():
    # Gotta be secure after that java.SecureRandom fiasco...
    entropy = (
        random_string(32)
        + str(random.randrange(2**256))
        + str(int(time.time() * 1000000))
    )
    return sha256(entropy)


def random_electrum_seed():
    # entropy = os.urandom(32) \ # fails in Python 3, hence copied from random_key()
    entropy = (
        random_string(32)
        + str(random.randrange(2**256))
        + str(int(time.time() * 1000000))
    )
    return sha256(entropy)[:32]


# Encodings


def b58check_to_bin_original(inp: str) -> Tuple[int, bytes]:
    leadingzbytes: int = len(re.match("^1*", inp).group(0))
    data = b"\x00" * leadingzbytes + changebase(string=inp, frm=58, to=256)
    assert bin_dbl_sha256(s=data[:-4])[:4] == data[-4:]
    magicbyte = data[0]
    return magicbyte, data[1:-4]


def b58check_to_bin(inp: str) -> Tuple[int, bytes]:
    """
    Converts a Base58Check encoded string to a binary representation.

    Args:
        inp (str): The Base58Check encoded string.

    Returns:
        Tuple[int, bytes]: A tuple containing the magic byte and the decoded binary data.

    Raises:
        AssertionError: If the checksum of the input string is invalid.

    Examples:
        >>> b58check_to_bin("16UjcYNBG9j16sxo88v5z83o5MYYxF" )

    More:
        break down data[1:-4] in the context of the b58check_to_bin function:

        Understanding the Code:

            data:
                This variable holds the binary representation of the
                Base58Check encoded string. It's a byte string,
                which means it's a sequence of bytes (think of each byte as a
                number between 0 and 255).

            data[1:-4]:
                This is a slice of the data byte string.
                It means:

                    1:
                        Start at the second element of the data byte string
                        (remember, Python indexing starts at 0).
                    -4:
                        End at the fourth element from the end of the data byte string.

        Why this Slice?:

            The b58check_to_bin function is designed to
            decode Base58Check encoded strings.
            The structure of a Base58Check encoded string is:

                Magic Byte:
                    This identifies the type(btc,doge,ltc...) of data being encoded.
                Data:
                    The actual data being encoded.
                Checksum:
                    A 4-byte checksum to ensure the data's integrity.

                Therefore:

                    data[0] is the magic byte.
                    data[1:-4] represents the actual data, excluding the magic byte and the checksum.
                    data[-4:] represents the 4-byte checksum.
        In Summary:

            The slice data[1:-4] extracts the decoded
            data from the data byte string, removing the magic
            byte and checksum. This is the actual information
            that was originally encoded.

    """
    from . import py3specials

    # leading_ones_count: int = len(re.match("^1*", inp).group(0))
    leading_ones_count: int = py3specials.count_leading_ones(binary_string=inp)
    data: bytes = b"\x00" * leading_ones_count + changebase(string=inp, frm=58, to=256)
    # assert bin_dbl_sha256(s=data[:-4])[:4] == data[-4:]
    # Calculate the checksum based on the data (excluding the existing checksum)

    # Remove the last four bytes from data
    truncated_data: bytes = data[:-4]
    double_sha256_hash: bytes = py3specials.bin_dbl_sha256(s=truncated_data)
    # checksum_calculated = bin_dbl_sha256(s=data[:-4])[:4]
    # Extract the first four bytes of the double_sha256_hash
    checksum_calculated = double_sha256_hash[:4]
    # checksum_calculated = py3specials.bin_dbl_sha256(s=data[:-4])[:4]

    # Extract the existing checksum from the data(extracting the last four bytes of the data)
    checksum_stored = data[-4:]

    # Compare the calculated checksum with the stored checksum
    if checksum_calculated != checksum_stored:
        raise ValueError(
            f"Checksum mismatch! Data might be corrupted. at file: {__file__} function: {b58check_to_bin.__name__}"
        )

    #
    magicbyte: int = data[0]
    # (removed magic byte and checksum) (the magic)
    actuall_data_without_Magic_byte_and_checksum: bytes = data[1:-4]
    return magicbyte, actuall_data_without_Magic_byte_and_checksum


def get_version_byte_original(inp):
    leadingzbytes = len(re.match("^1*", inp).group(0))
    data = b"\x00" * leadingzbytes + changebase(string=inp, frm=58, to=256)
    assert bin_dbl_sha256(s=data[:-4])[:4] == data[-4:]
    return ord(data[0])


def get_version_byte(inp: str) -> int:
    """
    Determines the version byte for a given input string.

    This function takes a string as input and calculates its version byte. It first counts the number of leading zeros in the input string, then converts the input string from base-58 to base-256. It then verifies the checksum of the resulting data and returns the first byte of the data as the version byte.

    Args:
        inp: The input string in base-58.

    Returns:
        The version byte as an integer.
    """
    leadingzbytes: int = len(re.match("^1*", inp).group(0))
    data: bytes = b"\x00" * leadingzbytes + changebase(string=inp, frm=58, to=256)
    assert bin_dbl_sha256(s=data[:-4])[:4] == data[-4:]
    version_byte: int = ord(data[0])
    return version_byte


def hex_to_b58check(inp, magicbyte=0):
    return bin_to_b58check(binascii.unhexlify(inp), magicbyte)


def b58check_to_hex_original(inp) -> Tuple[int, str]:
    magicbyte, bin = b58check_to_bin(inp=inp)
    return magicbyte, safe_hexlify(bin)


def b58check_to_hex(inp) -> Tuple[int, str]:
    """
    Decodes a Base58Check-encoded string to its hexadecimal representation.

    Args:
        inp (str): The Base58Check-encoded string to decode.

    Returns:
        Tuple[int, str]: A tuple containing the magic byte (as an integer) and the decoded binary data as a hexadecimal string.

    Example:
        >>> b58check_to_hex("16UjcYNBG9b4B19Y8Wqi68hdm7")
        (0, '0014c016a7e458c28d331a482163878819756786')

    Explanation:

    **1. Base58Check Decoding:**
        The function first calls `b58check_to_bin()` to decode
        the Base58Check-encoded string (`inp`) into its raw
        binary representation. This returns a tuple containing
        the magic byte (as an integer) and the decoded binary data (as bytes).

    **2. Hexadecimal Conversion:**
        The decoded binary data is then converted to a
        hexadecimal string using `safe_hexlify()`.

    **3. Return Values:**
        The function returns a tuple containing:
            - The magic byte (as an integer).
            - The decoded binary data as a hexadecimal string.

    This function is useful for converting
    Base58Check-encoded data, commonly used in Bitcoin
    and other cryptocurrencies, to a more easily
    readable hexadecimal format.
    """
    from . import py3specials

    magicbyte: int
    decoded_binary_data: bytes
    magicbyte, decoded_binary_data = b58check_to_bin(inp=inp)
    decoded_binary_data_as_hexadecimal_string: str = py3specials.safe_hexlify(
        a=decoded_binary_data
    )
    return magicbyte, decoded_binary_data_as_hexadecimal_string


def pubkey_to_hash_original(pubkey: PubKeyType):
    if isinstance(pubkey, (list, tuple)):
        pubkey = encode_pubkey(pub=pubkey, formt="bin")
    if len(pubkey) in [66, 130]:
        return bin_hash160(binascii.unhexlify(pubkey))
    return bin_hash160(pubkey)


def pubkey_to_hash_original(pubkey: PubKeyType):

    if isinstance(pubkey, (list, tuple)):
        pubkey_encoded = encode_pubkey(pub=pubkey, formt="bin")
        return pubkey_encoded
    if len(pubkey) in [66, 130]:
        return bin_hash160(binascii.unhexlify(pubkey))
    return bin_hash160(pubkey)


# PubKeyType = Union[list, tuple, str, bytes]


def pubkey_to_hash(
    pubkey: Union[str, bytes, Tuple[int, int], List[int]],
) -> bytes:
    """
    Calculates the hash160 of a public key.

    This function takes a public key in various formats and calculates its hash160.
    It supports different public key formats, including decimal, binary, hexadecimal,
    and compressed versions.

    Args:
        pubkey (Union[str, bytes, Tuple[int, int], List[int]]): The public key to hash.
            It can be a string (hexadecimal or binary), a byte array, a tuple of integers
            representing the X and Y coordinates, or a list of integers.

    Returns:
        bytes: The hash160 of the public key as a byte array.
    """
    if isinstance(pubkey, (list, tuple)):
        pubkey_encoded: bytes = encode_pubkey(pub=pubkey, formt="bin")
        return pubkey_encoded
    elif isinstance(pubkey, str) and len(pubkey) in [66, 130]:
        return bin_hash160(binascii.unhexlify(pubkey))
    elif isinstance(pubkey, bytes):
        return bin_hash160(pubkey)
    else:
        raise ValueError("Invalid public key format")
    # return bin_hash160(pubkey_encoded)


def pubkey_to_hash_hex_original(pubkey: str) -> str:
    return safe_hexlify(pubkey_to_hash(pubkey))


def pubkey_to_hash_hex(pubkey: str) -> str:
    """
    Converts a public key to its SHA-256 hash in hexadecimal format.

    Args:
        pubkey (str): The public key in hexadecimal format.

    Returns:
        str: The SHA-256 hash of the public key in hexadecimal format.
    """
    return safe_hexlify(pubkey_to_hash(pubkey))


def pubkey_to_address_original(pubkey: str, magicbyte: int = 0) -> str:
    pubkey_RIPEMD_160_hash: bytes = pubkey_to_hash(pubkey=pubkey)
    address_Base58_string: str = bin_to_b58check(
        inp=pubkey_RIPEMD_160_hash,
        magicbyte=magicbyte,
    )
    return address_Base58_string


def pubkey_to_address(pubkey: str, magicbyte: int = 0) -> str:
    """
    Converts a public key to a Bitcoin address using RIPEMD-160 hashing and Base58Check encoding.

    This function takes a public key string as input and performs the following steps:

    1. **Hashing:** It hashes the public key using RIPEMD-160, resulting in a 20-byte hash.
    2. **Base58Check Encoding:** It encodes the hash using Base58Check with the specified magicbyte.
       - **Magicbyte:** This byte is prepended to the hash before encoding. It is typically used to identify the network (e.g., 0 for Bitcoin mainnet, 111 for testnet).

    Args:
        pubkey (str): The public key in hexadecimal format.
        magicbyte (int, optional): The magicbyte to use for Base58Check encoding. Defaults to 0 (Bitcoin mainnet).

    Returns:
        str:(address_Base58_string) The Bitcoin address derived from the public key.

    Example:
        >>> pubkey = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
        >>> pubkey_to_address(pubkey)
        '16UjcYNBg9j16sxo8tTDgG8PxJ5W7nL6'
    """
    pubkey_RIPEMD_160_hash: bytes = pubkey_to_hash(pubkey=pubkey)
    address_Base58_string: str = bin_to_b58check(
        inp=pubkey_RIPEMD_160_hash,
        magicbyte=magicbyte,
    )
    return address_Base58_string


pubtoaddr = pubkey_to_address


def is_privkey(priv):
    try:
        get_privkey_format(privkey=priv)
        return True
    except:
        return False


def is_pubkey(pubkey):
    try:
        get_pubkey_format(pubkey)
        return True
    except:
        return False


# EDCSA


def encode_sig_original(v, r, s):
    vb, rb, sb = from_int_to_byte(v), encode(val=r, base=256), encode(val=s, base=256)

    result = base64.b64encode(
        vb + b"\x00" * (32 - len(rb)) + rb + b"\x00" * (32 - len(sb)) + sb
    )
    return result if is_python2 else str(result, "utf-8")


def encode_sig(v: int, r: int, s: int) -> str:
    """
    Encodes an ECDSA signature into a base64-encoded string.

    This function takes the components of an ECDSA signature (v, r, s) and encodes them into a base64-encoded string.
    It first converts the v component to a byte, then pads the r and s components to 32 bytes each.
    Finally, it concatenates the components and encodes the resulting byte string using base64.

    Args:
        v (int): The recovery ID, indicating the public key used for signing.
        r (int): The x-coordinate of the signature point.
        s (int): The y-coordinate of the signature point.

    Returns:
        str: The base64-encoded string representing the ECDSA signature.

    Example:
        >>> encode_sig(1, 0x1234567890abcdef, 0x9876543210fedcba)
        'AQAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
    """
    vb, rb, sb = from_int_to_byte(v), encode(val=r, base=256), encode(val=s, base=256)

    result = base64.b64encode(
        vb + b"\x00" * (32 - len(rb)) + rb + b"\x00" * (32 - len(sb)) + sb
    )
    return result if is_python2 else str(result, "utf-8")


def decode_sig_original(sig):
    bytez = base64.b64decode(sig)
    return from_byte_to_int(bytez[0]), decode(bytez[1:33], 256), decode(bytez[33:], 256)


def decode_sig(sig: str) -> tuple[int, int, int]:
    """
    Decodes a base64-encoded ECDSA signature into its components.

    This function takes a base64-encoded ECDSA signature and decodes it into its individual components:
    - v (recovery ID): Indicates the public key used for signing.
    - r (x-coordinate): The x-coordinate of the signature point.
    - s (y-coordinate): The y-coordinate of the signature point.

    Args:
        sig (str): The base64-encoded ECDSA signature.

    Returns:
        tuple[int, int, int]: A tuple containing the decoded v, r, and s components.

    Example:
        >>> decode_sig('AQAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=')
        (1, 18454937592756957144087016996894538384, 39569436408858239114555199769764197840)
    """
    bytez = base64.b64decode(sig)
    return from_byte_to_int(bytez[0]), decode(bytez[1:33], 256), decode(bytez[33:], 256)


# https://tools.ietf.org/html/rfc6979#section-3.2


def deterministic_generate_k_original(msghash, priv):
    v = b"\x01" * 32
    k = b"\x00" * 32
    priv = encode_privkey(priv, "bin")
    msghash = encode(hash_to_int(msghash), 256, 32)
    k = hmac.new(k, v + b"\x00" + priv + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + priv + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    return decode(hmac.new(k, v, hashlib.sha256).digest(), 256)


def deterministic_generate_k(msghash: bytes, priv: bytes) -> int:
    """
    Deterministically generates a nonce 'k' for ECDSA signing using HMAC-SHA256.

    This function implements a deterministic nonce generation algorithm based on HMAC-SHA256.
    It uses the message hash, the private key, and a series of HMAC operations to produce a unique and unpredictable nonce 'k'.
    This deterministic approach ensures that the same nonce is generated for the same message and private key,
    contributing to the security of the ECDSA signature process.

    Args:
        msghash (bytes): The message hash to be signed.
        priv (bytes): The private key used for signing.

    Returns:
        int: The deterministically generated nonce 'k' as an integer.


    More:
        https://tools.ietf.org/html/rfc6979#section-3.2
        import hmac
        import hashlib

    """
    v = b"\x01" * 32
    k = b"\x00" * 32
    priv = encode_privkey(priv, "bin")
    msghash = encode(hash_to_int(msghash), 256, 32)
    k = hmac.new(k, v + b"\x00" + priv + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + priv + msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    return decode(hmac.new(k, v, hashlib.sha256).digest(), 256)


def ecdsa_raw_sign_original(msghash, priv):

    z = hash_to_int(msghash)
    k = deterministic_generate_k(msghash, priv)

    r, y = fast_multiply(G, k)
    s = inv(k, N) * (z + r * decode_privkey(priv)) % N

    v, r, s = 27 + ((y % 2) ^ (0 if s * 2 < N else 1)), r, s if s * 2 < N else N - s
    if "compressed" in get_privkey_format(priv):
        v += 4
    return v, r, s


def ecdsa_raw_sign(msghash: bytes, private_key: bytes) -> Tuple[int, int, int]:
    """
    Signs a message hash using ECDSA with the given private key.

    (Elliptic Curve Digital Signature Algorithm (ECDSA)  (https://datatracker.ietf.org/doc/html/rfc6979#section-3.2)  )

    This function implements the ECDSA signature algorithm using the
    provided message hash and private key.
    It utilizes deterministic generation of the nonce 'k'
    and performs modular arithmetic operations to compute the signature components (r, s).
    The signature is then encoded in a standard format,
    including a
    recovery ID 'v' to allow for public key recovery.

    Args:
        msghash (bytes): The message hash to be signed.
        priv (bytes): The private key used for signing.

    Returns:
        tuple(int, int, int):
            A tuple containing the signature components (v, r, s):
                v(int):
                    x-coordinate of the point R on the elliptic curve
                r(int):
                    first part of the signature. This is the x-coordinate of the point R on
                    the elliptic curve
                s(int):
                    The second part of the signature. This component is calculated
                    using the private key, the message hash, and the nonce k.
    Raises:
        ValueError: If the private key format is invalid.

    Example:
        >>> msghash = sha256(b"Hello, world!")
        >>> priv = b"your_private_key"
        >>> v, r, s = ecdsa_raw_sign(msghash, priv)
        >>> print(f"Signature: (v: {v}, r: {r}, s: {s})")
    More:
        Description:
            Certainly The Elliptic Curve Digital Signature Algorithm (ECDSA)
            is a widely used cryptographic algorithm that provides a method
            for signing messages and verifying signatures. It is particularly
            popular in blockchain technologies and secure communications due to
            its efficiency and strong security properties.

        Key Components of ECDSA:
        Private Key:
            A secret number that is used to generate the signature.
        Public Key:
            A point on the elliptic curve derived from the private key, which can be shared publicly.
        Message Hash:
            A fixed-size representation of the message being signed, typically generated using a hash function (like SHA-256).
        Signature:
            The output of the signing process, which consists of two components: r and s.
        The Signature Process
        When signing a message using ECDSA, the following steps are typically followed:

        Generate a Random Nonce (k):
            A random number is generated for each signature.
            This nonce must be unique for every signature to ensure security.
            Calculate r:
                Using the nonce and the elliptic curve,
                a point is calculated, and its x-coordinate is
                reduced modulo the curve's order to produce r.
            Calculate s:
                The signature component s is calculated using the private key,
                the message hash, and the nonce.
            Recovery ID (v):
                This is an additional component that helps in recovering the
                public key from the signature.
                It indicates which of the two possible public
                keys corresponds to the signature.

        Understanding the Recovery ID (v)
        The recovery ID, often denoted as v,
        is crucial for reconstructing the public key
        from the signature. Heres how it works:

            Bit from Y Coordinate:
                The recovery ID is derived from the y-coordinate of the public key. Specifically, it takes the least significant bit of the y-coordinate.
            Adjustment for s:
                If the value of s is greater than half of the curves
                order (denoted as N), the recovery ID is adjusted by flipping the bit.
                This adjustment helps in distinguishing between the two possible public keys that could correspond to the same signature.

            The recovery ID v is typically one of the following values:
            0 or 1:
                Indicates the parity of the y-coordinate of the public key.
            2 or 3:
                Indicates the parity and whether the value of s was adjusted.

        Example of ECDSA Signature Components
        When you generate a signature using ECDSA, you will have:

            r: The first part of the signature. This is the x-coordinate of the point
                R on the elliptic curve
            s: The second part of the signature. This component is calculated
                using the private key, the message hash, and the nonce k.

            v: The recovery ID, which helps in recovering the public key.
                This is the recovery ID, which indicates the parity of
                the y-coordinate of the public key and whether the value of s
                s was adjusted.

        Conclusion:
            ECDSA is a powerful and efficient algorithm for
            digital signatures, and the inclusion of the recovery ID
            v enhances its utility by allowing the recovery of the
            public key from the signature. This feature is
            particularly useful in scenarios where the public
            key is not known in advance, such as in cryptocurrency transactions.
    """
    z: int = hash_to_int(x=msghash)
    k = deterministic_generate_k(msghash=msghash, priv=private_key)

    r, y = fast_multiply(a=G, n=k)
    s = inv(k, N) * (z + r * decode_privkey(private_key)) % N
    # v Recovery ID: Indicates the parity of the y-coordinate of
    # the public key and whether 's' was adjusted.
    v: int = 27 + ((y % 2) ^ (0 if s * 2 < N else 1))
    r: int = (
        r  # First component of the signature, calculated from the nonce and the elliptic curve.
    )
    s: int = (
        s if s * 2 < N else N - s
    )  # Second component of the signature, calculated using the private key, message hash, and nonce.
    if "compressed" in get_privkey_format(private_key):
        v += 4
    return v, r, s


def ecdsa_sign_original(msg, priv, coin):
    v, r, s = ecdsa_raw_sign(msghash=electrum_sig_hash(msg), private_key=priv)
    sig = encode_sig(v, r, s)
    assert ecdsa_verify(
        msg, sig, privtopub(priv), coin
    ), "Bad Sig!\t %s\nv = %d\n,r = %d\ns = %d" % (sig, v, r, s)
    return sig


def ecdsa_sign(
    msg: bytes,
    priv: int,
    # coin: BaseCoin,
    coin,
) -> str:
    """
    Signs a message using ECDSA with the provided private key and coin type.

    This function performs ECDSA signing using the provided private key and coin type.
    It first calculates the message hash using the `electrum_sig_hash` function.
    Then, it uses the `ecdsa_raw_sign` function to generate the raw signature components (v, r, s).
    Finally, it encodes the signature using the `encode_sig` function and verifies the signature using the `ecdsa_verify` function.

    Args:
        msg (bytes): The message to be signed.
        priv (int): The private key used for signing.
        coin (BaseCoin): Base implementation of crypto coin class, e.g., 'btc', 'eth'.

    Returns:
        str: The base64-encoded ECDSA signature.

    Raises:
        AssertionError: If the signature verification fails.

    Example:
        >>> ecdsa_sign(b'Hello world!', 0x1234567890abcdef, 'btc')
        'AQAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
    """

    v: int
    r: int
    s: int
    v, r, s = ecdsa_raw_sign(
        msghash=electrum_sig_hash(message=msg),
        private_key=priv,
    )
    sig: str = encode_sig(
        v=v,
        r=r,
        s=s,
    )
    assert ecdsa_verify(
        msg=msg,
        sig=sig,
        pub=privtopub(privkey=priv),
        coin=coin,
    ), "Bad Sig!\t %s\nv = %d\n,r = %d\ns = %d" % (sig, v, r, s)
    return sig


def ecdsa_raw_verify_original(msghash, vrs, pub):
    v, r, s = vrs

    w = inv(s, N)
    z = hash_to_int(msghash)

    u1, u2 = z * w % N, r * w % N
    x, y = fast_add(
        fast_multiply(a=G, n=u1), fast_multiply(a=decode_pubkey(pub=pub), n=u2)
    )
    return bool(r == x and (r % N) and (s % N))


def ecdsa_raw_verify(
    msghash: bytes,
    vrs: Tuple[int, int, int],
    pub: Union[bytes, str],
) -> bool:
    """
    Verifies an ECDSA signature against a given public key.

    This function performs raw ECDSA signature verification using the
    provided message hash, signature components (v, r, s), and public key.
    It calculates the expected x-coordinate of the public key
    based on the signature and compares it to the provided public key.

    The verification process involves the following steps:

    1. **Extract signature components:**
        - `v`: The recovery parameter, indicating the sign of the y-coordinate of the public key.
        - `r`: The x-coordinate of the point on the elliptic curve where the signature was generated.
        - `s`: The scalar value used to sign the message hash.

    2. **Calculate the modular inverse of 's':**
        - `w`: The modular inverse of `s` modulo the curve order `N`, calculated using the `inv` function.

    3. **Convert the message hash to an integer:**
        - `z`: The message hash converted to an integer using the `hash_to_int` function.

    4. **Calculate the 'u1' and 'u2' values:**
        - `u1`: Calculated as `z * w % N`.
        - `u2`: Calculated as `r * w % N`.

    5. **Calculate the expected public key point:**
        - `x, y`: The coordinates of the expected public key point calculated by adding the results of two point multiplications:
            - `fast_multiply(a=G, n=u1)`: Multiplication of the generator point `G` by `u1`.
            - `fast_multiply(a=decode_pubkey(pub=pub), n=u2)`: Multiplication of the decoded public key `pub` by `u2`.

    6. **Compare the calculated 'x' coordinate with the provided 'r':**
        - If the calculated `x` coordinate matches the provided `r` and both `r` and `s` are non-zero modulo `N`, the signature is considered valid.

    Args:
        msghash (bytes): The message hash that was signed.
        vrs (Tuple[int, int, int]): The ECDSA signature components (v, r, s).
        pub (Union[bytes, str]): The public key to verify against.

    Returns:
        bool: True if the signature is valid for the public key, False otherwise.


    More:
        In ECDSA signature verification,
        u1 and u2 are crucial values used to calculate the
        expected public key point based on the signature.

        Here's a breakdown of their role and how they're calculated:

            1. Purpose:

                u1 and u2 are scalar values that act as multipliers
                in point multiplication operations on the elliptic curve.
                They are used to combine the message hash (z) and the
                signature components (r and s) to derive the expected public key point.

            2. Calculation:

                u1 = (z * w) % N
                u2 = (r * w) % N
                Where: - z:
                    Integer representation of the message hash.
                        - w:
                            Modular inverse of s modulo the curve order N (w = inv(s, N)).
                        - N:
                            The order of the elliptic curve group. - %: Modulo operator.

            3. Significance:

                u1 is used to multiply the generator point G of the elliptic curve.
                This represents the contribution of the message hash to the public key calculation.
                u2 is used to multiply the public key pub provided for verification.
                This represents the contribution of the signature component r to the public key calculation.

            4. Verification Process:

                The calculated public key point (x, y) is obtained by adding the results of two point multiplications:
                    fast_multiply(a=G, n=u1):
                        Multiplication of the generator point G by u1.
                    fast_multiply(a=decode_pubkey(pub=pub), n=u2):
                        Multiplication of the decoded public key pub by u2.

        The verification process then compares the x coordinate of the
        calculated public key point with the r value from the signature.
        If they match, and other conditions are met, the signature is considered valid.
        In essence, u1 and u2 act as weights that combine the message
        hash and signature components to derive the expected public key point.
        This allows the verification process to determine if the signature was
        generated using the correct private key associated with the provided public key.
    And More:
        about r % N != 0! It's a crucial part of ECDSA signature verification, and understanding it is essential.

        Let's break it down:

        % (Modulo Operator): The modulo operator gives you the remainder after a division. For example, 10 % 3 equals 1 because 10 divided by 3 leaves a remainder of 1.

        N (Curve Order): In ECDSA, N represents the order of the elliptic curve used. It's a large prime number that defines the size of the group of points on the curve.

        r % N != 0 (The Condition): This expression checks if the remainder of r divided by N is not equal to zero.

        Why is this important?

        In ECDSA, the signature components r and s must lie within the range of 1 to N-1. This ensures that they represent valid points on the elliptic curve.

        If r % N == 0: This means r is a multiple of N, which places it outside the valid range. It indicates an invalid signature.
        In simpler terms: Think of N as the number of spaces on a circular track. The signature components r and s need to land on one of these spaces. If they land on the starting point (which is equivalent to a remainder of 0 after dividing by N), it's an invalid signature.

        Example:

        Imagine N is 11 (a small example). Valid values for r would be 1, 2, 3, ..., 10. But if r is 11, 22, 33, etc., it's outside the valid range because it's a multiple of 11.

    """
    v: int
    r: int
    s: int
    v, r, s = vrs

    w: int = inv(s, N)
    z: int = hash_to_int(msghash)

    u1: int = z * w % N
    u2: int = r * w % N
    x: int
    y: int
    x, y = fast_add(
        fast_multiply(a=G, n=u1), fast_multiply(a=decode_pubkey(pub=pub), n=u2)
    )
    is_signature_valid: bool = False  # bool(r == x and (r % N) and (s % N))
    # (r % N  means r divided with N)
    if r == x and r % N != 0 and s % N != 0:
        is_signature_valid = True
    else:
        is_signature_valid = False
    return is_signature_valid


# For BitcoinCore, (msg = addr or msg = "") be default
def ecdsa_verify_addr_original(
    msg,
    sig,
    addr,
    # coin: BaseCoin,
    coin,
):
    assert coin.is_address(addr=addr)
    Q: str = ecdsa_recover(msg=msg, sig=sig)
    magic: int = get_version_byte(inp=addr)
    return (addr == coin.pubtoaddr(Q, int(magic))) or (
        addr == coin.pubtoaddr(compress(Q), int(magic))
    )


# For BitcoinCore, (msg = addr or msg = "") be default
def ecdsa_verify_addr(
    msg: str,
    sig: str,
    addr: str,
    # coin: BaseCoin,
    coin,
) -> bool:
    """
    Verifies an ECDSA signature against a given address.

    Args:
        msg: The message that was signed.
        sig: The ECDSA signature.
        addr: The address to verify against.
        coin: The coin type (e.g., Bitcoin, Litecoin).

    Returns:
        True if the signature is valid for the address, False otherwise.
    """
    assert coin.is_address(addr=addr)
    Q: str = ecdsa_recover(msg=msg, sig=sig)
    magic: int = get_version_byte(inp=addr)

    # Variables for clarity
    pubkey_uncompressed: Tuple[str, int] = Q, int(magic)
    pubkey_compressed: Tuple[str, int] = compress(pubkey=Q), int(magic)

    # uncompressed_public_key: str = coin.pubtoaddr(Q, int(magic))
    # compressed_public_key: str = coin.pubtoaddr(compress(Q), int(magic))
    uncompressed_address: str = coin.pubtoaddr(pubkey_uncompressed)
    compressed_address: str = coin.pubtoaddr(pubkey_compressed)

    if addr == uncompressed_address or addr == compressed_address:
        return True
    else:
        return False


def ecdsa_verify_original(
    msg,
    sig,
    pub,
    # coin: BaseCoin,
    coin,
):
    is_signature_valid: bool = False
    if coin.is_address(addr=pub):
        is_signature_valid = ecdsa_verify_addr(
            msg=msg,
            sig=sig,
            addr=pub,
            coin=coin,
        )

        return is_signature_valid

    is_signature_valid = ecdsa_raw_verify(
        msghash=electrum_sig_hash(message=msg),
        vrs=decode_sig(sig=sig),
        bub=pub,
    )
    return is_signature_valid


def ecdsa_verify(
    msg: str,
    sig: str,
    pub: Union[str, bytes],
    # coin: BaseCoin,
    coin,
) -> bool:
    """
    Verifies an ECDSA signature against a given public key.

    This function first checks if the public key is an address.
    If so, it uses the coin-specific address verification method.
    Otherwise, it performs raw ECDSA
    signature verification using the provided message,
    signature, and public key.

    Args:
        msg (str): The message that was signed.
        sig (str): The ECDSA signature.
        pub (Union[str, bytes]): The public key to verify against.
        coin (BaseCoin): The coin object representing the cryptocurrency.

    Returns:
        bool: True if the signature is valid for the public key, False otherwise.
    """
    is_signature_valid: bool = False
    if coin.is_address(addr=pub):
        is_signature_valid = ecdsa_verify_addr(
            msg=msg,
            sig=sig,
            addr=pub,
            coin=coin,
        )

        return is_signature_valid

    is_signature_valid = ecdsa_raw_verify(
        msghash=electrum_sig_hash(message=msg),
        vrs=decode_sig(sig=sig),
        pub=pub,
    )
    return is_signature_valid


def ecdsa_raw_recover_original(msghash, vrs):
    v, r, s = vrs
    x = r
    xcubedaxb = (x * x * x + A * x + B) % P
    beta = pow(xcubedaxb, (P + 1) // 4, P)
    y = beta if v % 2 ^ beta % 2 else (P - beta)
    # If xcubedaxb is not a quadratic residue, then r cannot be the x coord
    # for a point on the curve, and so the sig is invalid
    if (xcubedaxb - y * y) % P != 0 or not (r % N) or not (s % N):
        return False
    z = hash_to_int(x=msghash)
    Gz = jacobian_multiply(a=(Gx, Gy, 1), n=(N - z) % N)
    XY = jacobian_multiply(a=(x, y, 1), n=s)
    Qr = jacobian_add(Gz, XY)
    Q = jacobian_multiply(Qr, inv(r, N))
    Q = from_jacobian(Q)

    # if ecdsa_raw_verify(msghash, vrs, Q):
    return Q
    # return False


def ecdsa_raw_recover(msghash: bytes, vrs: Tuple[int, int, int]) -> Tuple[int, int]:
    """
    Recovers the public key from an ECDSA signature and message hash.

    This function implements the ECDSA signature recovery algorithm, allowing you to reconstruct the public key used to sign a message given the message hash and the signature (v, r, s).

    Args:
        msghash: The message hash as a byte string.
        vrs: A tuple containing the signature components: (v, r, s).
            * **v:** The recovery ID, indicating which of the four possible public keys was used to sign the message.
            * **r:** The R component of the signature, a large integer representing the X coordinate of a point on the elliptic curve.
            * **s:** The S component of the signature, another large integer.

    Returns:
        A tuple representing the recovered public key (x, y) as integers, or `False` if the signature is invalid.
    """
    v: int
    r: int
    s: int
    v, r, s = vrs
    x: int = r
    xcubedaxb: int = (x * x * x + A * x + B) % P
    beta: int = pow(xcubedaxb, (P + 1) // 4, P)
    y: int = beta if v % 2 ^ beta % 2 else (P - beta)
    # If xcubedaxb is not a quadratic residue, then r cannot be the x coord
    # for a point on the curve, and so the sig is invalid
    if (xcubedaxb - y * y) % P != 0 or not (r % N) or not (s % N):
        return False
    z: int = hash_to_int(x=msghash)
    Gz: Tuple[int, int, int] = jacobian_multiply(a=(Gx, Gy, 1), n=(N - z) % N)
    XY: Tuple[int, int, int] = jacobian_multiply(a=(x, y, 1), n=s)
    Qr: Tuple[int, int, int] = jacobian_add(Gz, XY)
    Q: Tuple[int, int, int] = jacobian_multiply(Qr, inv(r, N))
    Q: Tuple[int, int] = from_jacobian(Q)

    return Q


def ecdsa_recover_original(msg, sig):
    v: int
    r: int
    s: int
    v, r, s = decode_sig(sig=sig)
    Q: Tuple[int, int] = ecdsa_raw_recover(
        msghash=electrum_sig_hash(message=msg),
        vrs=(v, r, s),
    )
    return (
        encode_pubkey(
            pub=Q,
            formt="hex_compressed",
        )
        if v >= 31
        else encode_pubkey(
            pub=Q,
            formt="hex",
        )
    )


def ecdsa_recover(msg: str, sig: str) -> str:
    """
    Recovers the public key from an ECDSA signature and message.

    This function takes a message and its corresponding ECDSA
    signature and recovers the public key that was used to sign
    the message. It uses the `ecdsa_raw_recover` function to perform
    the actual recovery process and then encodes the recovered public
    key in the appropriate format based on the signature's `v` value.

    Args:
        msg: The message that was signed.
        sig: The ECDSA signature.

    Returns:
        The recovered public key as a hexadecimal string, either
        in compressed or uncompressed format depending on the
        `v` value of the signature.
    """
    v: int
    r: int
    s: int
    v, r, s = decode_sig(sig=sig)
    Q: Tuple[int, int] = ecdsa_raw_recover(
        msghash=electrum_sig_hash(message=msg),
        vrs=(v, r, s),
    )
    return (
        encode_pubkey(
            pub=Q,
            formt="hex_compressed",
        )
        if v >= 31
        else encode_pubkey(
            pub=Q,
            formt="hex",
        )
    )


# add/subtract
def add(p1, p2):
    if is_privkey(p1):
        return add_privkeys(p1, p2)
    else:
        return add_pubkeys(p1, p2)


def subtract(p1, p2):
    if is_privkey(p1):
        return subtract_privkeys(p1, p2)
    else:
        return subtract_pubkeys(p1, p2)


hash160Low = (
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)
hash160High = (
    b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
)


def script_to_scripthash_bytes_original(script) -> bytes:
    return bin_sha256(str_or_bytes=safe_from_hex(s=script))


def script_to_scripthash_bytes(script: Union[str, bytes]) -> bytes:
    """
    Calculates the script hash from a given script.

    Args:
        script (Union[str, bytes]): The script, either as a hexadecimal string or bytes object.

    Returns:
        bytes: The script hash as bytes.

    Example:
        >>> script_to_scripthash_bytes("010203")
        b'\x94\x9d\x22\x13\x30\x3d\x92\x2d\x7b\x26\x30\x11\x5e\x1b\x25\x1c\x33\x0b\xd7\x2a\x22\x4e\x9b\x84\x93\xd7\x5a\x62\x65\x0d\x91'
    """
    bytes_obj_from_string: bytes = safe_from_hex(s=script)
    sha_256_hash_bytes: bytes = bin_sha256(str_or_bytes=bytes_obj_from_string)
    # bin_sha256(str_or_bytes=safe_from_hex(s=script))
    return sha_256_hash_bytes


def script_to_scripthash_original(script):
    return safe_hexlify(script_to_scripthash_bytes(script=script)[::-1])


def script_to_scripthash(script: str) -> str:
    """
    Calculates the script hash of a script in hexadecimal string format.

    Args:
        script: The script to hash, typically in hexadecimal string format.

    Returns:
        str: The script hash in hexadecimal string format.

    Example:
        >>> script_to_scripthash('010203')
        '6c823896623897a731039353627c41254c88955005827c717454384684769a39f95'
    """
    sha_256_hash_bytes: bytes = script_to_scripthash_bytes(script=script)
    sha_256_hash_bytes_reversed: bytes = sha_256_hash_bytes[::-1]
    hexadecimal_string: str = safe_hexlify(a=sha_256_hash_bytes_reversed)
    # safe_hexlify(script_to_scripthash_bytes(script=script)[::-1])
    return hexadecimal_string


def generate_private_key_original() -> str:
    return binascii.hexlify(os.urandom(32)).decode()


def generate_private_key() -> str:
    """Generates a random 256-bit private key in hexadecimal format.
    Returns:
        str(64 characters long): A hexadecimal string representing the generated private key.

    Description:
        The returned private key is **not publicly accessible** and should be kept secret.
        The generated key is a 64-character hexadecimal string. Each character
        represents a single hexadecimal digit (0-9 and a-f), and the entire string
        represents 256 bits of data. This is a common format for representing
        private keys in cryptography.

    Example:
        To get the 256-bit data from the hexadecimal string, you can use the
        following formula:

        ```
        bits = int(hex_string, 16) * 4
        ```

        where `hex_string` is the hexadecimal string returned by this function.
        The formula multiplies the integer representation of the hexadecimal string
        by 4, as each hexadecimal digit represents 4 bits.



        ```python
        private_key = generate_private_key()
        print(f"Private key: {private_key}")  # Example output: Private key: 4f3c2a1b5e7d8c9a0f1e2d3c4b5a6f7e8d9c0b1a2
        bits = int(private_key, 16) * 4
        print(f"Bits: {bits}")  # Example output: Bits: 256
        ```

    """
    return binascii.hexlify(os.urandom(32)).decode()


# from cryptos.coins_async import BaseCoin, Bitcoin, BitcoinCash, Dash, Litecoin, Doge

# coins = {c.coin_symbol: c for c in (Bitcoin, Litecoin, BitcoinCash, Dash, Doge)}

# from pybitcointools.cryptos.coins_async import BaseCoin
# from pybitcointools.cryptos.py3specials import *
# from pybitcointools.cryptos.ripemd import *
