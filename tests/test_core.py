"""
Unit tests for the core greeting logic.
"""

import pytest
from app.core import say_hello
from app.exceptions import HelloError

@pytest.mark.asyncio
async def test_default_greeting():
    greeting = await say_hello()
    assert greeting == "Hello, World!"

@pytest.mark.asyncio
async def test_custom_greeting():
    greeting = await say_hello("Alice")
    assert greeting == "Hello, Alice!"

@pytest.mark.asyncio
async def test_name_with_whitespace():
    greeting = await say_hello("   Bob   ")
    assert greeting == "Hello, Bob!"

@pytest.mark.asyncio
async def test_invalid_name_raises():
    with pytest.raises(HelloError):
        await say_hello("123Invalid")

@pytest.mark.asyncio
async def test_empty_string_falls_back_to_default():
    greeting = await say_hello("")
    assert greeting == "Hello, World!"
