"""Where the bundled fixtures live, and the demo case list.

``derepdx demo`` and the tests both drive the same list, so the quickstart and the test
suite can never disagree about what "runs" means.
"""

from __future__ import annotations

from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "data" / "fixtures"


def fixture(*parts: str) -> Path:
    p = FIXTURES.joinpath(*parts)
    if not p.exists():
        raise FileNotFoundError(f"bundled fixture missing: {p}")
    return p


# (Table 3 row, kind, callable returning a CheckResult using only bundled fixtures)
def cases():
    from . import io
    from .checks import background, concordance, counts, length, polarity, profile, qc_covariate
    from .lint import denominators, matrix_id

    return [
        (1, "neg", lambda: length.run(io.read_table(
            fixture("length", "neg_same_strain_within_tol.tsv"),
            ["accession", "strain", "total_bp"]))),
        (1, "pos", lambda: length.run(io.read_table(
            fixture("length", "pos_same_strain_107kb.tsv"),
            ["accession", "strain", "total_bp"]))),
        (2, "neg", lambda: denominators.run(io.read_json(fixture("lint", "neg_denominators.json")))),
        (2, "pos", lambda: denominators.run(io.read_json(fixture("lint", "pos_denominators.json")))),
        (3, "neg", lambda: concordance.run(
            io.read_matrix(fixture("concordance", "dist_8x8.tsv")),
            io.read_table(fixture("concordance", "neg_concordant.tsv"),
                          ["accession", "chromosome_blocks"]), t=20)),
        (3, "pos", lambda: concordance.run(
            io.read_matrix(fixture("concordance", "dist_8x8.tsv")),
            io.read_table(fixture("concordance", "pos_discordant_at_t20.tsv"),
                          ["accession", "chromosome_blocks"]), t=20)),
        (4, "neg", lambda: profile.run(io.read_table(
            fixture("profile", "neg_three_state.tsv"), ["accession", "replicon", "state"]))),
        (4, "pos", lambda: profile.run(io.read_table(
            fixture("profile", "pos_two_state.tsv"), ["accession", "replicon", "state"]))),
        (5, "neg", lambda: polarity.run(io.read_table(
            fixture("polarity", "neg_derived_loss.tsv"),
            ["outgroup", "callable_fraction", "present"]))),
        (5, "pos", lambda: polarity.run(io.read_table(
            fixture("polarity", "pos_lineage_gain.tsv"),
            ["outgroup", "callable_fraction", "present"]))),
        (6, "neg", lambda: background.run(io.read_table(
            fixture("background", "neg_outside_background.tsv"),
            ["region", "value", "background_p95", "claimed_special"]))),
        (6, "pos", lambda: background.run(io.read_table(
            fixture("background", "pos_inside_background.tsv"),
            ["region", "value", "background_p95", "claimed_special"]))),
        (7, "neg", lambda: matrix_id.run(io.read_json(fixture("lint", "neg_matrix_id.json")))),
        (7, "pos", lambda: matrix_id.run(io.read_json(fixture("lint", "pos_matrix_id.json")))),
        (8, "neg", lambda: qc_covariate.run(io.read_table(
            fixture("qc", "neg_metric_independent.tsv"),
            ["accession", "metric", "distance"]))),
        (8, "pos", lambda: qc_covariate.run(io.read_table(
            fixture("qc", "pos_metric_tracks_distance.tsv"),
            ["accession", "metric", "distance"]))),
        (9, "neg", lambda: counts.run(io.read_json(fixture("counts", "neg_206_of_206.json")))),
        (9, "pos", lambda: counts.run(io.read_json(fixture("counts", "pos_28_of_206.json")))),
    ]


def ambiguous_cases():
    """The polarity AMBIGUOUS third state, which is neither pos nor neg."""
    from . import io
    from .checks import polarity
    return [
        lambda: polarity.run(io.read_table(
            fixture("polarity", "amb_undetermined.tsv"),
            ["outgroup", "callable_fraction", "present"])),
    ]
