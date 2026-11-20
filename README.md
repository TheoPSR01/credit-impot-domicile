# credit-impot-domicile

Calculer le crédit d'impôt pour l'emploi d'un salarié à domicile en France : ménage, garde d'enfants à domicile, aide aux personnes âgées, petit jardinage, bricolage, assistance informatique. L'outil applique les plafonds, les majorations et les sous-plafonds. Aucune dépendance.

## Installation

```bash
pip install git+https://github.com/TheoPSR01/credit-impot-domicile.git
```

Python 3.10 ou plus récent.

## En ligne de commande

Un couple dont les deux membres ont plus de 65 ans, 18 000 € d'aide à domicile dans l'année :

```bash
credit-impot-domicile 18000 --plus-65 2
```

```
Plafond de dépenses : 15 000,00 €
Dépenses retenues   : 15 000,00 € (plafond atteint)
Crédit d'impôt      : 7 500,00 €
```

```bash
credit-impot-domicile 6000 --enfants 2                 # garde d'enfants à domicile
credit-impot-domicile 3000 --jardinage 7000            # jardinage limité à 5 000 €
credit-impot-domicile 10000 --aides 3000 --apa 1       # aides déduites
credit-impot-domicile 16000 --premiere-annee --enfants 1
```

## En Python

```python
from credit_impot_domicile import credit_impot, plafond

plafond(enfants=2)                                   # Decimal('15000')
r = credit_impot(5000, jardinage=7000)
print(r.depenses_retenues, r.credit)                 # 10000 5000.00
```

## Règles appliquées

Crédit égal à 50 % des dépenses effectivement supportées, aides déduites, dans la limite d'un plafond annuel :

- 12 000 €, majorés de 1 500 € par enfant à charge (750 € en résidence alternée), par membre du foyer de plus de 65 ans et par ascendant de plus de 65 ans bénéficiaire de l'APA, sans dépasser 15 000 € ;
- 15 000 € la première année où l'on emploie directement un salarié, majorés de la même façon, sans dépasser 18 000 € ;
- 20 000 € si un membre du foyer est titulaire de la carte d'invalidité ou d'une pension d'invalidité de 3e catégorie.

Sous-plafonds compris dans le plafond général : 5 000 € pour le petit jardinage, 500 € pour le petit bricolage, 3 000 € pour l'assistance informatique.

## Limites

L'outil ne vérifie pas que les services sont éligibles ni que le prestataire est déclaré. Avec l'avance immédiate, une partie du crédit est déjà versée au moment du paiement : le calcul donne le montant total, pas le solde. Un amendement au projet de loi de finances pour 2027 propose de baisser le taux pour certains services ; si une réforme est votée, il faudra mettre à jour `TAUX`.

## Contribuer

```bash
git clone https://github.com/TheoPSR01/credit-impot-domicile.git
cd credit-impot-domicile
pip install -e ".[dev]"
pytest
```

## Licence

MIT
