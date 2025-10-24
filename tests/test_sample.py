"""
Sample test file with Allure annotations for qa-lab project.
"""

import asyncio

import allure
import pytest


class TestSample:
    """Sample test class with Allure annotations."""

    @allure.feature("Basic Functionality")
    @allure.story("Simple Math Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Test basic addition operation")
    def test_addition(self):
        """Test basic addition functionality."""
        with allure.step("Perform addition"):
            result = 2 + 3

        with allure.step("Verify result"):
            assert result == 5

    @allure.feature("Basic Functionality")
    @allure.story("Simple Math Operations")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Test basic subtraction operation")
    def test_subtraction(self):
        """Test basic subtraction functionality."""
        with allure.step("Perform subtraction"):
            result = 10 - 4

        with allure.step("Verify result"):
            assert result == 6

    @allure.feature("Async Operations")
    @allure.story("Async Math Operations")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Test async multiplication operation")
    @pytest.mark.asyncio
    async def test_async_multiplication(self):
        """Test async multiplication functionality."""
        with allure.step("Simulate async operation"):
            await asyncio.sleep(0.1)  # Simulate async work

        with allure.step("Perform multiplication"):
            result = 3 * 4

        with allure.step("Verify result"):
            assert result == 12

    @allure.feature("Error Handling")
    @allure.story("Exception Testing")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("Test division by zero exception")
    def test_division_by_zero(self):
        """Test division by zero raises appropriate exception."""
        with allure.step("Attempt division by zero"):
            with pytest.raises(ZeroDivisionError):
                _ = 10 / 0

    @allure.feature("Data Validation")
    @allure.story("String Operations")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Test string concatenation with parameters")
    @pytest.mark.parametrize(
        "first,second,expected",
        [
            ("Hello", "World", "HelloWorld"),
            ("Test", "Case", "TestCase"),
            ("", "Value", "Value"),
        ],
    )
    def test_string_concatenation(self, first, second, expected):
        """Test string concatenation with various inputs."""
        with allure.step(f"Concatenate '{first}' and '{second}'"):
            result = first + second

        with allure.step(f"Verify result is '{expected}'"):
            assert result == expected
