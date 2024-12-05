import array
from .main import *
import hmac
import hashlib
from typing import AnyStr, Tuple, Dict

# Electrum wallets


def electrum_stretch(seed):
    return slowsha(seed)


# Accepts seed or stretched seed, returns master public key


def electrum_mpk(seed):
    if len(seed) == 32:
        seed = electrum_stretch(seed)
    return privkey_to_pubkey(seed)[2:]


# Accepts (seed or stretched seed), index and secondary index
# (conventionally 0 for ordinary address_derivations, 1 for change) , returns privkey


def electrum_privkey(seed, n, for_change=0):
    if len(seed) == 32:
        seed = electrum_stretch(seed)
    mpk = electrum_mpk(seed)
    offset = dbl_sha256(
        from_int_representation_to_bytes(n)
        + b":"
        + from_int_representation_to_bytes(for_change)
        + b":"
        + binascii.unhexlify(mpk)
    )
    return add_privkeys(seed, offset)


# Accepts (seed or stretched seed or master pubkey), index and secondary index
# (conventionally 0 for ordinary address_derivations, 1 for change) , returns pubkey


def electrum_pubkey(masterkey: AnyStr, n: int, for_change: int = 0) -> AnyStr:
    if len(masterkey) == 32:
        mpk = electrum_mpk(electrum_stretch(masterkey))
    elif len(masterkey) == 64:
        mpk = electrum_mpk(masterkey)
    else:
        mpk = masterkey
    bin_mpk = encode_pubkey(mpk, "bin_electrum")
    offset = bin_dbl_sha256(
        from_int_representation_to_bytes(n)
        + b":"
        + from_int_representation_to_bytes(for_change)
        + b":"
        + bin_mpk
    )
    return add_pubkeys("04" + mpk, privtopub(offset))


# seed/stretched seed/pubkey -> address (convenience method)


def electrum_address(masterkey, n, for_change=0, magicbyte=0):
    return pubkey_to_address(electrum_pubkey(masterkey, n, for_change), magicbyte)


# Given a master public key, a private key from that wallet and its index,
# cracks the secret exponent which can be used to generate all other private
# keys in the wallet


def crack_electrum_wallet(mpk, pk, n, for_change=0):
    bin_mpk = encode_pubkey(mpk, "bin_electrum")
    offset = dbl_sha256(str(n) + ":" + str(for_change) + ":" + bin_mpk)
    return subtract_privkeys(pk, offset)


# # Below code ASSUMES binary inputs and compressed pubkeys
# MAINNET_PRIVATE = b"\x04\x88\xAD\xE4"
# MAINNET_PUBLIC = b"\x04\x88\xB2\x1E"
# TESTNET_PRIVATE = b"\x04\x35\x83\x94"
# TESTNET_PUBLIC = b"\x04\x35\x87\xCF"
# PRIVATE = [MAINNET_PRIVATE, TESTNET_PRIVATE]
# PUBLIC = [MAINNET_PUBLIC, TESTNET_PUBLIC]
# # DEFAULT = (MAINNET_PRIVATE, MAINNET_PUBLIC)
# DEFAULT: List[bytes, bytes] = [MAINNET_PRIVATE, MAINNET_PUBLIC]

from typing import List, Tuple

# Below code ASSUMES binary inputs and compressed pubkeys
MAINNET_PRIVATE: bytes = b"\x04\x88\xAD\xE4"
MAINNET_PUBLIC: bytes = b"\x04\x88\xB2\x1E"
TESTNET_PRIVATE: bytes = b"\x04\x35\x83\x94"
TESTNET_PUBLIC: bytes = b"\x04\x35\x87\xCF"
PRIVATE: List[bytes] = [MAINNET_PRIVATE, TESTNET_PRIVATE]
PUBLIC: List[bytes] = [MAINNET_PUBLIC, TESTNET_PUBLIC]
# DEFAULT = (MAINNET_PRIVATE, MAINNET_PUBLIC)
DEFAULT: List[bytes] = [MAINNET_PRIVATE, MAINNET_PUBLIC]


# BIP32 child key derivation


# from . import main
def raw_bip32_ckd_original(rawtuple, i, prefixes=DEFAULT):
    vbytes, depth, fingerprint, oldi, chaincode, key = rawtuple
    i = int(i)

    private = vbytes == prefixes[0]

    if private:
        priv = key
        pub = privtopub(key)
    else:
        priv = None
        pub = key
    from . import py3specials

    if i >= 2**31:
        if not priv:
            raise Exception("Can't do private derivation on public key!")
        I = hmac.new(
            chaincode,
            b"\x00" + priv[:32] + py3specials.encode(val=i, base=256, minlen=4),
            hashlib.sha512,
        ).digest()
    else:
        I = hmac.new(
            chaincode,
            pub + py3specials.encode(val=i, base=256, minlen=4),
            hashlib.sha512,
        ).digest()
    if private:
        newkey = add_privkeys(I[:32] + b"\x01", priv)
        fingerprint = bin_hash160(privtopub(key))[:4]
    else:
        newkey = add_pubkeys(compress(privtopub(I[:32])), key)
        fingerprint = bin_hash160(key)[:4]

    return (vbytes, depth + 1, fingerprint, i, I[32:], newkey)


def raw_bip32_ckd(
    rawtuple: Tuple[bytes, int, bytes, int, bytes, bytes],
    i: Union[int, str],
    prefixes: List[bytes] = DEFAULT,
) -> Tuple[bytes, int, bytes, int, bytes, bytes]:
    """
    Performs a BIP32 child key derivation.

    This function implements the BIP32 child key derivation algorithm, taking
    a tuple representing the parent key and an index as input, and returning
    a tuple representing the child key.

    Args:
        rawtuple (Tuple[bytes, int, bytes, int, bytes, bytes]): A tuple
            representing the parent key, containing:
            - vbytes (bytes): The version bytes.
            - depth (int): The depth of the key.
            - fingerprint (bytes): The fingerprint of the parent key.
            - oldi (int): The index of the key.
            - chaincode (bytes): The chain code of the key.
            - key (bytes): The public or private key.
        i (Union[int, str]): The index of the child key.
        prefixes (List[bytes], optional): A list of version bytes for different
            key types. Defaults to DEFAULT.

    Returns:
        Tuple[bytes, int, bytes, int, bytes, bytes]: A tuple representing the
            child key, containing the same elements as the input tuple.
    """
    vbytes, depth, fingerprint, oldi, chaincode, key = rawtuple
    i = int(i)
    from . import main

    private = vbytes == prefixes[0]

    if private:
        priv: bytes = key
        pub: bytes = main.privtopub(privkey=key)
    else:
        priv: bytes = None
        pub: bytes = key
    from . import py3specials

    if i >= 2**31:
        if not priv:
            raise Exception("Can't do private derivation on public key!")
        I: bytes = hmac.new(
            chaincode,
            b"\x00" + priv[:32] + py3specials.encode(val=i, base=256, minlen=4),
            hashlib.sha512,
        ).digest()
    else:
        I: bytes = hmac.new(
            chaincode,
            pub + py3specials.encode(val=i, base=256, minlen=4),
            hashlib.sha512,
        ).digest()
    if private:
        newkey: bytes = main.add_privkeys(I[:32] + b"\x01", priv)
        fingerprint: bytes = main.bin_hash160(main.privtopub(privkey=key))[:4]
    else:
        newkey: bytes = main.add_pubkeys(
            main.compress(main.privtopub(privkey=I[:32])), key
        )
        fingerprint: bytes = main.bin_hash160(string=key)[:4]

    return (vbytes, depth + 1, fingerprint, i, I[32:], newkey)


# def encode(
#     # self,
#     val: int,
#     base: int,
#     minlen: int = 0,
# ):
#     from . import py3specials

#     py3specials.encode(
#         val=val,
#         base=base,
#         minlen=minlen,
#     )


def bip32_serialize_original(rawtuple, prefixes=DEFAULT):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    from . import py3specials

    i = py3specials.encode(val=i, base=256, minlen=4)
    from .main import hash_to_int, from_int_to_byte

    chaincode = py3specials.encode(val=hash_to_int(x=chaincode), base=256, minlen=32)
    keydata = b"\x00" + key[:-1] if vbytes == prefixes[0] else key
    bindata = (
        vbytes + from_int_to_byte(a=depth % 256) + fingerprint + i + chaincode + keydata
    )

    return changebase(
        string=bindata + bin_dbl_sha256(s=bindata)[:4],
        frm=256,
        to=58,
    )


def bip32_serialize(
    rawtuple: Tuple[bytes, int, bytes, int, bytes, bytes],
    prefixes: List[bytes] = DEFAULT,
) -> str:
    """
    Serializes a BIP32 extended key tuple into a base58-encoded string.

    This function takes a tuple containing the components of a BIP32 extended
    key and serializes it into a base58-encoded string according to the BIP32
    specification.

    Args:
        rawtuple (Tuple[bytes, int, bytes, int, bytes, bytes]): A tuple containing
            the following elements:
            - vbytes (bytes): The version bytes.
            - depth (int): The depth of the key.
            - fingerprint (bytes): The fingerprint of the parent key.
            - i (int): The index of the key.
            - chaincode (bytes): The chain code of the key.
            - key (bytes): The public or private key.
        prefixes (Dict[str, bytes], optional): A dictionary mapping key prefixes
            to their corresponding version bytes. Defaults to DEFAULT.

    Returns:
        str: The base58-encoded string representation of the extended key.
    """
    vbytes: bytes
    depth: int
    fingerprint: bytes
    i: int
    chaincode: bytes
    key: bytes
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    from . import py3specials

    i: bytes = py3specials.encode(val=i, base=256, minlen=4)
    from .main import hash_to_int, from_int_to_byte, bin_dbl_sha256

    chaincode: bytes = py3specials.encode(
        val=hash_to_int(x=chaincode), base=256, minlen=32
    )
    keydata: bytes = b"\x00" + key[:-1] if vbytes == prefixes[0] else key
    bindata: bytes = (
        vbytes + from_int_to_byte(a=depth % 256) + fingerprint + i + chaincode + keydata
    )

    base_58_encoded_string: str = py3specials.changebase(
        string=bindata + bin_dbl_sha256(s=bindata)[:4],
        frm=256,
        to=58,
    )
    return base_58_encoded_string


def bip32_deserialize_original(data, prefixes=DEFAULT):
    from . import py3specials

    dbin = py3specials.changebase(data, 58, 256)
    if bin_dbl_sha256(dbin[:-4])[:4] != dbin[-4:]:
        raise Exception("Invalid checksum")
    vbytes = dbin[0:4]
    depth = from_byte_to_int(dbin[4])
    fingerprint = dbin[5:9]
    i = decode(dbin[9:13], 256)
    chaincode = dbin[13:45]
    key = dbin[46:78] + b"\x01" if vbytes == prefixes[0] else dbin[45:78]
    return (vbytes, depth, fingerprint, i, chaincode, key)


def bip32_deserialize(
    data: str,
    prefixes: List[bytes] = DEFAULT,
) -> Tuple[bytes, int, bytes, int, bytes, bytes]:
    """
    Deserializes a base58-encoded BIP32 extended key string into a tuple.

    This function takes a base58-encoded string representing a BIP32 extended
    key and deserializes it into a tuple containing the components of the key.

    Args:
        data (str): The base58-encoded string representing the extended key.
        prefixes (List[bytes], optional): A list of version bytes for different
            key types. Defaults to DEFAULT.

    Returns:
        Tuple[bytes, int, bytes, int, bytes, bytes]: A tuple containing the
            following elements:
            - vbytes (bytes): The version bytes.
            - depth (int): The depth of the key.
            - fingerprint (bytes): The fingerprint of the parent key.
            - i (int): The index of the key.
            - chaincode (bytes): The chain code of the key.
            - key (bytes): The public or private key.
    """
    from . import py3specials
    from . import main

    dbin: bytes = py3specials.changebase(string=data, frm=58, to=256)
    if main.bin_dbl_sha256(s=dbin[:-4])[:4] != dbin[-4:]:
        raise Exception("Invalid checksum")
    vbytes: bytes = dbin[0:4]
    depth: int = main.from_byte_to_int(a=dbin[4])
    fingerprint: bytes = dbin[5:9]
    i: int = py3specials.decode(string=dbin[9:13], base=256)
    chaincode: bytes = dbin[13:45]
    key: bytes = dbin[46:78] + b"\x01" if vbytes == prefixes[0] else dbin[45:78]
    return (vbytes, depth, fingerprint, i, chaincode, key)


def is_xprv(text, prefixes=DEFAULT):
    try:
        vbytes, depth, fingerprint, i, chaincode, key = bip32_deserialize(
            text, prefixes
        )
        return vbytes == prefixes[0]
    except:
        return False


def is_xpub(text, prefixes=DEFAULT):
    try:
        vbytes, depth, fingerprint, i, chaincode, key = bip32_deserialize(
            text, prefixes
        )
        return vbytes == prefixes[1]
    except:
        return False


def raw_bip32_privtopub_original(rawtuple, prefixes=DEFAULT):
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    newvbytes = prefixes[1]
    return (newvbytes, depth, fingerprint, i, chaincode, privtopub(key))


def raw_bip32_privtopub(
    rawtuple: Tuple[bytes, int, bytes, int, bytes, bytes],
    prefixes: List[bytes] = DEFAULT,
) -> Tuple[bytes, int, bytes, int, bytes, bytes]:
    """
    Converts a BIP32 private key tuple to a public key tuple.

    This function takes a tuple representing a BIP32 private key and converts
    it to a tuple representing the corresponding public key, by changing the
    version bytes and converting the private key to a public key.

    Args:
        rawtuple (Tuple[bytes, int, bytes, int, bytes, bytes]): A tuple
            representing the private key, containing:
            - vbytes (bytes): The version bytes.
            - depth (int): The depth of the key.
            - fingerprint (bytes): The fingerprint of the parent key.
            - i (int): The index of the key.
            - chaincode (bytes): The chain code of the key.
            - key (bytes): The private key.
        prefixes (List[bytes], optional): A list of version bytes for different
            key types. Defaults to DEFAULT.

    Returns:
        Tuple[bytes, int, bytes, int, bytes, bytes]: A tuple representing the
            public key, containing the same elements as the input tuple, except
            for the version bytes and the key, which are replaced with the
            public key version bytes and the public key, respectively.
    """
    vbytes, depth, fingerprint, i, chaincode, key = rawtuple
    newvbytes: bytes = prefixes[1]
    from . import main

    return (newvbytes, depth, fingerprint, i, chaincode, main.privtopub(privkey=key))


def bip32_privtopub(data, prefixes=DEFAULT):
    return bip32_serialize(
        raw_bip32_privtopub(bip32_deserialize(data, prefixes), prefixes), prefixes
    )


def bip32_ckd(
    key,
    path,
    prefixes: List[bytes] = DEFAULT,
    public=False,
):
    if isinstance(path, (list, tuple)):
        pathlist = map(str, path)
    else:
        path = str(path)
        pathlist = parse_bip32_path(path)
    for i, p in enumerate(pathlist):
        key = bip32_serialize(
            raw_bip32_ckd(bip32_deserialize(key, prefixes), p, prefixes), prefixes
        )
    return key if not public else bip32_privtopub(key)


# def bip32_master_key(seed, prefixes=DEFAULT):
#     from .main import from_string_to_bytes

#     I = hmac.new(
#         from_string_to_bytes(a="Bitcoin seed"),
#         from_string_to_bytes(a=seed),
#         hashlib.sha512,
#     ).digest()
#     return bip32_serialize(
#         (prefixes[0], 0, b"\x00" * 4, 0, I[32:], I[:32] + b"\x01"), prefixes
#     )


def bip32_master_key_original(seed, prefixes=DEFAULT):
    from .main import from_string_to_bytes

    I = hmac.new(
        from_string_to_bytes(a="Bitcoin seed"),
        from_string_to_bytes(a=seed),
        hashlib.sha512,
    ).digest()
    return bip32_serialize(
        (prefixes[0], 0, b"\x00" * 4, 0, I[32:], I[:32] + b"\x01"), prefixes
    )


def bip32_master_key(seed, prefixes=DEFAULT):
    from .main import from_string_to_bytes

    I: bytes = hmac.new(
        from_string_to_bytes(a="Bitcoin seed"),
        from_string_to_bytes(a=seed),
        hashlib.sha512,
    ).digest()
    version_bytesbytes: bytes = prefixes[0]
    key_depth: int = 0
    parent_key_fingerprint: bytes = b"\x00" * 4  # The fingerprint of the parent key.
    key_index: int = 0  # The index of the key.
    chaincode: bytes = I[32:]  # The chain code of the key.
    key: bytes = I[:32] + b"\x01"  # The public or private key.
    raw_tuple: Tuple[bytes, int, bytes, int, bytes, bytes] = (
        version_bytesbytes,
        key_depth,
        parent_key_fingerprint,
        key_index,
        chaincode,
        key,
    )
    base_58_encoded_string: str = bip32_serialize(
        rawtuple=raw_tuple,
        prefixes=prefixes,
    )
    return base_58_encoded_string


def bip32_bin_extract_key(data, prefixes=DEFAULT):
    return bip32_deserialize(data, prefixes)[-1]


def bip32_extract_key_original(data, prefixes=DEFAULT):
    return safe_hexlify(bip32_deserialize(data, prefixes)[-1])


def bip32_extract_key(data, prefixes=DEFAULT):
    from . import py3specials

    bip_32_deserialized: Tuple[bytes, int, bytes, int, bytes, bytes] = (
        bip32_deserialize(data=data, prefixes=prefixes)[-1]
    )
    hex_bytes_object: str = py3specials.safe_hexlify(a=bip_32_deserialized)
    return hex_bytes_object


def bip32_derive_key(key, path, prefixes=DEFAULT, **kwargs):
    return bip32_extract_key(bip32_ckd(key, path, prefixes, **kwargs), prefixes)


# Exploits the same vulnerability as above in Electrum wallets
# Takes a BIP32 pubkey and one of the child privkeys of its corresponding
# privkey and returns the BIP32 privkey associated with that pubkey


def raw_crack_bip32_privkey(parent_pub, priv, prefixes=DEFAULT):
    vbytes, depth, fingerprint, i, chaincode, key = priv
    pvbytes, pdepth, pfingerprint, pi, pchaincode, pkey = parent_pub
    i = int(i)

    if i >= 2**31:
        raise Exception("Can't crack private derivation!")
    from . import py3specials

    I = hmac.new(
        pchaincode, pkey + py3specials.encode(val=i, base=256, minlen=4), hashlib.sha512
    ).digest()

    pprivkey = subtract_privkeys(key, I[:32] + b"\x01")

    newvbytes = prefixes[0]
    return (newvbytes, pdepth, pfingerprint, pi, pchaincode, pprivkey)


def crack_bip32_privkey(parent_pub, priv, prefixes=DEFAULT):
    dsppub = bip32_deserialize(parent_pub, prefixes)
    dspriv = bip32_deserialize(priv, prefixes)
    return bip32_serialize(raw_crack_bip32_privkey(dsppub, dspriv, prefixes), prefixes)


def coinvault_pub_to_bip32(*args, prefixes=DEFAULT):
    if len(args) == 1:
        args = args[0].split(" ")
    vals = map(int, args[34:])
    I1 = "".join(map(chr, vals[:33]))
    I2 = "".join(map(chr, vals[35:67]))
    return bip32_serialize((prefixes[1], 0, b"\x00" * 4, 0, I2, I1))


def coinvault_priv_to_bip32(*args, prefixes=DEFAULT):
    if len(args) == 1:
        args = args[0].split(" ")
    vals = map(int, args[34:])
    I2 = "".join(map(chr, vals[35:67]))
    I3 = "".join(map(chr, vals[72:104]))
    return bip32_serialize((prefixes[0], 0, b"\x00" * 4, 0, I2, I3 + b"\x01"))


def bip32_descend(*args, prefixes=DEFAULT):
    """Descend masterkey and return privkey"""
    if len(args) == 2 and isinstance(args[1], list):
        key, path = args
    elif len(args) == 2 and isinstance(args[1], string_types):
        key = args[0]
        path = map(int, str(args[1]).lstrip("mM/").split("/"))
    elif len(args):
        key, path = args[0], map(int, args[1:])
    for p in path:
        key = bip32_ckd(key, p, prefixes)
    return bip32_extract_key(key, prefixes)


def parse_bip32_path_original(path: str):
    """Takes bip32 path, "m/0'/2H" or "m/0H/1/2H/2/1000000000.pub", returns list of ints"""
    path_without_whitespaces = path.lstrip("m/").rstrip(".pub")
    if not path_without_whitespaces:
        return []
    # elif path.endswith("/"):       incorrect for electrum segwit
    #    path += "0"
    patharr = []
    for v in path_without_whitespaces.split("/"):
        if not v:
            continue
        elif v[-1] in ("'H"):  # hardened path
            v = int(v[:-1]) | 0x80000000
        else:  # non-hardened path
            v = int(v) & 0x7FFFFFFF
        patharr.append(v)
    return patharr


# from typing import List


def parse_bip32_path(path: str) -> List[int]:
    """
    Parses a BIP32 path string into a list of integers.

    This function takes a BIP32 path string, such as "m/0'/2H" or
    "m/0H/1/2H/2/1000000000.pub", and converts it into a list of
    integers representing the path components.

    Args:
        path (str): The BIP32 path string to parse.

    Returns:
        List[int]: A list of integers representing the path components.
    """
    path_without_whitespaces: str = path.lstrip("m/").rstrip(".pub")
    if not path_without_whitespaces:
        return []
    # elif path.endswith("/"):       incorrect for electrum segwit
    #    path += "0"
    patharr: List[int] = []
    for v in path_without_whitespaces.split("/"):
        if not v:
            continue
        elif v[-1] in ("'H"):  # hardened path
            v = int(v[:-1]) | 0x80000000
        else:  # non-hardened path
            v = int(v) & 0x7FFFFFFF
        patharr.append(v)
    return patharr
