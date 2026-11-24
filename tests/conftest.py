# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import numpy as np
import pytest

from rigged.generator import Population


def make_population(x, y, group_b, tie_u=None):
    x = np.asarray(x, dtype=np.float64)
    n = x.shape[0]
    return Population(group_b=np.asarray(group_b, dtype=bool), q=x.copy(), y=np.asarray(y, dtype=bool), x=x,
                      tie_u=np.linspace(0.05, 0.95, n) if tie_u is None else np.asarray(tie_u, dtype=np.float64))


@pytest.fixture
def make_pop():
    return make_population
