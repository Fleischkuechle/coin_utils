#!/usr/bin/python
import copy
import sys

# # sys.path.append(__file__)
# try:

#     from .main import *
#     from .opcodes import opcodes
#     from . import segwit_addr
#     from . import cashaddr
#     from .utils import is_hex
#     from .types import Tx, Witness
# except:
#     from pybitcointools.cryptos.main import *
#     from pybitcointools.cryptos.opcodes import opcodes
#     from pybitcointools.cryptos import segwit_addr
#     from pybitcointools.cryptos import cashaddr
#     from pybitcointools.cryptos.utils import is_hex
#     from pybitcointools.cryptos.types import Tx, Witness

from .main import *
from .opcodes import opcodes
from . import segwit_addr
from . import cashaddr
from .utils import is_hex
from .types import Tx, Witness
import binascii
from copy import deepcopy

from functools import reduce


from typing import AnyStr, Union, List


### Hex to bin converter and vice versa for objects


def json_is_base_original(obj, base):
    if isinstance(obj, bytes):
        return False
    from . import py3specials

    alpha = get_code_string(base)
    if isinstance(obj, string_types):
        for i in range(len(obj)):
            if alpha.find(obj[i]) == -1:
                return False
        return True
    elif isinstance(obj, int_types) or obj is None:
        return True
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if not json_is_base(obj[i], base):
                return False
        return True
    else:
        for x in obj:
            if not json_is_base(obj[x], base):
                return False
        return True


def json_is_base(obj, base):
    if isinstance(obj, bytes):
        return False
    from . import py3specials

    alpha = py3specials.get_code_string(base)
    if isinstance(obj, py3specials.string_types):
        for i in range(len(obj)):
            if alpha.find(obj[i]) == -1:
                return False
        return True
    elif isinstance(obj, py3specials.int_types) or obj is None:
        return True
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if not json_is_base(obj[i], base):
                return False
        return True
    else:
        for x in obj:
            if not json_is_base(obj[x], base):
                return False
        return True


def json_changebase_original(obj, changer):
    if isinstance(obj, string_or_bytes_types):
        return changer(obj)
    elif isinstance(obj, int_types) or obj is None:
        return obj
    elif isinstance(obj, list):
        return [json_changebase(x, changer) for x in obj]
    return dict((x, json_changebase(obj[x], changer)) for x in obj)


def json_changebase(obj, changer):
    from . import py3specials

    if isinstance(obj, py3specials.string_or_bytes_types):
        return changer(obj)
    elif isinstance(obj, py3specials.int_types) or obj is None:
        return obj
    elif isinstance(obj, list):
        return [json_changebase(x, changer) for x in obj]
    return dict((x, json_changebase(obj[x], changer)) for x in obj)


# Hashing transactions for signing

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
# this works like SIGHASH_ANYONECANPAY | SIGHASH_ALL, might as well make it explicit while
# we fix the constant
SIGHASH_ANYONECANPAY = 0x81
SIGHASH_FORKID = 0x40


def encode_1_byte_original(val):
    return encode(val, 256, 1)[::-1]


def encode_1_byte(val: int) -> bytes:
    """
    Encodes an integer value into a single byte.

    This function takes an integer value and encodes it into a single byte using the `py3specials` module.
    The byte is returned in reverse order.

    Args:
        val (int): The integer value to encode.

    Returns:
        bytes: The encoded byte.
    """
    from . import py3specials

    return py3specials.encode(val, 256, 1)[::-1]


def encode_4_bytes_original(val):

    return encode(val, 256, 4)[::-1]


def encode_4_bytes(val: int) -> bytes:
    """
    Encodes an integer value into four bytes.

    This function takes an integer value and encodes it into four bytes using the `py3specials` module.
    The bytes are returned in reverse order.

    Args:
        val (int): The integer value to encode.

    Returns:
        bytes: The encoded four bytes.
    """
    from . import py3specials

    return py3specials.encode(val, 256, 4)[::-1]


def encode_8_bytes_original(val):
    return encode(val, 256, 8)[::-1]


def encode_8_bytes(val: int) -> bytes:
    """
    Encodes an integer value into eight bytes.

    This function takes an integer value and encodes it into eight bytes using the `py3specials` module.
    The bytes are returned in reverse order.

    Args:
        val (int): The integer value to encode.

    Returns:
        bytes: The encoded eight bytes.
    """
    from . import py3specials

    return py3specials.encode(val, 256, 8)[::-1]


def list_to_bytes_original(vals: list[bytes]) -> bytes:
    try:
        return reduce(lambda x, y: x + y, vals, bytes())
    except Exception as e:
        print(e)
        pass


def list_to_bytes(vals: list[bytes]) -> bytes:
    """
    Concatenates a list of byte arrays into a single byte array.

    Args:
        vals: A list of byte arrays.

    Returns:
        A single byte array containing the concatenated bytes from the input list.

    Raises:
        Exception: If an error occurs during concatenation.
    """
    try:
        return reduce(lambda x, y: x + y, vals, bytes())
    except Exception as e:
        print(e)
        pass


def dbl_sha256_list_original(vals):
    return bin_dbl_sha256(list_to_bytes(vals))


def dbl_sha256_list(vals: list[bytes]) -> bytes:
    """
    Calculates the double SHA-256 hash of a list of bytes.

    This function takes a list of byte strings, concatenates them,
    and then applies the double SHA-256 hash algorithm to the resulting byte string.

    Args:
        vals (list): A list of byte strings.

    Returns:
        bytes: The double SHA-256 hash of the concatenated byte strings.

    Example:
        >>> vals = [b'hello', b'world']
        >>> dbl_sha256_list(vals)
        b'...'  # Returns the double SHA-256 hash
    """
    from . import main

    double_hash: bytes = main.bin_dbl_sha256(list_to_bytes(vals=vals))
    return double_hash


# Transaction serialization and deserialization


def is_segwit(tx: bytes) -> bool:
    """
    Checks that the marker in a transaction is set to 0. For legacy transactions this would indicate the number of
    inputs so will be at least 1.
    """
    return tx[4] == 0


def deserialize_original(tx: AnyStr) -> Tx:
    if isinstance(tx, str) and is_hex(tx):
        # tx = bytes(bytearray.fromhex(tx))
        return json_changebase(
            deserialize(binascii.unhexlify(tx)), lambda x: safe_hexlify(x)
        )
    # http://stackoverflow.com/questions/4851463/python-closure-write-to-variable-in-parent-scope
    # Python's scoping rules are demented, requiring me to make pos an object
    # so that it is call-by-reference
    pos = [0]

    def read_as_int(bytez: int):
        pos[0] += bytez
        return decode(tx[pos[0] - bytez : pos[0]][::-1], 256)

    def read_var_int() -> int:
        pos[0] += 1
        val = -1
        try:
            val = from_byte_to_int(tx[pos[0] - 1])

            if val < 253:
                return val
        except:
            print("exception at read_var_int")
        return read_as_int(pow(2, val - 252))

    def read_bytes(bytez: int) -> str:
        pos[0] += bytez
        return tx[pos[0] - bytez : pos[0]]

    def read_var_string() -> str:
        size = read_var_int()
        return read_bytes(size)

    def read_witness_script_code() -> str:
        size = read_var_int()
        return num_to_var_int(size) + read_bytes(size)

    obj: Tx = {"ins": [], "outs": [], "version": read_as_int(4)}
    has_witness = is_segwit(tx)
    if has_witness:
        obj["marker"] = read_as_int(1)
        obj["flag"] = read_as_int(1)
    ins = read_var_int()
    for _ in range(ins):
        obj["ins"].append(
            {
                "tx_hash": read_bytes(32)[::-1],
                "tx_pos": read_as_int(4),
                "script": read_var_string(),
                "sequence": read_as_int(4),
            }
        )
    outs = read_var_int()
    for _ in range(outs):
        obj["outs"].append({"value": read_as_int(8), "script": read_var_string()})
    if has_witness:
        obj["witness"] = []
        for _ in range(ins):
            number = read_var_int()
            script_code = [read_witness_script_code() for _ in range(number)]
            obj["witness"].append(
                {"number": number, "scriptCode": list_to_bytes(script_code)}
            )
    obj["locktime"] = read_as_int(4)
    return obj


def deserialize(tx: AnyStr) -> Tx:
    from . import py3specials

    if isinstance(tx, str) and is_hex(tx):
        # tx = bytes(bytearray.fromhex(tx))
        return json_changebase(
            deserialize(binascii.unhexlify(tx)), lambda x: py3specials.safe_hexlify(a=x)
        )
    # http://stackoverflow.com/questions/4851463/python-closure-write-to-variable-in-parent-scope
    # Python's scoping rules are demented, requiring me to make pos an object
    # so that it is call-by-reference
    pos = [0]

    def read_as_int(bytez: int) -> int:
        """
        Reads a sequence of bytes from the transaction data (`tx`) and decodes it as an integer.

        This function advances the current position (`pos[0]`) within the transaction data by `bytez` bytes.
        It then extracts the specified number of bytes from the transaction data, reverses the byte order,
        and decodes the resulting byte string as an integer using base 256.

        Args:
            bytez (int): The number of bytes to read from the transaction data.

        Returns:
            int: The decoded integer value.
        """
        pos[0] += bytez
        byte_sequence: str = tx[pos[0] - bytez : pos[0]][::-1]
        decoded_number: int = py3specials.decode(string=byte_sequence, base=256)
        return decoded_number

    def read_var_int() -> int:
        """
        Reads a variable-length integer from the transaction data (`tx`).

        This function reads a single byte from the transaction data to determine the length of the following integer.
        Based on the first byte, it either returns the value directly if it's less than 253,
        or it reads the specified number of bytes and decodes them as an integer.

        Returns:
            int: The decoded variable-length integer.
        """
        pos[0] += 1
        val = -1
        try:
            val = py3specials.from_byte_to_int(tx[pos[0] - 1])

            if val < 253:
                return val
        except:
            print("exception at read_var_int")
        decoded_number: int = read_as_int(bytez=pow(2, val - 252))
        return decoded_number

    def read_bytes(bytez: int) -> str:
        """
        Reads a specified number of bytes from the transaction data (`tx`) and returns them as a string.

        This function advances the current position (`pos[0]`) within the transaction data by `bytez` bytes.
        It then extracts the specified number of bytes from the transaction data and returns them as a string.

        Args:
            bytez (int): The number of bytes to read from the transaction data.

        Returns:
            str: The extracted bytes as a string.
        """
        pos[0] += bytez
        extracted_bytes: str = tx[
            pos[0] - bytez : pos[0]
        ]  # Store the extracted bytes in a variable
        return extracted_bytes  # Return the variable

    def read_var_string() -> str:
        """
        Reads a variable-length string from the transaction data (`tx`).

        This function first reads the length of the string using `read_var_int()`.
        Then, it reads the specified number of bytes from the transaction data using `read_bytes()`.
        Finally, it returns the extracted bytes as a string.

        Returns:
            str: The extracted variable-length string.
        """
        size: int = read_var_int()
        extracted_bytes: str = read_bytes(bytez=size)
        return extracted_bytes

    def read_witness_script_code() -> str:
        from . import main

        size: int = read_var_int()
        return main.num_to_var_int(x=size) + read_bytes(size)

    obj: Tx = {"ins": [], "outs": [], "version": read_as_int(4)}
    has_witness = is_segwit(tx)
    if has_witness:
        obj["marker"] = read_as_int(1)
        obj["flag"] = read_as_int(1)
    ins = read_var_int()
    for _ in range(ins):
        obj["ins"].append(
            {
                "tx_hash": read_bytes(32)[::-1],
                "tx_pos": read_as_int(4),
                "script": read_var_string(),
                "sequence": read_as_int(4),
            }
        )
    outs = read_var_int()
    for _ in range(outs):
        obj["outs"].append({"value": read_as_int(8), "script": read_var_string()})
    if has_witness:
        obj["witness"] = []
        for _ in range(ins):
            number = read_var_int()
            script_code = [read_witness_script_code() for _ in range(number)]
            obj["witness"].append(
                {"number": number, "scriptCode": list_to_bytes(script_code)}
            )
    obj["locktime"] = read_as_int(4)
    return obj


def test_unhexlify(x):
    try:
        return binascii.unhexlify(x)
    except binascii.Error:
        raise Exception("Unhexlify failed for", x)


def serialize_original(txobj: Tx, include_witness: bool = True) -> AnyStr:
    txobj = deepcopy(txobj)
    for i in txobj["ins"]:
        if "address" in i:
            del i["address"]
    if isinstance(txobj, bytes):
        txobj = bytes_to_hex_string(txobj)
    o = []
    if json_is_base(txobj, 16):
        json_changedbase = json_changebase(txobj, test_unhexlify)
        hexlified = safe_hexlify(
            serialize(json_changedbase, include_witness=include_witness)
        )
        return hexlified
    o.append(encode_4_bytes(txobj["version"]))
    if include_witness and all(k in txobj.keys() for k in ["marker", "flag"]):
        o.append(encode_1_byte(txobj["marker"]))
        o.append(encode_1_byte(txobj["flag"]))
    o.append(num_to_var_int(len(txobj["ins"])))
    for inp in txobj["ins"]:
        o.append(inp["tx_hash"][::-1])
        o.append(encode_4_bytes(inp["tx_pos"]))
        o.append(
            num_to_var_int(len(inp["script"]))
            + (inp["script"] if inp["script"] else bytes())
        )
        o.append(encode_4_bytes(inp["sequence"]))
    o.append(num_to_var_int(len(txobj["outs"])))
    for out in txobj["outs"]:
        o.append(encode_8_bytes(out["value"]))
        o.append(num_to_var_int(len(out["script"])) + out["script"])
    if include_witness and "witness" in txobj.keys():
        for witness in txobj["witness"]:
            o.append(
                num_to_var_int(witness["number"])
                + (witness["scriptCode"] if witness["scriptCode"] else bytes())
            )
    o.append(encode_4_bytes(txobj["locktime"]))
    return list_to_bytes(o)


# def serialize(txobj: Tx, include_witness: bool = True) -> AnyStr:
#     txobj = deepcopy(txobj)
#     for i in txobj["ins"]:
#         if "address" in i:
#             del i["address"]
#     from . import py3specials

#     if isinstance(txobj, bytes):
#         txobj = py3specials.bytes_to_hex_string(b=txobj)
#     o = []
#     if json_is_base(txobj, 16):
#         json_changedbase = json_changebase(txobj, test_unhexlify)
#         hexlified = py3specials.safe_hexlify(
#             serialize(json_changedbase, include_witness=include_witness)
#         )
#         return hexlified
#     o.append(encode_4_bytes(txobj["version"]))
#     if include_witness and all(k in txobj.keys() for k in ["marker", "flag"]):
#         o.append(encode_1_byte(txobj["marker"]))
#         o.append(encode_1_byte(txobj["flag"]))
#     from . import main

#     o.append(main.num_to_var_int(len(txobj["ins"])))
#     for inp in txobj["ins"]:
#         o.append(inp["tx_hash"][::-1])
#         o.append(encode_4_bytes(inp["tx_pos"]))
#         o.append(
#             main.num_to_var_int(len(inp["script"]))
#             + (inp["script"] if inp["script"] else bytes())
#         )
#         o.append(encode_4_bytes(inp["sequence"]))
#     o.append(main.num_to_var_int(len(txobj["outs"])))
#     for out in txobj["outs"]:
#         o.append(encode_8_bytes(out["value"]))
#         o.append(main.num_to_var_int(len(out["script"])) + out["script"])
#     if include_witness and "witness" in txobj.keys():
#         for witness in txobj["witness"]:
#             o.append(
#                 main.num_to_var_int(witness["number"])
#                 + (witness["scriptCode"] if witness["scriptCode"] else bytes())
#             )
#     o.append(encode_4_bytes(txobj["locktime"]))
#     single_byte_array: bytes = list_to_bytes(vals=o)

#     return single_byte_array


def serialize(
    txobj: Tx,
    include_witness: bool = True,
) -> bytes:
    """
    Serializes a transaction object into a byte array.

    Args:
        txobj: The transaction object to serialize.
        include_witness: Whether to include witness data in the serialization. Defaults to True.

    Returns:
        A byte array(bytes) representing the serialized transaction.

    Raises:
        None.

    Notes:
        This function assumes the transaction object is in a specific format.
        It uses various helper functions (e.g., `encode_4_bytes`, `num_to_var_int`, `list_to_bytes`)
        which are not defined here but are assumed to exist in the context of the code.
    """
    txobj = deepcopy(txobj)
    for i in txobj["ins"]:
        if "address" in i:
            del i["address"]
    from . import py3specials

    if isinstance(txobj, bytes):
        txobj = py3specials.bytes_to_hex_string(b=txobj)
    o: list[bytes] = []
    if json_is_base(txobj, 16):
        json_changedbase = json_changebase(txobj, test_unhexlify)
        hexlified = py3specials.safe_hexlify(
            serialize(json_changedbase, include_witness=include_witness)
        )
        return hexlified
    o.append(encode_4_bytes(txobj["version"]))
    if include_witness and all(k in txobj.keys() for k in ["marker", "flag"]):
        o.append(encode_1_byte(txobj["marker"]))
        o.append(encode_1_byte(txobj["flag"]))
    from . import main

    o.append(main.num_to_var_int(len(txobj["ins"])))
    for inp in txobj["ins"]:
        o.append(inp["tx_hash"][::-1])
        o.append(encode_4_bytes(inp["tx_pos"]))
        o.append(
            main.num_to_var_int(len(inp["script"]))
            + (inp["script"] if inp["script"] else bytes())
        )
        o.append(encode_4_bytes(inp["sequence"]))
    o.append(main.num_to_var_int(len(txobj["outs"])))
    for out in txobj["outs"]:
        o.append(encode_8_bytes(out["value"]))
        o.append(main.num_to_var_int(len(out["script"])) + out["script"])
    if include_witness and "witness" in txobj.keys():
        for witness in txobj["witness"]:
            o.append(
                main.num_to_var_int(witness["number"])
                + (witness["scriptCode"] if witness["scriptCode"] else bytes())
            )
    o.append(encode_4_bytes(txobj["locktime"]))
    single_byte_array: bytes = list_to_bytes(vals=o)

    return single_byte_array


def uahf_digest_original(txobj: Tx, i: int) -> bytes:
    for inp in txobj["ins"]:
        inp.pop("address", None)
    if isinstance(txobj, bytes):
        txobj = bytes_to_hex_string(txobj)
    o = []

    if json_is_base(txobj, 16):
        txobj = json_changebase(txobj, lambda x: binascii.unhexlify(x))
    o.append(encode(txobj["version"], 256, 4)[::-1])

    serialized_ins = []
    for inp in txobj["ins"]:
        serialized_ins.append(inp["tx_hash"][::-1])
        serialized_ins.append(encode_4_bytes(inp["tx_pos"]))
    inputs_hashed = dbl_sha256_list(serialized_ins)
    o.append(inputs_hashed)

    sequences = dbl_sha256_list(
        [encode_4_bytes(inp["sequence"]) for inp in txobj["ins"]]
    )
    o.append(sequences)

    inp = txobj["ins"][i]
    o.append(inp["tx_hash"][::-1])
    o.append(encode_4_bytes(inp["tx_pos"]))
    o.append(
        num_to_var_int(len(inp["script"]))
        + (inp["script"] if inp["script"] else bytes())
    )
    o.append(encode_8_bytes(inp["value"]))
    o.append(encode_4_bytes(inp["sequence"]))

    serialized_outs = []
    for out in txobj["outs"]:
        serialized_outs.append(encode_8_bytes(out["value"]))
        serialized_outs.append(num_to_var_int(len(out["script"])) + out["script"])
    outputs_hashed = dbl_sha256_list(serialized_outs)
    o.append(outputs_hashed)

    o.append(encode_4_bytes(txobj["locktime"]))
    # o.append(b'\x01\x00\x00\x00')
    return list_to_bytes(o)


def uahf_digest(txobj: Tx, i: int) -> bytes:
    """
    Calculates the UAHF (User Activated Hard Fork) digest for a transaction.

    This function computes the UAHF digest for a given transaction and input index.
    The UAHF digest is used in SegWit transactions to ensure that the signature hash
    is calculated correctly, taking into account the SegWit flag.

    Args:
        txobj (Tx): The transaction object, a dictionary representing the transaction.
        i (int): The index of the input for which the digest is being calculated.

    Returns:
        bytes: The UAHF digest for the specified transaction and input.

    Example:
        >>> txobj = {'version': 2, 'ins': [...], 'outs': [...], 'locktime': 0}  # Sample transaction
        >>> i = 0  # Input index
        >>> uahf_digest(txobj, i)
        b'...'  # Returns the UAHF digest
    """
    from . import py3specials
    from . import main

    for inp in txobj["ins"]:
        inp.pop("address", None)
    if isinstance(txobj, bytes):
        txobj = bytes_to_hex_string(txobj)
    o = []

    if json_is_base(txobj, 16):
        txobj = json_changebase(txobj, lambda x: binascii.unhexlify(x))
    o.append(py3specials.encode(txobj["version"], 256, 4)[::-1])

    serialized_ins = []
    for inp in txobj["ins"]:
        serialized_ins.append(inp["tx_hash"][::-1])
        serialized_ins.append(encode_4_bytes(inp["tx_pos"]))
    inputs_hashed: bytes = dbl_sha256_list(serialized_ins)
    o.append(inputs_hashed)

    sequences = dbl_sha256_list(
        [encode_4_bytes(inp["sequence"]) for inp in txobj["ins"]]
    )
    o.append(sequences)

    inp = txobj["ins"][i]
    o.append(inp["tx_hash"][::-1])
    o.append(encode_4_bytes(inp["tx_pos"]))
    o.append(
        main.num_to_var_int(len(inp["script"]))
        + (inp["script"] if inp["script"] else bytes())
    )
    o.append(encode_8_bytes(inp["value"]))
    o.append(encode_4_bytes(inp["sequence"]))

    serialized_outs = []
    for out in txobj["outs"]:
        serialized_outs.append(encode_8_bytes(out["value"]))
        serialized_outs.append(main.num_to_var_int(len(out["script"])) + out["script"])
    outputs_hashed = dbl_sha256_list(serialized_outs)
    o.append(outputs_hashed)

    o.append(encode_4_bytes(txobj["locktime"]))
    # o.append(b'\x01\x00\x00\x00')
    return list_to_bytes(vals=o)


def uahf_digest(txobj: Tx, i: int) -> bytes:
    """
    Calculates the UAHF (User Activated Hard Fork) digest for a transaction.

    This function computes the UAHF digest for a given transaction and input index.
    The UAHF digest is used in SegWit transactions to ensure that the signature hash
    is calculated correctly, taking into account the SegWit flag.

    Args:
        txobj (Tx): The transaction object, a dictionary representing the transaction.
        i (int): The index of the input for which the digest is being calculated.

    Returns:
        bytes: The UAHF digest for the specified transaction and input.

    Example:
        >>> txobj = {'version': 2, 'ins': [...], 'outs': [...], 'locktime': 0}  # Sample transaction
        >>> i = 0  # Input index
        >>> uahf_digest(txobj, i)
        b'...'  # Returns the UAHF digest
    """
    from . import py3specials
    from . import main

    for inp in txobj["ins"]:
        inp.pop("address", None)
    if isinstance(txobj, bytes):
        txobj: str = bytes_to_hex_string(txobj)
    o: list = []

    if json_is_base(txobj, 16):
        txobj: bytes = json_changebase(txobj, lambda x: binascii.unhexlify(x))
    o.append(py3specials.encode(txobj["version"], 256, 4)[::-1])

    serialized_ins: list = []
    for inp in txobj["ins"]:
        serialized_ins.append(inp["tx_hash"][::-1])
        serialized_ins.append(encode_4_bytes(inp["tx_pos"]))
    inputs_hashed: bytes = dbl_sha256_list(serialized_ins)
    o.append(inputs_hashed)

    sequences: bytes = dbl_sha256_list(
        [encode_4_bytes(inp["sequence"]) for inp in txobj["ins"]]
    )
    o.append(sequences)

    inp: dict = txobj["ins"][i]
    o.append(inp["tx_hash"][::-1])
    o.append(encode_4_bytes(inp["tx_pos"]))
    o.append(
        main.num_to_var_int(len(inp["script"]))
        + (inp["script"] if inp["script"] else bytes())
    )
    o.append(encode_8_bytes(inp["value"]))
    o.append(encode_4_bytes(inp["sequence"]))

    serialized_outs: list = []
    for out in txobj["outs"]:
        serialized_outs.append(encode_8_bytes(out["value"]))
        serialized_outs.append(main.num_to_var_int(len(out["script"])) + out["script"])
    outputs_hashed: bytes = dbl_sha256_list(vals=serialized_outs)
    o.append(outputs_hashed)

    o.append(encode_4_bytes(txobj["locktime"]))
    # o.append(b'\x01\x00\x00\x00')
    return list_to_bytes(vals=o)


def signature_form_original(
    tx: Union[AnyStr, Tx],
    i: int,
    script,
    hashcode: int = SIGHASH_ALL,
    segwit: bool = False,
) -> bytes:
    i, hashcode = int(i), int(hashcode)
    if isinstance(tx, string_or_bytes_types):
        tx = deserialize(tx)
    newtx = deepcopy(tx)
    for j, inp in enumerate(newtx["ins"]):
        if j == i:
            newtx["ins"][j]["script"] = script
        else:
            newtx["ins"][j]["script"] = ""
    if segwit or hashcode & 255 == SIGHASH_ALL + SIGHASH_FORKID:
        return uahf_digest(newtx, i)
    elif hashcode == SIGHASH_NONE:
        newtx["outs"] = []
    elif hashcode == SIGHASH_SINGLE:
        newtx["outs"] = newtx["outs"][: len(newtx["ins"])]
        for out in newtx["outs"][: len(newtx["ins"]) - 1]:
            out["value"] = 2**64 - 1
            out["script"] = ""
    elif hashcode == SIGHASH_ANYONECANPAY:
        newtx["ins"] = [newtx["ins"][i]]

    return serialize(newtx, include_witness=False)


def signature_form(
    tx: Union[AnyStr, Tx],
    i: int,
    script: bytes,
    hashcode: int = SIGHASH_ALL,
    segwit: bool = False,
) -> bytes:
    """
    Prepares a transaction for signing by modifying it based on the specified signature hash code.

    This function takes a transaction, an input index, a script, a signature hash code,
    and a flag indicating whether SegWit is enabled, and returns a modified transaction
    that can be used to generate a signature. The modification includes setting the script
    for the specified input, clearing scripts for other inputs, and potentially adjusting
    the outputs based on the signature hash code.

    Args:
        tx (Union[AnyStr, Tx]): The transaction to be modified, either as a serialized string
            or a transaction dictionary.
        i (int): The index of the input to be signed.
        script (bytes): The script to be used for the input being signed.
        hashcode (int, optional): The signature hash code, defaulting to SIGHASH_ALL.
            Possible values:
                - SIGHASH_ALL: All inputs and outputs are included in the hash.
                - SIGHASH_NONE: Only the transaction version and the input being signed are included.
                - SIGHASH_SINGLE: Only the transaction version, the input being signed, and the corresponding output
                    are included.
                - SIGHASH_ANYONECANPAY: Only the input being signed is included.
        segwit (bool, optional): Whether SegWit is enabled, defaulting to False.

    Returns:
        bytes: The serialized transaction in bytes, modified for signing.

    Example:
        >>> tx = deserialize(b'...')  # Assuming 'tx' is a serialized transaction
        >>> i = 0  # Input index to be signed
        >>> script = b'...'  # Script for the input
        >>> signature_form(tx, i, script, hashcode=SIGHASH_ALL)
        b'...'  # Returns the modified transaction in bytes
    """
    from . import py3specials

    i, hashcode = int(i), int(hashcode)
    if isinstance(tx, py3specials.string_or_bytes_types):
        tx = deserialize(tx)
    newtx = deepcopy(tx)
    for j, inp in enumerate(newtx["ins"]):
        if j == i:
            newtx["ins"][j]["script"] = script
        else:
            newtx["ins"][j]["script"] = ""
    if segwit or hashcode & 255 == SIGHASH_ALL + SIGHASH_FORKID:
        return uahf_digest(newtx, i)
    elif hashcode == SIGHASH_NONE:
        newtx["outs"] = []
    elif hashcode == SIGHASH_SINGLE:
        newtx["outs"] = newtx["outs"][: len(newtx["ins"])]
        for out in newtx["outs"][: len(newtx["ins"]) - 1]:
            out["value"] = 2**64 - 1
            out["script"] = ""
    elif hashcode == SIGHASH_ANYONECANPAY:
        newtx["ins"] = [newtx["ins"][i]]

    return serialize(newtx, include_witness=False)


# Making the actual signatures


def der_encode_sig_original(v, r, s):
    b1, b2 = safe_hexlify(encode(r, 256)), safe_hexlify(encode(s, 256))
    if len(b1) and b1[0] in "89abcdef":
        b1 = "00" + b1
    if len(b2) and b2[0] in "89abcdef":
        b2 = "00" + b2
    left = "02" + encode(len(b1) // 2, 16, 2) + b1
    right = "02" + encode(len(b2) // 2, 16, 2) + b2
    return "30" + encode(len(left + right) // 2, 16, 2) + left + right


def der_encode_sig(v: int, r: int, s: int) -> str:
    """
    Encodes a signature in DER format.

    This function takes the signature components (v, r, s) and encodes them
    in the DER (Distinguished Encoding Rules) format, which is commonly used
    for representing cryptographic signatures.

    Args:
        v (int): The recovery ID, typically 0 or 1.
        r (int): The R component of the signature.
        s (int): The S component of the signature.

    Returns:
        str: The DER-encoded signature as a hexadecimal string.

    Example:
        >>> v = 0
        >>> r = 0x1234567890abcdef
        >>> s = 0x9876543210fedcba
        >>> der_encode_sig(v, r, s)
        '30460221001234567890abcdef0221009876543210fedcba'
    """
    from . import py3specials

    b1: str
    b2: str
    b1, b2 = py3specials.safe_hexlify(
        a=py3specials.encode(val=r, base=256)
    ), py3specials.safe_hexlify(py3specials.encode(val=s, base=256))
    if len(b1) and b1[0] in "89abcdef":
        b1 = "00" + b1
    if len(b2) and b2[0] in "89abcdef":
        b2 = "00" + b2
    left: str = "02" + py3specials.encode(val=len(b1) // 2, base=16, minlen=2) + b1
    right: str = "02" + py3specials.encode(val=len(b2) // 2, base=16, minlen=2) + b2

    der_encoded_sig: str = (
        "30"
        + py3specials.encode(val=len(left + right) // 2, base=16, minlen=2)
        + left
        + right
    )
    return der_encoded_sig


def der_decode_sig(sig):
    leftlen = decode(sig[6:8], 16) * 2
    left = sig[8 : 8 + leftlen]
    rightlen = decode(sig[10 + leftlen : 12 + leftlen], 16) * 2
    right = sig[12 + leftlen : 12 + leftlen + rightlen]
    return None, decode(left, 16), decode(right, 16)


def is_bip66(sig: str) -> bool:
    """Checks hex DER sig for BIP66 consistency"""
    # https://raw.githubusercontent.com/bitcoin/bips/master/bip-0066.mediawiki
    # 0x30  [total-len]  0x02  [R-len]  [R]  0x02  [S-len]  [S]  [sighash]
    sig = bytearray.fromhex(sig) if is_hex(sig) else bytearray(sig)
    if (sig[0] == 0x30) and (sig[1] == len(sig) - 2):  # check if sighash is missing
        sig.extend(b"\1")  # add SIGHASH_ALL for testing
    # assert (sig[-1] & 124 == 0) and (not not sig[-1]), "Bad SIGHASH value"

    if len(sig) < 9 or len(sig) > 73:
        return False
    if sig[0] != 0x30:
        return False
    if sig[1] != len(sig) - 3:
        return False
    rlen = sig[3]
    if 5 + rlen >= len(sig):
        return False
    slen = sig[5 + rlen]
    if rlen + slen + 7 != len(sig):
        return False
    if sig[2] != 0x02:
        return False
    if rlen == 0:
        return False
    if sig[4] & 0x80:
        return False
    if rlen > 1 and (sig[4] == 0x00) and not (sig[5] & 0x80):
        return False
    if sig[4 + rlen] != 0x02:
        return False
    if slen == 0:
        return False
    if sig[rlen + 6] & 0x80:
        return False
    if slen > 1 and (sig[6 + rlen] == 0x00) and not (sig[7 + rlen] & 0x80):
        return False
    return True


def txhash_original(tx: AnyStr, hashcode: int = None, wtxid: bool = True) -> str:
    if isinstance(tx, str) and re.match("^[0-9a-fA-F]*$", tx):
        tx = changebase(tx, 16, 256)
    if isinstance(tx, string_or_bytes_types):
        segwit = is_segwit(tx)
    else:
        segwit = False
    if not wtxid and segwit:
        tx = serialize(deserialize(tx), include_witness=False)
    if hashcode:
        return dbl_sha256(
            from_string_to_bytes(tx) + encode(int(hashcode), 256, 4)[::-1]
        )
    else:
        return safe_hexlify(bin_dbl_sha256(tx)[::-1])


# def txhash(
#     tx: AnyStr,
#     hashcode: int = None,
#     wtxid: bool = True,
# ) -> str:
#     from . import py3specials
#     from . import main

#     if isinstance(tx, str) and re.match("^[0-9a-fA-F]*$", tx):
#         tx = py3specials.changebase(string=tx, frm=16, to=256)
#     if isinstance(tx, py3specials.string_or_bytes_types):
#         segwit = is_segwit(tx)
#     else:
#         segwit = False
#     if not wtxid and segwit:
#         tx = serialize(deserialize(tx), include_witness=False)
#     if hashcode:
#         return main.dbl_sha256(
#             string=py3specials.from_string_to_bytes(a=tx)
#             + py3specials.encode(val=int(hashcode), base=256, minlen=4)[::-1]
#         )
#     else:
#         return py3specials.safe_hexlify(a=main.bin_dbl_sha256(tx)[::-1])


def txhash(
    tx: AnyStr,
    hashcode: int = None,
    wtxid: bool = True,
) -> str:
    """
    Calculates the transaction hash.

    This function takes a transaction object (`tx`) and calculates its hash.
    It supports different input formats, including hexadecimal strings, bytes,
    and transaction objects. It also allows specifying a custom hashcode and
    whether to include witness data in the hash calculation.

    Args:
        tx (AnyStr): The transaction object. This can be a string, bytes, or any
            object that can be converted to a hexadecimal string.
        hashcode (int, optional): The hashcode to use. Defaults to None, which
            uses the default hashcode.
        wtxid (bool, optional): Whether to include witness data in the hash
            calculation. Defaults to True.

    Returns:
        str: The transaction hash as a hexadecimal string.

    Example:
        >>> tx = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000'
        >>> txhash(tx)
        '957f434a9a7f74935d8a2d315948b24f0c869187233d425e86c5947c99589c6893'
        >>> txhash(tx, hashcode=1)
        '7c802c9660264a6451814635606a679626543d552d25252754a2467254486535'
    """
    from . import py3specials
    from . import main
    import re

    segwit: bool
    if isinstance(tx, str) and re.match("^[0-9a-fA-F]*$", tx):
        tx: bytes = py3specials.changebase(string=tx, frm=16, to=256)
    if isinstance(tx, py3specials.string_or_bytes_types):
        segwit = is_segwit(tx)
    else:
        segwit = False
    if not wtxid and segwit:
        tx = serialize(deserialize(tx), include_witness=False)
    if hashcode:
        return main.dbl_sha256(
            string=py3specials.from_string_to_bytes(a=tx)
            + py3specials.encode(val=int(hashcode), base=256, minlen=4)[::-1]
        )
    else:
        return py3specials.safe_hexlify(a=main.bin_dbl_sha256(tx)[::-1])


def public_txhash(tx: AnyStr, hashcode: int = None) -> str:
    return txhash(tx, hashcode=hashcode, wtxid=False)


def bin_txhash_original(tx: AnyStr, hashcode: int = None) -> bytes:
    return binascii.unhexlify(txhash(tx, hashcode))


def bin_txhash(tx: AnyStr, hashcode: int = None) -> bytes:
    """
    Calculates the binary transaction hash.

    This function takes a transaction object (`tx`) and an optional hashcode
    and returns the binary representation of the transaction hash.

    Args:
        tx (AnyStr): The transaction object. This can be a string, bytes, or any
            object that can be converted to a hexadecimal string.
        hashcode (int, optional): The hashcode to use. Defaults to None, which
            uses the default hashcode.

    Returns:
        bytes: The binary transaction hash.

    Example:
        >>> tx = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000'
        >>> bin_txhash(tx)
        b'\x95\x7f\x43\x4a\x9a\x7f\x74\x93\x5d\x8a\x2d\x31\x59\x48\xb2\x4f\x0c\x86\x91\x87\x23\x3d\x42\x5e\x86\xc5\x94\x7c\x99\x58\x9c\x68\x93'
    """
    return binascii.unhexlify(txhash(tx, hashcode))


def ecdsa_tx_sign_original(tx, priv, hashcode=SIGHASH_ALL):
    rawsig = ecdsa_raw_sign(bin_txhash(tx, hashcode), priv)
    return der_encode_sig(*rawsig) + encode(hashcode & 255, 16, 2)


def ecdsa_tx_sign_original(tx, priv, hashcode=SIGHASH_ALL):
    rawsig = ecdsa_raw_sign(bin_txhash(tx, hashcode), priv)
    return der_encode_sig(*rawsig) + encode(hashcode & 255, 16, 2)


def ecdsa_tx_sign(
    tx: AnyStr,
    priv: AnyStr,
    hashcode: int = SIGHASH_ALL,
) -> str:
    """
    Signs a transaction using ECDSA.

    This function takes a transaction object (`tx`), a private key (`priv`), and
    an optional hashcode (`hashcode`) and returns the ECDSA signature for the
    transaction.

    Args:
        tx: The transaction object to sign.
        priv: The private key to use for signing.
        hashcode (int, optional): The hashcode to use. Defaults to SIGHASH_ALL.

    Returns:
        str: The ECDSA signature for the transaction.

    Example:
        >>> tx = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000'
        >>> priv = '0x0000000000000000000000000000000000000000000000000000000000000001'
        >>> ecdsa_tx_sign(tx, priv)
        '3044022078a8444417754913576204532630d98523c565193215992171c50349619d9c0220542748042059458c342e392d07366479936340e516585a332d7c139c50778701'
    """
    from . import main
    from . import py3specials

    binary_transaction_hash: bytes = bin_txhash(tx=tx, hashcode=hashcode)
    raw_sig_components_v_r_s: Tuple[int, int, int] = main.ecdsa_raw_sign(
        msghash=binary_transaction_hash,
        private_key=priv,
    )
    DER_encoded_signature_as_a_hexadecimal_string: str = der_encode_sig(
        v=raw_sig_components_v_r_s[0],
        r=raw_sig_components_v_r_s[1],
        s=raw_sig_components_v_r_s[2],
    )
    hashcode_hex: str = py3specials.encode(
        val=hashcode & 255,
        base=16,
        minlen=2,
    )
    signature: str = DER_encoded_signature_as_a_hexadecimal_string + hashcode_hex
    return signature


def ecdsa_tx_verify(tx, sig, pub, hashcode=SIGHASH_ALL):
    return ecdsa_raw_verify(bin_txhash(tx, hashcode), der_decode_sig(sig), pub)


def ecdsa_tx_recover(tx, sig, hashcode=SIGHASH_ALL):
    z = bin_txhash(tx, hashcode)
    _, r, s = der_decode_sig(sig)
    left = ecdsa_raw_recover(z, (0, r, s))
    right = ecdsa_raw_recover(z, (1, r, s))
    return (encode_pubkey(left, "hex"), encode_pubkey(right, "hex"))


# Scripts


def mk_pubkey_script_original(pubkey_hash: str) -> str:
    """
    Used in converting public key hash to input or output script
    """
    return (
        opcodes.OP_DUP.hex()
        + opcodes.OP_HASH160.hex()
        + "14"
        + pubkey_hash
        + opcodes.OP_EQUALVERIFY.hex()
        + opcodes.OP_CHECKSIG.hex()
    )


def mk_pubkey_script(pubkey_hash: str) -> str:
    """
    Creates a Pay-to-Public-Key-Hash (P2PKH) script for a given public key hash.

    Args:
        pubkey_hash (str): The public key hash (in hexadecimal format) for which to create the script.

    Returns:
        str: The P2PKH (Pay-to-Public-Key-Hash) script as a hexadecimal string.

    Example:
        >>> mk_pubkey_script("76a914bf5c830c87f1966621282822ac6a7c5d31a3132d88ac")
        '76a914bf5c830c87f1966621282822ac6a7c5d31a3132d88ac88ac'

    Explanation:

    The P2PKH (Pay-to-Public-Key-Hash) script is a standard script used in Bitcoin and other cryptocurrencies to
    control the spending of funds associated with a public key.

    It follows a specific structure:

        1. **OP_DUP:**
            This opcode duplicates the top item on the stack (the public key hash).

        2. **OP_HASH160:**
            This opcode calculates the hash of the top item on the stack (the duplicated public key hash).

        3. **"14":**
            This represents the length of the public key hash (20 bytes).

        4. **pubkey_hash:**
            The provided public key hash (in hexadecimal format).

        5. **OP_EQUALVERIFY:**
            This opcode checks if the hash calculated in step 2
            matches the provided public key hash. If they match,
            the script continues; otherwise, the transaction fails.

        6. **OP_CHECKSIG:**
            This opcode verifies the signature provided by
            the transaction sender against the public key
            corresponding to the public key hash. If the signature is valid,
            the transaction is considered valid.

    **What the Script Means:**

        The P2PKH(Pay-to-Public-Key-Hash) script essentially acts as a lock and key mechanism
        for Bitcoin transactions. It ensures that only the owner of the
        private key corresponding to the public key hash can spend the
        funds associated with that public key.

        - **Lock:** The script represents the lock, which can only be opened by the correct key.
        - **Key:** The private key corresponding to the public key hash is the key that can unlock the script and allow spending of funds.

    **How it Works:**

        1. When a transaction is sent to an address associated with a P2PKH(Pay-to-Public-Key-Hash) script,
            the script is executed.
        2. The script checks if the provided signature matches the public key
            corresponding to the public key hash.
        3. If the signature is valid, the transaction is considered
            valid and the funds are released to the recipient.
        4. If the signature is invalid, the transaction is rejected and the funds remain locked.

    **Key Points:**

        - **P2PKH(Pay-to-Public-Key-Hash) Script:**
            This function generates a P2PKH(Pay-to-Public-Key-Hash) script,
            which is a common and widely used script type in Bitcoin
            and other cryptocurrencies.
        - **Script Structure:**
            The script follows a specific structure with predefined
            opcodes and data elements, ensuring its functionality and
            compatibility with the Bitcoin network.
        - **Security:**
            The script's structure enforces security by requiring a valid
            signature from the private key owner to spend funds.
        - **Lock and Key:**
            The script acts as a lock and key mechanism, ensuring only
            the private key owner can unlock the funds.

    """
    return (
        opcodes.OP_DUP.hex()
        + opcodes.OP_HASH160.hex()
        + "14"
        + pubkey_hash
        + opcodes.OP_EQUALVERIFY.hex()
        + opcodes.OP_CHECKSIG.hex()
    )


def addr_to_pubkey_script_original(addr: str) -> str:
    """
    Used in converting public key hash address to input or output script
    """
    magicbyte, bin = b58check_to_hex(addr)
    return mk_pubkey_script(bin)


def addr_to_pubkey_script(addr: str) -> str:
    """
    Converts a Bitcoin address to a Pay-to-Public-Key-Hash (P2PKH) script.

    Args:
        addr (str): The Bitcoin address to convert.

    Returns:
        str: The P2PKH script as a hexadecimal string.

    Example:
        >>> addr_to_pubkey_script("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        '76a914bf5c830c87f1966621282822ac6a7c5d31a3132d88ac88ac'

    Explanation:

    This function takes a Bitcoin address as input and converts it to a P2PKH script, which is a standard script used in Bitcoin transactions to control the spending of funds associated with a public key.

    1. **Decode Address:** The function first decodes the Bitcoin address using the `b58check_to_hex` function. This function converts the base58check encoded address to its corresponding hexadecimal representation.

    2. **Extract Public Key Hash:** The decoded hexadecimal string represents the public key hash, which is the unique identifier of the address.

    3. **Create P2PKH Script:** The function then calls the `mk_pubkey_script` function to create the P2PKH script using the extracted public key hash.

    4. **Return Script:** The function returns the generated P2PKH script as a hexadecimal string.

    **How it Works:**

    The function essentially translates a human-readable Bitcoin address into a script that can be understood and executed by the Bitcoin network. This script acts as a lock and key mechanism, ensuring that only the owner of the corresponding private key can spend the funds associated with the address.

    **Key Points:**

    - **Bitcoin Address:** The function accepts a standard Bitcoin address as input.
    - **P2PKH Script:** The function generates a P2PKH script, which is a common and widely used script type in Bitcoin.
    - **Script Structure:** The script follows a specific structure with predefined opcodes and data elements, ensuring its functionality and compatibility with the Bitcoin network.
    - **Security:** The script's structure enforces security by requiring a valid signature from the private key owner to spend funds.
    - **Lock and Key:** The script acts as a lock and key mechanism, ensuring only the private key owner can unlock the funds.

    """
    from . import main

    magicbyte, decoded_binary_data_as_hexadecimal_string = main.b58check_to_hex(addr)
    P2PKH_Pay_to_Public_Key_Hash_script_as_hexadecimal_string: str = mk_pubkey_script(
        pubkey_hash=decoded_binary_data_as_hexadecimal_string
    )
    return P2PKH_Pay_to_Public_Key_Hash_script_as_hexadecimal_string


def mk_p2pk_script_original(pub: str) -> str:
    """
    Used in converting public key to p2pk script
    """
    length = hex(int(len(pub) / 2)).split("0x")[1]
    return length + pub + opcodes.OP_CHECKSIG.hex()


def mk_p2pk_script(pub: str) -> str:
    """
    Converts a public key to a Pay-to-Public-Key (P2PK) script.

    Args:
        pub (str): The public key in hexadecimal format.

    Returns:
        str: The P2PK script as a hexadecimal string.
    Example:
        >>> mk_p2pk_script("04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a27c2b22ff6c39")
        '2104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a27c2b22ff6c39ac'
    """
    length: str = hex(int(len(pub) / 2)).split("0x")[
        1
    ]  # Length of the public key in hex
    return (
        length + pub + opcodes.OP_CHECKSIG.hex()
    )  # Combining length, public key, and CHECKSIG opcode


def script_to_pk(script: str) -> str:
    """
    Used in converting p2pk script to public key
    """
    length = int(script[0:2], 16)
    return script[2 : (length + 1) * 2]


def hash_to_scripthash_script(hashbin: str) -> str:
    return opcodes.OP_HASH160.hex() + "14" + hashbin + opcodes.OP_EQUAL.hex()


def mk_scripthash_script_original(addr: str):
    """
    Used in converting p2sh address to output script
    """
    from . import main

    magicbyte, hashbin = main.b58check_to_hex(inp=addr)
    return hash_to_scripthash_script(hashbin=hashbin)


def mk_scripthash_script(addr: str):
    """
    Used in converting p2sh address to output script
    """

    magicbyte, hashbin = b58check_to_hex(addr)
    return hash_to_scripthash_script(hashbin)


def output_script_to_address_original(
    script,
    magicbyte: int = 0,
    script_magicbyte: int = 5,
    segwit_hrp: str = None,
    cash_hrp: str = None,
) -> AnyStr:
    if script.startswith("76a914") and script.endswith("88ac"):
        script = script[6:][:-4]
        return bin_to_b58check(safe_from_hex(script), magicbyte=magicbyte)
    elif script.startswith("a914") and script.endswith("87"):
        script = script[4:][:-2]
        return bin_to_b58check(safe_from_hex(script), magicbyte=script_magicbyte)
    elif script.startswith("0") and segwit_hrp:
        return decode_p2w_scripthash_script(script, 0, segwit_hrp)
    elif script.startswith("0") and cash_hrp:
        return decode_cash_scripthash_script(script, 0, cash_hrp)
    elif script.startswith("6a"):
        return binascii.unhexlify(
            "Arbitrary Data: %s" % script[2:].decode("utf-8", "ignore")
        )
    raise Exception("Unable to convert script to an address: %s" % script)


def output_script_to_address(
    script: str,
    magicbyte: int = 0,
    script_magicbyte: int = 5,
    segwit_hrp: str = None,
    cash_hrp: str = None,
) -> AnyStr:
    from . import py3specials

    if script.startswith("76a914") and script.endswith("88ac"):
        script = script[6:][:-4]
        return py3specials.bin_to_b58check(
            py3specials.safe_from_hex(script), magicbyte=magicbyte
        )
    elif script.startswith("a914") and script.endswith("87"):
        script = script[4:][:-2]
        return py3specials.bin_to_b58check(
            py3specials.safe_from_hex(script), magicbyte=script_magicbyte
        )
    elif script.startswith("0") and segwit_hrp:
        return decode_p2w_scripthash_script(script, 0, segwit_hrp)
    elif script.startswith("0") and cash_hrp:
        return decode_cash_scripthash_script(script, 0, cash_hrp)
    elif script.startswith("6a"):
        return binascii.unhexlify(
            "Arbitrary Data: %s" % script[2:].decode("utf-8", "ignore")
        )
    raise Exception("Unable to convert script to an address: %s" % script)


def decode_p2w_scripthash_script_original(script, witver, segwit_hrp):
    witprog = safe_from_hex(script[4:])
    return segwit_addr.encode_segwit_address(segwit_hrp, witver, witprog)


def decode_p2w_scripthash_script(script, witver, segwit_hrp):
    from . import py3specials

    witprog = py3specials.safe_from_hex(script[4:])
    return segwit_addr.encode_segwit_address(segwit_hrp, witver, witprog)


def decode_cash_scripthash_script_original(script, witver, hrp):
    witprog = safe_from_hex(script[4:])
    return cashaddr.encode(hrp, witver, witprog)


def decode_cash_scripthash_script(script, witver, hrp):
    from . import py3specials

    witprog = py3specials.safe_from_hex(script[4:])
    return cashaddr.encode(hrp, witver, witprog)


def mk_p2w_scripthash_script_original(witver: int, witprog: List[int]) -> str:
    """
    Used in converting a decoded pay to witness script hash address to output script
    """
    assert 0 <= witver <= 16
    OP_n = witver + int(opcodes.OP_RESERVED) if witver > 0 else 0
    length = len(witprog)
    len_hex = hex(length).split("0x")[1]
    return bytes_to_hex_string([OP_n]) + len_hex + (bytes_to_hex_string(witprog))


def mk_p2w_scripthash_script(witver: int, witprog: List[int]) -> str:
    """
    Used in converting a decoded pay to witness script hash address to output script
    """
    from . import py3specials

    assert 0 <= witver <= 16
    OP_n = witver + int(opcodes.OP_RESERVED) if witver > 0 else 0
    length = len(witprog)
    len_hex = hex(length).split("0x")[1]
    return (
        py3specials.bytes_to_hex_string([OP_n])
        + len_hex
        + (py3specials.bytes_to_hex_string(witprog))
    )


def mk_p2wpkh_redeemscript(pubkey: str) -> str:
    """
    Used in converting public key to p2wpkh script
    """
    from . import main

    return "16" + opcodes.OP_0.hex() + "14" + main.pubkey_to_hash_hex(pubkey=pubkey)


def mk_p2wpkh_script(pubkey: str) -> str:
    """
    Used in converting public key to p2wpkh script
    """
    from .main import hex_to_hash160

    script = mk_p2wpkh_redeemscript(pubkey)[2:]
    return (
        opcodes.OP_HASH160.hex()
        + "14"
        + hex_to_hash160(script)
        + opcodes.OP_EQUAL.hex()
    )


def mk_p2wpkh_scriptcode_original(pubkey):
    """
    Used in signing for tx inputs
    """
    return (
        opcodes.OP_DUP.hex()
        + opcodes.OP_HASH160.hex()
        + "14"
        + pubkey_to_hash_hex(pubkey)
        + opcodes.OP_EQUALVERIFY.hex()
        + opcodes.OP_CHECKSIG.hex()
    )


def mk_p2wpkh_scriptcode(pubkey: bytes) -> str:
    """
    Generates a P2WPKH (Pay-to-Witness-Public-Key-Hash) script code for a given public key.

    This function constructs a script code that can be used in Bitcoin transactions
    to represent a P2WPKH output. P2WPKH is a type of Bitcoin address that utilizes
    SegWit (Segregated Witness) technology for improved efficiency and security.

    Args:
        pubkey (bytes): The public key for which to generate the script code.

    Returns:
        str: The P2WPKH script code in hexadecimal format.

    Example:
        >>> pubkey = b'\x04\x88\x73\x87\x8c\x30\x9d\x32\x4b\x07\xb6\x21\x12\x0e\x90\x04\x4f\x32\x0c\x9c\x7f\x0e\x0e\x44\x99\x26\x91\x97\x36\x55\x51\x0a\x99\x9c\x9f\x0c\x6f\x9c\x0f\x0e\x0b\x2c\x25\x24\x2a\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        >>> mk_p2wpkh_scriptcode(pubkey)
        '76a91414' + main.pubkey_to_hash_hex(pubkey=pubkey) + '88ac'
    """
    from . import main

    return (
        opcodes.OP_DUP.hex()
        + opcodes.OP_HASH160.hex()
        + "14"
        + main.pubkey_to_hash_hex(pubkey=pubkey)
        + opcodes.OP_EQUALVERIFY.hex()
        + opcodes.OP_CHECKSIG.hex()
    )


def p2wpkh_nested_script(pubkey):
    return opcodes.OP_0.hex() + "14" + hash160(safe_from_hex(pubkey))


# Output script to address representation


def deserialize_script(script):
    if isinstance(script, str) and is_hex(script):
        return json_changebase(
            deserialize_script(binascii.unhexlify(script)), lambda x: safe_hexlify(x)
        )
    out, pos = [], 0
    while pos < len(script):
        code = from_byte_to_int(script[pos])
        if code == 0:
            out.append(None)
            pos += 1
        elif code <= 75:
            out.append(script[pos + 1 : pos + 1 + code])
            pos += 1 + code
        elif code <= 78:
            szsz = pow(2, code - 76)
            sz = decode(script[pos + szsz : pos : -1], 256)
            out.append(script[pos + 1 + szsz : pos + 1 + szsz + sz])
            pos += 1 + szsz + sz
        elif code <= 96:
            out.append(code - 80)
            pos += 1
        else:
            out.append(code)
            pos += 1
    return out


def serialize_script_unit_original(unit):
    if isinstance(unit, int):
        if unit < 16:
            return from_int_to_byte(unit + 80)
        else:
            return from_int_to_byte(unit)
    elif unit is None:
        return b"\x00"
    else:
        if len(unit) <= 75:
            return from_int_to_byte(len(unit)) + unit
        elif len(unit) < 256:
            return from_int_to_byte(76) + from_int_to_byte(len(unit)) + unit
        elif len(unit) < 65536:
            return from_int_to_byte(77) + encode(len(unit), 256, 2)[::-1] + unit
        else:
            return from_int_to_byte(78) + encode(len(unit), 256, 4)[::-1] + unit


def serialize_script_unit(unit: Union[int, bytes, None]) -> bytes:
    """
    Serializes a single unit of a script.

    This function takes a single unit of a script (`unit`) and returns its
    serialized representation. It handles different types of units, including:

    - Integers: Represent opcodes.
    - Bytes: Represent data.
    - None: Represents an empty byte.

    Args:
        unit: The single unit of the script to serialize.

    Returns:
        bytes: The serialized unit as bytes.

    Example:
        >>> serialize_script_unit(81)  # OP_DUP
        b'\x76'
        >>> serialize_script_unit(b'\x14\x95\x4e\x56\x4d\x7c\x93\x40\x7a\xa1\x7b\x72\x52\x85\x6a\x61\x1f\x2c\x9c\x84\x55\x67\x0e\x10\x04\x78\x91\x76\x64\x8f')  # Public key hash
        b'\x14\x95\x4e\x56\x4d\x7c\x93\x40\x7a\xa1\x7b\x72\x52\x85\x6a\x61\x1f\x2c\x9c\x84\x55\x67\x0e\x10\x04\x78\x91\x76\x64\x8f'
        >>> serialize_script_unit(None)  # Empty byte
        b'\x00'
    """
    from . import py3specials

    if isinstance(unit, int):
        if unit < 16:
            return py3specials.from_int_to_byte(a=unit + 80)
        else:
            return py3specials.from_int_to_byte(a=unit)
    elif unit is None:
        return b"\x00"
    else:
        if len(unit) <= 75:
            return py3specials.from_int_to_byte(a=len(unit)) + unit
        elif len(unit) < 256:
            return (
                py3specials.from_int_to_byte(a=76)
                + py3specials.from_int_to_byte(a=len(unit))
                + unit
            )
        elif len(unit) < 65536:
            return (
                py3specials.from_int_to_byte(a=77)
                + py3specials.encode(val=len(unit), base=256, minlen=2)[::-1]
                + unit
            )
        else:
            return (
                py3specials.from_int_to_byte(a=78)
                + py3specials.encode(val=len(unit), base=256, minlen=4)[::-1]
                + unit
            )


def serialize_script_original(script) -> AnyStr:
    if json_is_base(script, 16):
        return safe_hexlify(
            serialize_script(json_changebase(script, lambda x: binascii.unhexlify(x)))
        )

    result = bytes()
    for b in map(serialize_script_unit, script):
        result += b if isinstance(b, bytes) else bytes(b, "utf-8")
    return result


def serialize_script(
    script: Union[str, List[Union[str, bytes]]],
) -> AnyStr:
    """
    Serializes a script object.

    This function takes a script object (`script`) and returns a serialized
    representation of the script. It handles both hexadecimal and binary
    representations of the script.

    Args:
        script: The script object to serialize. It can be a string (hexadecimal
            representation) or a list of strings and bytes.

    Returns:
        AnyStr: The serialized script as a string or bytes.

    Example:
        >>> serialize_script('01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000')
        '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000'
        >>> serialize_script(['OP_DUP', 'OP_HASH160', b'\x14\x95\x4e\x56\x4d\x7c\x93\x40\x7a\xa1\x7b\x72\x52\x85\x6a\x61\x1f\x2c\x9c\x84\x55\x67\x0e\x10\x04\x78\x91\x76\x64\x8f', 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
        '76a914954e564d7c93407aaa17b7252856a611f2c9c8455670e1004789176648f88ac'
    """
    from . import py3specials

    if json_is_base(script, 16):
        return py3specials.safe_hexlify(
            serialize_script(json_changebase(script, lambda x: binascii.unhexlify(x)))
        )
    result: bytes = bytes()
    for b in map(serialize_script_unit, script):
        result += b if isinstance(b, bytes) else bytes(b, "utf-8")
    return result


def mk_multisig_script(*args):  # [pubs],k or pub1,pub2...pub[n],M
    """
    :param args: List of public keys to used to create multisig and M, the number of signatures required to spend
    :return: multisig script
    """
    if isinstance(args[0], list):
        pubs, M = args[0], int(args[1])
    else:
        pubs = list(filter(lambda x: len(str(x)) >= 32, args))
        M = int(args[len(pubs)])
    N = len(pubs)
    return serialize_script([M] + pubs + [N] + [opcodes.OP_CHECKMULTISIG])


# Signing and verifying


def verify_tx_input(tx, i, script, sig, pub):
    if is_hex(tx):
        tx = binascii.unhexlify(tx)
    if is_hex(script):
        script = binascii.unhexlify(script)
    if isinstance(script, string_types) and is_hex(script):
        sig = safe_hexlify(sig)
    hashcode = decode(sig[-2:], 16)
    modtx = signature_form(tx, int(i), script, hashcode)
    return ecdsa_tx_verify(modtx, sig, pub, hashcode)


def multisign(
    tx, i: int, script, pk, hashcode: int = SIGHASH_ALL, segwit: bool = False
):
    modtx = signature_form(tx, i, script, hashcode, segwit=segwit)
    return ecdsa_tx_sign(modtx, pk, hashcode)


def apply_multisignatures(
    txobj: Union[Tx, str], i: int, script, *args, segwit: bool = False
):
    # tx,i,script,sigs OR tx,i,script,sig1,sig2...,sig[n]
    sigs = args[0] if isinstance(args[0], list) else list(args)

    if isinstance(script, str) and re.match("^[0-9a-fA-F]*$", script):
        script = binascii.unhexlify(script)
    sigs = [binascii.unhexlify(x) if x[:2] == "30" else x for x in sigs]
    if not isinstance(txobj, dict):
        txobj = deserialize(txobj)
    if isinstance(txobj, str) and re.match("^[0-9a-fA-F]*$", txobj):
        return safe_hexlify(
            serialize(apply_multisignatures(binascii.unhexlify(txobj), i, script, sigs))
        )

    if not isinstance(txobj, dict):
        txobj = deserialize(txobj)

    if segwit:
        if "witness" not in txobj.keys():
            txobj.update({"marker": 0, "flag": 1, "witness": []})
            for _ in range(0, i):
                witness: Witness = {"number": 0, "scriptCode": ""}
                # Pycharm IDE gives a type error for the following line, no idea why...
                # noinspection PyTypeChecker
                txobj["witness"].append(witness)
        txobj["ins"][i]["script"] = ""
        number = len(sigs) + 2
        scriptSig = safe_hexlify(
            serialize_script([None] + sigs + [len(script)] + deserialize_script(script))
        )
        witness: Witness = {"number": number, "scriptCode": scriptSig}
        # Pycharm IDE gives a type error for the following line, no idea why...
        # noinspection PyTypeChecker
        txobj["witness"].append(witness)
    else:
        # Not pushing empty elements on the top of the stack if passing no
        # script (in case of bare multisig inputs there is no script)
        script_blob = [] if script.__len__() == 0 else [script]
        scriptSig = safe_hexlify(serialize_script([None] + sigs + script_blob))
        txobj["ins"][i]["script"] = scriptSig
        if "witness" in txobj.keys():
            witness: Witness = {"number": 0, "scriptCode": ""}
            # Pycharm IDE gives a type error for the following line, no idea why...
            # noinspection PyTypeChecker
            txobj["witness"].append(witness)
    return txobj


def select_original(unspents, value: int):
    value = int(value)
    high = [u for u in unspents if u["value"] >= value]
    high.sort(key=lambda u: u["value"])
    low = [u for u in unspents if u["value"] < value]
    low.sort(key=lambda u: -u["value"])
    if len(high):
        return [high[0]]
    i, tv = 0, 0
    while tv < value and i < len(low):
        tv += low[i]["value"]
        i += 1
    if tv < value:
        raise Exception("Not enough funds")
    return low[:i]


from typing import List, Dict
from .electrumx_client.types import (
    # ElectrumXBlockHeaderNotification,
    # ElectrumXHistoryResponse,
    # ElectrumXBalanceResponse,
    ElectrumXUnspentResponse,
    # ElectrumXTx,
    # ElectrumXMerkleResponse,
    # ElectrumXMultiBalanceResponse,
    # ElectrumXMultiTxResponse,
    # ElectrumXVerboseTX,
)


def select(
    unspents: ElectrumXUnspentResponse,
    value: int,
) -> List[Dict[str, int]]:
    """
    Selects a set of unspent units to reach a target value.

    This function attempts to find a combination of unspent units from a given list
    that sums up to the specified target value. It prioritizes selecting the smallest
    unit with sufficient value if available. If not, it tries to find a combination of
    smaller units.

    Args:
        unspents(ElectrumXUnspentResponse): A list of dictionaries, where each dictionary represents an unspent
            unit with a key "value" indicating its value.
        value: An integer representing the target value to be reached.

    Returns:
        A list of dictionaries representing the selected unspent units.

    Raises:
        Exception: If there are not enough unspent units to reach the target value.
    """
    value = int(value)
    high: List[Dict[str, int]] = [u for u in unspents if u["value"] >= value]
    high.sort(key=lambda u: u["value"])
    low: List[Dict[str, int]] = [u for u in unspents if u["value"] < value]
    low.sort(key=lambda u: -u["value"])
    if len(high):
        return [high[0]]
    i: int = 0
    tv: int = 0
    while tv < value and i < len(low):
        tv += low[i]["value"]
        i += 1
    if tv < value:
        message: str = f"Not enough funds (tv:{tv})<(value:{value})"
        print(message)
        raise Exception(message)
    return low[:i]
