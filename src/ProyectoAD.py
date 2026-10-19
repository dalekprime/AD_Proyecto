from mpi4py import MPI
from dataclasses import dataclass
from datetime import datetime

from models import *
from styleManager import styleManager
from scoreManager import scoreManager

class Game(GameBase, styleManager, scoreManager):
    #Calcular Puntuacion
    def calculateScore(self):
        self.style = self.detectStyle()
        if self.style in CLASSIC_BASE:
            self.baseScore = CLASSIC_BASE[self.style]
        else:
            self.calcBase()
        self.calcDoubles()
        raw = self.baseScore * (2 ** self.doubles)
        total = 5000 if (self.style == Style.TRADICIONAL and raw > 4500) else raw
        total = min(total, 20000)
        self.total = round(total / 100) * 100
        self.log.append(f"Total mano: {raw} para {self.total}")
    #Generar Salida
    def createOutput(self) -> str: 
        return f"{self.originalString} | {self.baseScore} | {self.doubles} | {self.total} | {self.style.value} | {self.log}"
#Distribucion
def main(): 
    return