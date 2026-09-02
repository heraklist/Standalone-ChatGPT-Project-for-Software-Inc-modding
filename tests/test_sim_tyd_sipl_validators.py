from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/sim/tyd"


def test_validate_tyd_text_accepts_documented_list_and_hash_comment() -> None:
    from tools.validate_tyd_static import validate_tyd_text

    text = '# documented TyD comment\nItems ["A"; "B"]\nOptional True\n'
    assert validate_tyd_text(text) == []


def test_validate_tyd_text_does_not_reject_lowercase_boolean_as_parser_law() -> None:
    from tools.validate_tyd_static import validate_tyd_text

    assert validate_tyd_text("Optional true\n") == []


def test_validate_tyd_sipl_boundaries_flags_sipl_array_in_tyd_context() -> None:
    from tools.validate_sipl_boundaries import validate_tyd_sipl_boundaries

    errors = validate_tyd_sipl_boundaries("Items ~[\"A\", \"B\"]\n")
    assert any("SIPL array marker '~['" in error for error in errors)


def test_validate_tyd_sipl_boundaries_flags_sipl_comment_in_tyd_context() -> None:
    from tools.validate_sipl_boundaries import validate_tyd_sipl_boundaries

    errors = validate_tyd_sipl_boundaries("Value 1 // wrong parser comment\n")
    assert any("SIPL comment marker '//'" in error for error in errors)


def test_validate_tyd_sipl_boundaries_ignores_markers_inside_quoted_strings() -> None:
    from tools.validate_sipl_boundaries import validate_tyd_sipl_boundaries

    text = 'Script "var x = ~[1, 2]; // valid SIPL content inside TyD string"\n'
    assert validate_tyd_sipl_boundaries(text) == []


def test_validate_tyd_file_reads_valid_fixture() -> None:
    from tools.validate_tyd_static import validate_tyd_file

    assert validate_tyd_file(FIXTURES / "valid.tyd") == []


def test_validate_tyd_file_reports_broken_sipl_array_fixture() -> None:
    from tools.validate_tyd_static import validate_tyd_file

    errors = validate_tyd_file(FIXTURES / "broken-sipl-array.tyd")
    assert any("SIPL array marker '~['" in error for error in errors)


def test_validate_tyd_file_reports_broken_sipl_comment_fixture() -> None:
    from tools.validate_tyd_static import validate_tyd_file

    errors = validate_tyd_file(FIXTURES / "broken-sipl-comment.tyd")
    assert any("SIPL comment marker '//'" in error for error in errors)


def test_tyd_static_cli_returns_nonzero_for_invalid_fixture() -> None:
    from tools.validate_tyd_static import main

    assert main([str(FIXTURES / "broken-sipl-array.tyd")]) == 1
    assert main([str(FIXTURES / "valid.tyd")]) == 0
