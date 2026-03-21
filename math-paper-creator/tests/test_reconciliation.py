import pytest
from meta_compiler.compiler.parser import ProseBlock
from meta_compiler.checks import check_directional_claims


class TestCheckDirectionalClaims:
    def test_flags_increases(self):
        blocks = [ProseBlock(content="The σ parameter increases the outside option.\n")]
        warnings = check_directional_claims(blocks)
        assert len(warnings) == 1
        assert "increases" in warnings[0].lower()

    def test_flags_multiple_keywords(self):
        blocks = [ProseBlock(content="As x increases, y decreases and is monotone.\n")]
        warnings = check_directional_claims(blocks)
        # Should flag "increases", "decreases", and "monotone"
        assert len(warnings) == 3

    def test_no_warnings_for_clean_prose(self):
        blocks = [ProseBlock(content="The model defines a set of workers.\n")]
        warnings = check_directional_claims(blocks)
        assert warnings == []

    def test_ignores_non_prose_blocks(self):
        """Only ProseBlock content is scanned."""
        from meta_compiler.compiler.parser import ValidationBlock
        blocks = [ValidationBlock(code="# value increases here", line_number=1)]
        warnings = check_directional_claims(blocks)
        assert warnings == []
