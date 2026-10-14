"""derepdx -- diagnostics for SNP-distance dereplication blind to structural variation.

Every function in this package takes tables in and returns a verdict out. The
package deliberately never reads BAM/VCF/FASTA: that keeps it ``pip install``-able,
keeps the test fixtures small enough to live in git, and keeps it independent of the
multi-hundred-gigabyte intermediate files of the source study.

See ``docs/table3_mapping.md`` for the mapping between the nine diagnostics of the
companion manuscript and the commands implemented here.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
