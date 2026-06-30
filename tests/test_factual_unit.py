"""Unit tests for factual extraction and validation helpers."""

import pytest

from factual import extract_account_type, extract_amount, validate_factual


class TestExtractAmount:
    def test_standard_format(self):
        assert extract_amount("Your balance is $1,847.32.") == "$1,847.32"

    def test_no_amount_returns_none(self):
        assert extract_amount("No money here") is None


class TestExtractAccountType:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("checking account balance", "checking"),
            ("savings account", "savings"),
            ("term deposit balance", "term deposit"),
            ("your account", None),
        ],
    )
    def test_account_types(self, text, expected):
        assert extract_account_type(text) == expected


class TestValidateFactualKnownCases:
    REF = "Your checking account balance is $1,847.32."

    @pytest.mark.parametrize(
        "candidate,should_pass",
        [
            ("Your checking account balance is $1,847.32.", True),
            ("The balance in your checking account is $1,800.32.", False),
            ("Your savings account balance is $1,847.32.", False),
            ("You have $1,847.32 in your checking account.", True),
            ("You have $1,847.32 in your account.", False),
        ],
        ids=["exact", "wrong_amount", "wrong_account", "paraphrase_ok", "incomplete"],
    )
    def test_checking_balance_week1_cases(self, candidate, should_pass):
        result = validate_factual(self.REF, candidate)
        assert result["pass"] is should_pass
