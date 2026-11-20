"""credit_impot_domicile : crédit d'impôt pour l'emploi d'un salarié à domicile.

Crédit = 50 % des dépenses supportées (aides déduites), retenues dans la
limite d'un plafond annuel (article 199 sexdecies du CGI) :

- 12 000 €, majorés de 1 500 € par enfant à charge (750 € en résidence
  alternée), par membre du foyer de plus de 65 ans et par ascendant de plus
  de 65 ans bénéficiaire de l'APA, sans dépasser 15 000 € ;
- 15 000 € (au plus 18 000 € avec les majorations) la première année où l'on
  emploie directement un salarié à domicile ;
- 20 000 € si un membre du foyer est titulaire de la carte d'invalidité (ou CMI
  invalidité) ou d'une pension d'invalidité de 3e catégorie.

Sous-plafonds compris dans le plafond général : petit jardinage 5 000 €,
petit bricolage 500 €, assistance informatique 3 000 €.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Union

__version__ = "0.1.0"

Montant = Union[int, float, str, Decimal]
D = Decimal
TAUX = D("0.5")
SOUS_PLAFONDS = {"jardinage": D(5000), "bricolage": D(500), "informatique": D(3000)}


def _d(x: Montant) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x).replace(",", ".").replace(" ", ""))


def plafond(enfants: int = 0, enfants_residence_alternee: int = 0, plus_de_65_ans: int = 0,
            ascendants_apa: int = 0, premiere_annee: bool = False, invalidite: bool = False) -> Decimal:
    """Plafond annuel des dépenses retenues."""
    if min(enfants, enfants_residence_alternee, plus_de_65_ans, ascendants_apa) < 0:
        raise ValueError("les nombres de personnes doivent être positifs")
    if invalidite:
        return D(20000)
    base, maximum = (D(15000), D(18000)) if premiere_annee else (D(12000), D(15000))
    majoration = D(1500) * (enfants + plus_de_65_ans + ascendants_apa) + D(750) * enfants_residence_alternee
    return min(base + majoration, maximum)


@dataclass(frozen=True)
class Resultat:
    depenses_retenues: Decimal
    plafond: Decimal
    credit: Decimal
    plafond_atteint: bool


def credit_impot(depenses: Montant, jardinage: Montant = 0, bricolage: Montant = 0, informatique: Montant = 0,
                 aides: Montant = 0, **situation) -> Resultat:
    """Montant du crédit d'impôt.

    ``depenses`` : services sans sous-plafond (ménage, garde d'enfants, aide à domicile...) ;
    ``jardinage``, ``bricolage``, ``informatique`` : dépenses soumises à un sous-plafond ;
    ``aides`` : aides reçues pour ces services (APA, PCH, aides de la CAF...), à déduire ;
    ``situation`` : paramètres de :func:`plafond`.
    """
    montants = {"jardinage": _d(jardinage), "bricolage": _d(bricolage), "informatique": _d(informatique)}
    general, aides_ = _d(depenses), _d(aides)
    if general < 0 or aides_ < 0 or any(v < 0 for v in montants.values()):
        raise ValueError("les montants doivent être positifs")
    total = general + sum(min(v, SOUS_PLAFONDS[k]) for k, v in montants.items())
    total = max(total - aides_, D(0))
    p = plafond(**situation)
    retenues = min(total, p)
    credit = (retenues * TAUX).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    return Resultat(retenues, p, credit, total > p)


def _fr(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="credit-impot-domicile", description="Crédit d'impôt pour l'emploi d'un salarié à domicile.")
    p.add_argument("--version", action="version", version=f"credit-impot-domicile {__version__}")
    p.add_argument("depenses", help="dépenses de l'année (ménage, garde d'enfants, aide à domicile...)")
    p.add_argument("--jardinage", default="0")
    p.add_argument("--bricolage", default="0")
    p.add_argument("--informatique", default="0")
    p.add_argument("--aides", default="0", help="aides reçues pour ces services (APA, CAF...)")
    p.add_argument("--enfants", type=int, default=0, help="enfants à charge")
    p.add_argument("--alternee", type=int, default=0, help="enfants en résidence alternée")
    p.add_argument("--plus-65", type=int, default=0, help="membres du foyer de plus de 65 ans")
    p.add_argument("--apa", type=int, default=0, help="ascendants de plus de 65 ans bénéficiaires de l'APA")
    p.add_argument("--premiere-annee", action="store_true", help="première année d'emploi direct")
    p.add_argument("--invalidite", action="store_true", help="membre du foyer invalide (plafond de 20 000 €)")
    a = p.parse_args(argv)
    try:
        r = credit_impot(a.depenses, a.jardinage, a.bricolage, a.informatique, a.aides,
                         enfants=a.enfants, enfants_residence_alternee=a.alternee, plus_de_65_ans=a.plus_65,
                         ascendants_apa=a.apa, premiere_annee=a.premiere_annee, invalidite=a.invalidite)
    except (ValueError, InvalidOperation) as exc:
        print(f"credit-impot-domicile : {exc}", file=sys.stderr)
        return 2
    print(f"Plafond de dépenses : {_fr(r.plafond)} €")
    print(f"Dépenses retenues   : {_fr(r.depenses_retenues)} €" + (" (plafond atteint)" if r.plafond_atteint else ""))
    print(f"Crédit d'impôt      : {_fr(r.credit)} €")
    return 0


__all__ = ["Resultat", "SOUS_PLAFONDS", "TAUX", "credit_impot", "main", "plafond"]
