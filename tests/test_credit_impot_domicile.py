from decimal import Decimal

import pytest

from credit_impot_domicile import credit_impot, main, plafond


@pytest.mark.parametrize("kwargs,attendu", [
    ({}, 12000),
    ({"enfants": 1}, 13500),
    ({"enfants_residence_alternee": 1}, 12750),
    ({"plus_de_65_ans": 2}, 15000),
    ({"enfants": 4}, 15000),                          # plafonné à 15 000 €
    ({"premiere_annee": True}, 15000),
    ({"premiere_annee": True, "enfants": 1}, 16500),
    ({"premiere_annee": True, "enfants": 3}, 18000),
    ({"invalidite": True, "enfants": 2}, 20000),
])
def test_plafond(kwargs, attendu):
    assert plafond(**kwargs) == Decimal(attendu)


def test_cas_simple():
    # 5 000 € d'aide à domicile : 2 500 € de crédit
    assert credit_impot(5000).credit == Decimal("2500.00")


def test_couple_de_plus_de_65_ans():
    # 18 000 € dépensés, plafond 12 000 + 2 × 1 500 = 15 000 € : 7 500 € de crédit
    r = credit_impot(18000, plus_de_65_ans=2)
    assert r.depenses_retenues == Decimal(15000)
    assert r.credit == Decimal("7500.00")
    assert r.plafond_atteint


def test_sous_plafonds():
    r = credit_impot(0, jardinage=7000, bricolage=800, informatique=1000)
    assert r.depenses_retenues == Decimal(6500)    # 5 000 + 500 + 1 000
    assert r.credit == Decimal("3250.00")


def test_aides_deduites():
    assert credit_impot(6000, aides=2000).credit == Decimal("2000.00")


def test_erreurs():
    with pytest.raises(ValueError):
        credit_impot(-1)
    with pytest.raises(ValueError):
        plafond(enfants=-1)


def test_cli(capsys):
    assert main(["18000", "--plus-65", "2"]) == 0
    out = capsys.readouterr().out
    assert "Crédit d'impôt      : 7 500,00 €" in out
    assert "plafond atteint" in out


def test_cli_aide():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
