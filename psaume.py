#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Module destiné à préparer des psaumes pour inclusion dans des documents LaTeX
avec le package gredoc.sty.
'''

import motslatins as m
from sys import stdin, stdout
from re import match


class Syllabe:
    def __init__(self, txt, accent=False, precedente=None):
        self.txt = txt
        self.precedente = precedente
        self.accent = accent

    def __str__(self):
        return self.txt

    def encadrer(self, avant, apres):
        self.txt = avant + self.txt + apres


class Mot:
    def __init__(self, txt, precedent=None):
        self.txt = txt
        self.precedent = precedent
        self.syllabes = self.decouper()

    def __str__(self):
        if len(self.syllabes):
            return ''.join(str(syl) for syl in self.syllabes)
        else:
            return self.txt

    def decouper(self):
        if len(self.txt) == 1 and not match(m.V, self.txt):
            return []
        syllabes = []
        decoupe = m.decouper(self.txt)
        accent = m.reperer_accent(decoupe)
        for idx, txt in enumerate(decoupe):
            syllabes.append(
                Syllabe(
                    txt, idx == accent,
                    precedente = \
                        syllabes[-1] if len(syllabes) \
                        else self.precedent[-1] if self.precedent \
                        else None
                    )
                )
        return syllabes


class Signe:
    def __init__(self, txt):
        self.txt = txt

    def __str__(self):
        return self.txt


class Phrase:
    def __init__(self, txt):
        self.txt = txt
        self.mots = self.decouper()
        self.syllabes = self.decouper_syllabes()

    def __str__(self):
        return ' '.join(str(mot) for mot in self.mots)

    def decouper(self):
        return [Mot(txt) for txt in self.txt.split(' ')]

    def decouper_syllabes(self):
        syllabes = []
        for mot in self.mots:
            syllabes += mot.syllabes
        return syllabes

    @property
    def accent_dernier(self):
        syllabes = self.syllabes
        if syllabes[-2].accent:
            return -2
        elif syllabes[-3].accent:
            return -3
        else:
            return -2

    @property
    def accent_penultieme(self):
        syllabes = self.syllabes
        dernier = self.accent_dernier
        if syllabes[dernier - 2].accent:
            return dernier - 2
        elif syllabes[dernier - 3].accent:
            return dernier - 3
        else:
            return dernier - 2


if __name__ == '__main__':
    for verset in stdin.readlines():
        hemisticheI, hemisticheII = verset.split('*')
        hemisticheI = Phrase(hemisticheI)
        hemisticheII = Phrase(hemisticheII)
        aca = hemisticheII.accent_dernier
        acb = hemisticheII.accent_penultieme
        acc = hemisticheI.accent_dernier
        acd = hemisticheI.accent_penultieme
        hemisticheII.syllabes[aca].encadrer('\\aca{','}')
        hemisticheII.syllabes[aca - 1].encadrer('\\praa{','}')
        hemisticheII.syllabes[aca - 2].encadrer('\\prab{','}')
        hemisticheII.syllabes[aca - 3].encadrer('\\prac{','}')
        if aca == -3:
            hemisticheII.syllabes[aca + 1].encadrer('\\saca{','}')
        hemisticheII.syllabes[acb].encadrer('\\acb{','}')
        hemisticheII.syllabes[acb - 1].encadrer('\\prba{','}')
        hemisticheI.syllabes[acc].encadrer('\\acc{','}')
        hemisticheI.syllabes[acc - 1].encadrer('\\prca{','}')
        hemisticheI.syllabes[acc - 2].encadrer('\\prcb{','}')
        hemisticheI.syllabes[acc - 3].encadrer('\\prcc{','}')
        if acc == -3:
            hemisticheI.syllabes[acc + 1].encadrer('\\sacc{','}')
        hemisticheI.syllabes[acd].encadrer('\\acd{','}')
        hemisticheI.syllabes[acd - 1].encadrer('\\prda{','}')
        #print(hemisticheI.txt, hemisticheII.txt)
        #print(tuple((syl.txt) for syl in hemisticheI.syllabes), tuple((syl.txt) for syl in hemisticheII.syllabes))
        stdout.write('\\versus{' + str(hemisticheI)[:-1] + '~\*' + str(hemisticheII).replace('\n','}\n'))
