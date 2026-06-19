"""CMC returns human-formatted number STRINGS; parse_cmc_number must normalise them."""
import math

from rotoredge.mcp_client import parse_cmc_number as p


def test_commas_and_dollar():
    assert p("67,728.08") == 67728.08
    assert p("$42,567.89") == 42567.89


def test_suffixes():
    assert abs(p("2.09 T") - 2.09e12) < 1.0
    assert abs(p("112.82 B") - 112.82e9) < 1.0
    assert abs(p("500K") - 500e3) < 1e-6
    assert abs(p("3.5 M") - 3.5e6) < 1e-6


def test_percent_divided_by_100():
    assert abs(p("-0.49242%") - (-0.0049242)) < 1e-12
    assert abs(p("5%") - 0.05) < 1e-12


def test_passthrough_and_empty():
    assert p(45) == 45.0
    assert p(3.14) == 3.14
    assert p(None) is None
    assert p("") is None
    assert p("15") == 15.0


if __name__ == "__main__":
    test_commas_and_dollar(); test_suffixes(); test_percent_divided_by_100(); test_passthrough_and_empty()
    print("test_parser: OK")
