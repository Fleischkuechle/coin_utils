import os
import binascii
import hashlib
from typing import Any, AnyStr, Union, List


string_types = str
string_or_bytes_types = (str, bytes)
int_types = (int, float)
# Base switching
code_strings = {
    2: "01",
    10: "0123456789",
    16: "0123456789abcdef",  # hex
    32: "abcdefghijklmnopqrstuvwxyz234567",
    58: "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
    256: "".join([chr(x) for x in range(256)]),
}


def bin_dbl_sha256_original(s):
    bytes_to_hash = from_string_to_bytes(s)
    return hashlib.sha256(hashlib.sha256(bytes_to_hash).digest()).digest()


import re


def count_leading_ones(binary_string: str) -> int:
    """
    Counts the number of leading '1's in a binary string.

    This function is useful in cryptocurrency contexts for:

    - **Bitcoin Address Validation:**  Bitcoin addresses are derived from public keys, which are represented in binary form. Leading "1"s in the binary representation of a public key are significant for address validation.
    - **Hashing Algorithms:**  Cryptocurrency hashing algorithms often involve manipulating binary data.  Understanding the number of leading "1"s can be helpful in analyzing the output of these algorithms.

    Args:
        binary_string: The binary string to analyze.

    Returns:
        The number of leading '1's in the binary string.
    Example usage:
        binary_string:
            str = "1110101"
        leading_ones:
            int = count_leading_ones(binary_string)
        print(f"Number of leading '1's: {leading_ones}")
    """

    # 1. Match leading '1's using a regular expression
    match_result: re.Match = re.match("^1*", binary_string)

    # 2. Extract the matched substring (the leading '1's)
    leading_ones_substring: str = match_result.group(0)

    # 3. Calculate the length of the matched substring
    leading_ones_count: int = len(leading_ones_substring)

    return leading_ones_count


def bin_dbl_sha256(s: str) -> bytes:
    """
    Calculates the double SHA-256 hash of a string in binary format.

    This function first converts the input string to bytes using UTF-8 encoding.
    Then, it performs two consecutive SHA-256 hash operations on the bytes.

    Args:
        s: The string to hash.

    Returns:
        The double SHA-256 hash of the string as a bytes object.
    """
    bytes_to_hash: bytes = from_string_to_bytes(s)
    first_hash: bytes = hashlib.sha256(bytes_to_hash).digest()
    double_sha256_hash: bytes = hashlib.sha256(first_hash).digest()
    return double_sha256_hash


def lpad_original(msg, symbol, length):
    if len(msg) >= length:
        return msg
    return symbol * (length - len(msg)) + msg


def lpad(msg: str, symbol: str, length: int) -> str:
    """
    Left-pads a string with a given symbol to a specified length.

    This function takes a string, a symbol, and a length as input.
    It left-pads the string with the specified symbol until
    it reaches the desired length.
    If the string is already longer than or equal to the specified length,
    it returns the original string without any padding.

    Args:
        msg (str): The string to be padded.
        symbol (str): The symbol to use for padding.
        length (int): The desired length of the padded string.

    Returns:
        str: The left-padded string.

    Example:
        >>> lpad("hello", " ", 10)
        '     hello'
    More:
        Left padding refers to the process of adding characters
        (often spaces or other symbols) to the beginning (left side)
        of a string to ensure that it reaches a specified length.
        This is commonly used in programming to format strings consistently,
        especially when displaying numbers or aligning text.

        Key Points about Left Padding:
        Purpose:

        To ensure that strings have a uniform length for better readability or formatting.
        Commonly used in user interfaces, reports, or when preparing data for output.
        How It Works:

        If the original string is shorter than the desired length, the specified character
        (like a space or zero) is added to the left until the string reaches the required length.
        If the string is already equal to or longer than the
        desired length, it remains unchanged.
        Example:

        If you have the string "42" and you want it to be 5 characters long,
        left padding with spaces would result in " 42" (three spaces before the number).
        Historical Context:
        The term "left pad" gained notable attention in the programming community
        due to an incident involving a small JavaScript package called left-pad.
        In March 2016, the package was removed from the npm registry,
        causing widespread issues in many projects that depended on it.
        This incident highlighted the importance of even the smallest pieces
        of code in software development.

        In summary, left padding is a simple
        yet effective technique used in programming to
        format strings, ensuring they meet specific length
        requirements for better presentation and usability.

    """
    if len(msg) >= length:
        return msg
    return symbol * (length - len(msg)) + msg


def get_code_string_original(base):
    if base in code_strings:
        return code_strings[base]
    else:
        raise ValueError("Invalid base!")


def get_code_string_old(base: int) -> str:
    """
    Retrieves the code string associated with a given base.

    This function looks up the code string corresponding to the provided
        base in a dictionary called `code_strings(dict[int, str])`:
            If the base is found, it returns the associated code string.
            Otherwise, it raises a `ValueError` indicating an invalid base.
    This is how code_strings looks like:
        code_strings = {
        2: "01",
        10: "0123456789",
        16: "0123456789abcdef",  # hex
        32: "abcdefghijklmnopqrstuvwxyz234567",
        58: "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
        256: "".join([chr(x) for x in range(256)]),
        }
    Args:
        base (str): The base for which to retrieve the code string.

    Returns:
        str: The code string associated with the provided base.

    Raises:
        ValueError: If the provided base is not found in the `code_strings` dictionary.

    Example:
        >>> get_code_string('btc')
        'BTC'
        >>> get_code_string('eth')
        'ETH'
        >>> get_code_string('invalid')
        Traceback (most recent call last):
          ...
        ValueError: Invalid base!
    """
    if base in code_strings:
        return code_strings[base]
    else:
        raise ValueError("Invalid base!")


def get_code_string(base: int) -> str:
    """
    Retrieves the code string associated with a given base.

    This function looks up the code string corresponding to the provided base
    in a dictionary called `code_strings`. If the base is found, it returns
    the associated code string. Otherwise, it raises a `ValueError` indicating
    an invalid base.

    Args:
        base (int): The base for which to retrieve the code string.

    Returns:
        str: The code string associated with the provided base.

    Raises:
        ValueError: If the provided base is not found in the `code_strings` dictionary.

    Example:
        >>> get_code_string(2)
        '01'
        >>> get_code_string(16)
        '0123456789abcdef'
        >>> get_code_string(58)
        '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        >>> get_code_string(100)
        Traceback (most recent call last):
          ...
        ValueError: Invalid base!
    """
    # code_strings = {
    #     2: "01",
    #     10: "0123456789",
    #     16: "0123456789abcdef",  # hex
    #     32: "abcdefghijklmnopqrstuvwxyz234567",
    #     58: "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
    #     256: "".join([chr(x) for x in range(256)]),
    # }
    if base in code_strings:
        return code_strings[base]
    else:
        raise ValueError("Invalid base!")


def changebase_original(string, frm, to, minlen=0):
    if frm == to:
        return lpad(
            msg=string,
            symbol=get_code_string(base=frm)[0],
            length=minlen,
        )
    return encode(
        val=decode(string=string, base=frm),
        base=to,
        minlen=minlen,
    )


def changebase(
    string: str,
    frm: int,
    to: int,
    minlen: int = 0,
) -> str:
    """
    Converts a string representation of a number from one base to another.

    Args:
        string (str): The string representation of the number to convert.
        frm (int): The base of the input number.
        to (int): The base to convert the number to.
        minlen (int, optional): The minimum length of the output string. Defaults to 0.

    Returns:
        str: The string representation of the number in the new base.

    Examples:
        >>> changebase("101", 2, 10)
        '5'
        >>> changebase("123", 10, 16)
        '7B'
        >>> changebase("FF", 16, 2, minlen=8)
        '01111111'
    """
    if frm == to:
        return lpad(
            msg=string,
            symbol=get_code_string(base=frm)[0],
            length=minlen,
        )
    return encode(
        val=decode(string=string, base=frm),
        base=to,
        minlen=minlen,
    )


def bin_to_b58check_original(inp: bytes, magicbyte: int = 0) -> str:
    if magicbyte == 0:
        inp = from_int_to_byte(0) + inp
    while magicbyte > 0:
        inp = from_int_to_byte(magicbyte % 256) + inp
        magicbyte //= 256

    leadingzbytes = 0
    for x in inp:
        if x != 0:
            break
        leadingzbytes += 1

    checksum = bin_dbl_sha256(inp)[:4]
    return "1" * leadingzbytes + changebase(string=inp + checksum, frm=256, to=58)


def bin_to_b58check(inp: bytes, magicbyte: int = 0) -> str:
    """
    Encodes binary data to Base58Check format.

    This function takes binary data and encodes it using the Base58Check encoding scheme.
    It includes a checksum and a magic byte to ensure data integrity and identify the data type.

    Args:
        inp(bytes): The binary data to encode.
        magicbyte(int): An optional magic byte to prepend to the data.

    Returns:
        The Base58Check encoded string.

    More info:
        Base58Check is a modified encoding scheme used primarily in the cryptocurrency space,
        particularly for encoding Bitcoin addresses. It is designed to be
        more user-friendly than traditional base encodings by avoiding
        characters that can be easily confused.

        breakdown of its key features and components:


        Base58 Encoding:

            Base58 uses a specific set of 58 characters to represent data.
            This set excludes similar-looking characters such as 0 (zero),
            O (capital o), I (capital i), and l (lowercase L) to reduce
            the chance of errors when reading or typing addresses.
        Checksum:

            Base58Check includes a checksum to help verify the integrity
            of the data. This checksum is generated by taking a double
            SHA-256 hash of the data being encoded and using the first
            four bytes of that hash as the checksum. This helps ensure
            that any errors in the address can be detected.
        Magic Byte:

            The encoding process often includes a magic
            byte at the beginning of the data. This byte indicates
            the type of data being encoded (e.g., whether its a public
            key or a script hash). This helps wallets and software
            recognize the format of the address.

        How Base58Check Works:
            Input Data:
                The data to be encoded (e.g., a public key or hash) is prepared.
            Add Magic Byte:
                If applicable, a magic byte is prepended to the data.
            Checksum Calculation:
                A checksum is calculated using the double SHA-256 hash of the data.
            Concatenation:
                The original data (with the magic byte) is concatenated with the checksum.
            Base58 Encoding:
                The resulting byte array is then encoded using the Base58 algorithm.
            Example Use Case:
                Bitcoin Addresses:
                    Base58Check is most commonly used for Bitcoin addresses,
                    allowing users to easily share their addresses without the
                    risk of confusion or error.

            In summary,
            Base58Check is a crucial component of Bitcoin and other
            cryptocurrencies, providing a way to encode data that is
            both user-friendly and secure. Its design minimizes the
            risk of errors while ensuring that the encoded data can be
            easily verified.


    """
    if magicbyte == 0:
        inp = from_int_to_byte(0) + inp
    while magicbyte > 0:
        inp = from_int_to_byte(magicbyte % 256) + inp
        magicbyte //= 256

    leadingzbytes: int = 0
    for x in inp:
        if x != 0:
            break
        leadingzbytes += 1
    double_hash: bytes = bin_dbl_sha256(s=inp)
    checksum: bytes = double_hash[:4]  # taking the firs 4 values from the double hash
    encoded_data: bytes = inp + checksum

    leading_zeros: str = "1" * leadingzbytes
    base58_encoded: str = changebase(string=encoded_data, frm=256, to=58)

    base58_encoded_with_leading_zeros: str = leading_zeros + base58_encoded

    return base58_encoded_with_leading_zeros


def bytes_to_hex_string(b: Union[int, bytes, List[str], List[int]]) -> str:
    if isinstance(b, str):
        return b

    return "".join("{:02x}".format(y) for y in b)


def safe_from_hex_original(s: str) -> bytes:
    return bytes.fromhex(s)


def safe_from_hex(s: str) -> bytes:
    """
    Safely converts a hexadecimal string to bytes.

    Args:
        s (str): The hexadecimal string to convert.

    Returns:
        bytes: The converted bytes object.

    Example:
        >>> safe_from_hex("010203")
        b'\x01\x02\x03'
    """
    bytes_obj_from_string: bytes = bytes.fromhex(s)
    return bytes_obj_from_string


def from_int_representation_to_bytes(a: int) -> bytes:
    return bytes(str(a), "utf-8")


def from_int_to_byte_original(a: int) -> bytes:
    return bytes([a])


def from_int_to_byte(a: int) -> bytes:
    """
    Converts an integer to a single-byte representation.

    This function takes an integer 'a' and converts it into a single-byte representation.
    It is useful for converting integer values into bytes for use in cryptographic operations or data storage.

    Args:
        a (int): The integer to be converted to a byte.

    Returns:
        bytes: A single-byte representation of the input integer.

    Example:
        >>> from_int_to_byte(10)
        b'\n'
    """
    return bytes([a])


def from_byte_to_int_original(a: bytes) -> int:
    return a


def from_byte_to_int(a: bytes) -> int:
    """
    Converts a byte string to an integer.

    This function takes a byte string as input and returns the corresponding integer value.

    Args:
        a(bytes): The byte string to convert.

    Returns:
        The integer representation of the byte string.
    """
    return a


def from_string_to_bytes_original(a: AnyStr) -> bytes:
    return a if isinstance(a, bytes) else bytes(a, "utf-8")


def from_string_to_bytes(a: AnyStr) -> bytes:
    """
    Converts a string to bytes, handling both byte strings and Unicode strings.

    This function takes a string 'a' and converts it to bytes.
    It handles both byte strings (already in bytes format) and Unicode strings.
    If 'a' is already a byte string, it returns it directly.
    If 'a' is a Unicode string, it converts it to bytes using UTF-8 encoding.

    Args:
        a (AnyStr): The string to be converted to bytes. This can be either a byte string or a Unicode string.

    Returns:
        bytes: The byte representation of the input string.

    Example:
        >>> from_string_to_bytes(b'hello')
        b'hello'
        >>> from_string_to_bytes('world')
        b'world'
    """
    return a if isinstance(a, bytes) else bytes(a, "utf-8")


def safe_hexlify_original(a: bytes) -> str:
    return str(binascii.hexlify(a), "utf-8")


def safe_hexlify(a: bytes) -> str:
    """
    Converts a bytes object to a hexadecimal string,
    ensuring compatibility with different Python versions.

    Args:
        a (bytes): The bytes object to convert.

    Returns:
        str: The hexadecimal string representation of the bytes object.

    Example:
        >>> safe_hexlify(b'\x01\x02\x03')
        '010203'
    """
    hexadecimal_string: str = str(binascii.hexlify(a), "utf-8")
    return hexadecimal_string


def encode_original(val, base, minlen=0):
    base, minlen = int(base), int(minlen)
    code_string = get_code_string(base)
    result_bytes = bytes()
    while val > 0:
        curcode = code_string[val % base]
        result_bytes = bytes([ord(curcode)]) + result_bytes
        val //= base

    pad_size = minlen - len(result_bytes)

    padding_element = b"\x00" if base == 256 else b"1" if base == 58 else b"0"
    if pad_size > 0:
        result_bytes = padding_element * pad_size + result_bytes

    result_string = "".join([chr(y) for y in result_bytes])
    result = result_bytes if base == 256 else result_string

    return result


def encode(
    val: int,
    base: int,
    minlen: int = 0,
) -> Union[str, bytes]:
    """
    Encodes an integer value into a string or bytes representation based on the specified base.

    This function converts an integer 'val' into a string or bytes representation based on the provided base.
    It supports various bases, including 256 (for bytes), 58 (for Base58 encoding), and 16 (for hexadecimal).
    The 'minlen' parameter allows specifying a minimum length for the encoded output.

    Args:
        val (int): The integer value to be encoded.
        base (int): The base for encoding (e.g., 256 for bytes, 58 for Base58, 16 for hexadecimal).
        minlen (int, optional): The minimum length of the encoded output. Defaults to 0.

    Returns:
        Union[str, bytes]: The encoded value as a string (for bases other than 256) or bytes (for base 256).

    Example:
        >>> encode(12345, 16)
        '3039'
        >>> encode(12345, 58)
        '26'
        >>> encode(12345, 256, 4)
        b'\\x00\\x00\\x04\\xd9'
    """
    base, minlen = int(base), int(minlen)
    code_string = get_code_string(base=base)
    result_bytes = bytes()
    while val > 0:
        curcode = code_string[val % base]
        result_bytes = bytes([ord(curcode)]) + result_bytes
        val //= base

    pad_size = minlen - len(result_bytes)

    padding_element = b"\x00" if base == 256 else b"1" if base == 58 else b"0"
    if pad_size > 0:
        result_bytes = padding_element * pad_size + result_bytes

    result_string = "".join([chr(y) for y in result_bytes])
    result = result_bytes if base == 256 else result_string

    return result


def decode_original(string: str, base):
    if base == 256 and isinstance(string, str):
        string = bytes(bytearray.fromhex(string))
    base = int(base)
    code_string = get_code_string(base)
    result = 0
    if base == 256:

        def extract(d, cs):
            return d

    else:

        def extract(d, cs):
            return cs.find(d if isinstance(d, str) else chr(d))

    if base == 16:
        string = string.lower()
    while len(string) > 0:
        result *= base
        result += extract(string[0], code_string)
        string = string[1:]
    return result


def decode(string: str, base: int):
    """
    Decodes a string representation of a number in a given base into an integer.

    Args:
        string (str): The string representation of the number to decode.
        base (int): The base of the number.  Common bases include:
            - 2: Binary
            - 10: Decimal
            - 16: Hexadecimal
            - 256: Each character is treated as a byte (8 bits)

    Returns:
        int: The integer representation of the decoded number.

    Raises:
        ValueError: If the base is invalid or the string contains invalid characters for the given base.

    Examples:
        >>> decode("101", 2)  # Binary
        5
        >>> decode("123", 10) # Decimal
        123
        >>> decode("FF", 16)  # Hexadecimal
        255

    more:
        In the context of the decode function, base represents the numerical
        system used to represent the input string.

        Here's a breakdown:

        Base 2 (Binary): Uses only the digits 0 and 1. Each position in the string represents a power of 2.
        Base 10 (Decimal): The standard number system we use daily, with digits 0-9. Each position represents a power of 10.
        Base 16 (Hexadecimal): Uses digits 0-9 and letters A-F (representing 10-15). Each position represents a power of 16.
        Base 256: Each character in the string is treated as a byte (8 bits), representing a number between 0 and 255.
        How the base is used:

        The decode function uses the base value to determine how to interpret each character in the input string. For example:

        If base is 2 (binary), the function will interpret each character as a 0 or 1 and calculate the decimal equivalent.
        If base is 16 (hexadecimal), the function will interpret each character as a hexadecimal digit (0-9 or A-F) and calculate the decimal equivalent.
        If base is 256, the function treats each character as a byte, which is already in decimal form.
        In summary: The base argument tells the decode function which numerical system the input string is written in, allowing it to correctly convert the string into its equivalent decimal integer value.
    Think of it like this:

        The string is just a sequence of characters. It doesn't inherently tell us what those characters represent.
        The base tells us how to interpret those characters. It defines the numerical system being used.
        Let's take an example:

        String: "101"
        Base 2 (Binary): This represents the number 5 in decimal.
        Base 10 (Decimal): This represents the number 101 in decimal.
        Base 16 (Hexadecimal): This represents the number 257 in decimal.
        As you can see, the same string ("101") can have very different meanings depending on the base. The decode function uses the base to correctly convert the string into its corresponding decimal value.

        Without the base, the function would be unable to determine the correct interpretation of the input string.

    """
    if base == 256 and isinstance(string, str):
        string = bytes(bytearray.fromhex(string))
    base = int(base)
    code_string = get_code_string(base)
    result = 0
    if base == 256:

        def extract_origial(d, cs):
            return d

        def extract(d, cs):
            """
            This function simply returns the input value `d` without any modification.

            Args:
                d: Any value.
                cs: Any value. This argument is not used in the function.

            Returns:
                Any: The value of `d` is returned.

            Example:
                >>> extract(5, "hello")
                5
                >>> extract("world", 10)
                "world"
            """
            return d

    else:

        def extract_original(d, cs: str):
            return cs.find(d if isinstance(d, str) else chr(d))

        def extract(d, cs: str) -> int:
            """
            Finds the index of a character or string within a given character string.

            This function takes a character or string (`d`) and a character string (`cs`) as input. It returns the index of the first occurrence of `d` within `cs`. If `d` is a character, it is converted to its ASCII code before searching.

            Args:
                d (str or int): The character or string to find. If an integer is provided, it is interpreted as an ASCII code.
                cs (str): The character string to search within.

            Returns:
                int: The index of the first occurrence of `d` within `cs`, or -1 if `d` is not found.

            Example:
                >>> extract('a', 'abcde')
                0
                >>> extract(97, 'abcde')
                0
                >>> extract('z', 'abcde')
                -1
            """
            return cs.find(d if isinstance(d, str) else chr(d))

    if base == 16:
        string = string.lower()
    while len(string) > 0:
        result *= base
        result += extract(string[0], code_string)
        string = string[1:]
    return result


def random_string(x):
    return str(os.urandom(x))
