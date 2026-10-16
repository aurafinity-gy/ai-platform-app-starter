from pathlib import Path


def test_domain_is_pure():
    src = (Path(__file__).parents[1] / "starter" / "domain.py").read_text()
    for forbidden in ("fastapi", "psycopg", "jwt", "requests", "httpx"):
        assert forbidden not in src


def test_application_has_no_infrastructure_imports():
    src = (Path(__file__).parents[1] / "starter" / "application.py").read_text()
    for forbidden in ("fastapi", "psycopg", "starter.persistence"):
        assert forbidden not in src


def test_forced_rls_and_no_bypass():
    sql = (Path(__file__).parents[3] / "migrations" / "001_init.sql").read_text()
    assert "FORCE ROW LEVEL SECURITY" in sql
    assert "NOBYPASSRLS" in sql
    assert "WITH CHECK" in sql
