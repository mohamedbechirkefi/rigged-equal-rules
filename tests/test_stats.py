# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import pytest

from rigged.stats import summarise


def test_summarise_golden():
    s = summarise([1.0, 2.0, 3.0, 4.0])
    assert s["mean"] == 2.5
    assert s["sd"] == pytest.approx(1.2909944487)
    half = 3.18244630528 * 1.2909944487 / 2  # t(0.975, 3) * sd / sqrt(4)
    assert s["t_lo"] == pytest.approx(2.5 - half, abs=1e-5) and s["t_hi"] == pytest.approx(2.5 + half, abs=1e-5)
    assert 1.0 <= s["boot_lo"] <= s["mean"] <= s["boot_hi"] <= 4.0
    assert s["standardised"] == pytest.approx(2.5 / 1.2909944487)


def test_summarise_is_deterministic_and_handles_missing():
    a, b = summarise([0.1, 0.4, None, 0.2]), summarise([0.1, 0.4, None, 0.2])
    assert a == b
    assert a["n_seeds"] == 3 and a["n_missing"] == 1


def test_summarise_degenerate():
    assert summarise([])["mean"] is None
    one = summarise([0.3])
    assert one["mean"] == 0.3 and one["sd"] is None and one["boot_lo"] is None
    const = summarise([0.25, 0.25, 0.25])  # exactly representable
    assert const["sd"] == 0.0 and const["standardised"] is None
    assert const["boot_lo"] == 0.25 and const["boot_hi"] == 0.25
