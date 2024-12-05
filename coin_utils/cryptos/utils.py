# Electrum - lightweight Bitcoin client
# Copyright (C) 2011 Thomas Voegtlin
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
from typing import AsyncGenerator, List, Any, Optional, AnyStr, Match


def user_dir(appname: str) -> Optional[str]:
    if os.name == "posix":
        return os.path.join(os.environ["HOME"], ".%s" % appname.lower())
    elif "APPDATA" in os.environ:
        return os.path.join(os.environ["APPDATA"], appname.capitalize())
    elif "LOCALAPPDATA" in os.environ:
        return os.path.join(os.environ["LOCALAPPDATA"], appname.capitalize())
    else:
        # raise Exception("No home directory found in environment variables.")
        return


async def alist_original(generator: AsyncGenerator[Any, None]) -> List[Any]:
    return [i async for i in generator]


async def alist(self, generator: AsyncGenerator[Any, None]) -> List[Any]:
    """
    Converts an asynchronous generator to a list.

    This function iterates through the provided asynchronous generator and collects all the yielded values into a list.

    Args:
        generator: An asynchronous generator that yields values of any type.

    Returns:
        A list containing all the values yielded by the asynchronous generator.
    """
    result: List[Any] = [i async for i in generator]
    return result  # [i async for i in generator]


def is_hex_original(text: str) -> Optional[Match[AnyStr]]:
    regex = "^[0-9a-fA-F]*$"
    if isinstance(text, bytes):
        regex = regex.encode()
    return re.match(regex, text)


def is_hex(text: str) -> Optional[Match[AnyStr]]:
    """
    Checks if a string is a hexadecimal string.

    This function uses a regular expression to determine if the
    input string consists only of hexadecimal characters
    (0-9 and a-f, case-insensitive).
    **A hexadecimal character is a digit from 0 to 9 or
    a letter from a to f (case-insensitive), representing a value in base-16.**
    **Hexadecimal numbers are often used in computer programming
    and data representation, particularly for representing memory
    addresses, colors, and other binary data.**
    This is useful for validating hexadecimal values, such as when
    parsing data from a database or a file.

    Args:
        text: The string to be checked.

    Returns:
        A Match object if the string is a hexadecimal string, otherwise None.
    """
    regex: str = "^[0-9a-fA-F]*$"
    if isinstance(text, bytes):
        regex = regex.encode()
    return re.match(regex, text)
