"""Report-side linters (Table 3 rows 2 and 7).

These two do not look at biological data; they lint the *reporting* convention. They only
mean something once a study writes its numbers into a claims file, which is why they are
prefixed ``lint-`` rather than ``check-`` and why they are the first things to drop when
time is short.
"""

from . import denominators, matrix_id

__all__ = ["denominators", "matrix_id"]
