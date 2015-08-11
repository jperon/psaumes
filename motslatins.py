#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Module destiné à effectuer la césure des mots latins, suivant les règles
données sur marello.org :
This page employs the rules found in *A Primer on Ecclesiastical Latin*
by Collins. The rules are the following: Divisions occur when:

- After open vowels (those not followed by a consonant)
    (e.g., "pi-us" and "De-us")
- After vowels followed by a single consonant
    (e.g., "vi-ta" and "ho-ra")
- After the first consonant when two or more consonants follow a vowel
    (e.g., "mis-sa", "minis-ter", and "san-ctus").

Exceptions to syllable divisions:

- In compound words the consonants stay together (e.g., "de-scribo").
    Note: this particular exception is not currently implemented since
    it requires a dictionary list of compound words.
- A mute consonant (b, c, d, g, p, t) or f followed by a liquid consonant
    (l, r) go with the succeeding vowel: "la-crima", "pa-tris"

In addition to these rules, Wheelock's Latin provides this sound exception:

- Also counted as single consonants are qu and the aspirates ch, ph, th,
    which should never be separated in syllabification:
    architectus, ar-chi-tec-tus; loquacem, lo-qua-cem.
'''

import re
from sys import stdin, stdout, stderr


DEBUG = False

# Accents. Ne soyez pas surpris : á et á ne sont pas tout-à-fait identiques !
ACCENTS = re.compile('[áéíóúýǽ]|á|é|ı́|ó|ú|ý|ǽ|œ́]')

# Mots prédéfinis.
DICTIONNAIRE_MOTS = (
    'dé-scri-bo', 'de-scrí-be-re', 'de-scríp-ti-o',
    'id-íp-sum',
)


# Types de lettres.
CONSONNE_DOUBLE = (
    '(ch|ph|th|gn|qu' +
    '|bl|cl|dl|gl|pl|tl|fl' +
    '|br|cr|dr|gr|pr|tr|fr' +
    '|sc' +
    ')'
)
CONSONNE_SIMPE = '([bcdfgjklmnpqrstvwxz])'
DIPHTONGUE = '(æ|œ|ǽ|au|ou)'
I = '(i|y)'
VOYELLE = '(a|e|o|u|á|é|í|ó|ú|ý|ä|ë|ï|ü|ÿ)'

C = '(' + CONSONNE_DOUBLE + '|' + CONSONNE_SIMPE + ')'
V = '(' + DIPHTONGUE + '|' + VOYELLE + '|' + I + ')'


# Syllabes prédéfinies : placer les syllabes par ordre de priorité.
DICTIONNAIRE_SYLLABES = (
    'bli',
)


DICTIONNAIRE_MOTS = {
    mot.replace('-', ''): tuple(mot.split('-')) for mot in DICTIONNAIRE_MOTS
}
EXPRESSIONS_SYLLABES = tuple(
    re.compile(syllabe) for syllabe in DICTIONNAIRE_SYLLABES
)


def debug(message):
    '''Fonction affichant les messages d'erreur en mode debug'''
    if DEBUG:
        stderr.write(message + '\n')


def decouper(mot):
    '''Découpage d'un mot

    Le résultat est un tuple de syllabes.
    '''
    # Détection des mots déjà découpés
    if '-' in mot:
        return mot.split('-')
    # Recherche des mots prédéfinis
    if mot in DICTIONNAIRE_MOTS:
        return DICTIONNAIRE_MOTS[mot]
    # Recherche des syllabes prédéfinies
    for syllabe in EXPRESSIONS_SYLLABES:
        resultat = syllabe.search(mot)
        if resultat:
            print(syllabe)
            return decouper(mot[:resultat.start()]) + \
                (mot[resultat.start():resultat.end()],) + \
                decouper(mot[resultat.end():])
    # Recherche d'une syllabe finale terminée par une (ou des) consonne(s)
    resultat = re.search(
        C + '+' + V + '[^' + V + ']+$',
        mot,
        re.IGNORECASE
    )
    if resultat:
        debug('1\t' + mot[resultat.start():resultat.end()])
        if (
                re.match(C + C, mot[resultat.start():resultat.end()])
                and not re.match(
                    CONSONNE_DOUBLE,
                    mot[resultat.start():resultat.end()]
                )
        ):
            return decouper(mot[:resultat.start() + 1]) + \
                (mot[resultat.start() + 1:],)
        else:
            return decouper(mot[:resultat.start()]) + \
                (mot[resultat.start():],)
    # Coupure après la première de plusieurs consonnes.
    resultat = re.search(
        C + V + C + C,
        mot,
        re.IGNORECASE
    )
    if resultat:
        debug('2\t' + mot[resultat.start():resultat.end()])
        syl = mot[resultat.start():resultat.end()]
        try:
            idx = re.search(CONSONNE_DOUBLE + '$', syl).start()
        except AttributeError:
            idx = len(syl) - 1
        return decouper(mot[:resultat.start()]) + \
            (mot[resultat.start():resultat.start() + idx],) + \
            decouper(mot[resultat.start() + idx:])
    # Coupure après une voyelle.
    resultat = re.search(
        C + V,
        mot,
        re.IGNORECASE
    )
    if resultat:
        debug('3\t' + mot[resultat.start():resultat.end()])
        return decouper(mot[:resultat.start()]) + \
            (mot[resultat.start():resultat.end()],) + \
            decouper(mot[resultat.end():])
    return (mot,) if len(mot) else tuple()


def reperer_accent(mot):
    '''Repérage de l'accent d'un mot.

    Le mot en entrée est un tuple de syllabes, la sortie est l'indice de la
    syllabe accentuée dans ce tuple.
    Rappel : en python, on compte à partir de 0 !
    '''
    for idx, syllabe in enumerate(mot):
        if ACCENTS.search(syllabe):
            return idx
    if len(mot) < 3:
        return 0
    raise AccentAbsent


def traiter(phrase):
    '''Découpage de tous les mots d'une phrase

    Le résultat est un tuple de tuples.
    '''
    return (decouper(mot) for mot in re.split(r'\s', phrase))


class AccentAbsent(Exception):
    '''Un mot d'au moins trois syllabes n'est pas marqué d'un accent'''
    pass


if __name__ == '__main__':
    stdout.write(
        '\n'.join(
            ' '.join(
                '-'.join(mot) for mot in traiter(phrase) if len(mot)
            ) for phrase in stdin.readlines()
        )
    )
