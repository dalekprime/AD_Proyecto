from mpi4py import MPI
from datetime import datetime
import time
import math

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
def worker(chunk: list) -> list:
    result = []
    for line in chunk:
        if not line.strip():
            continue
        try:
            game = Game.parse(line)
            game.calculateScore()
            result.append((game.ID, game.createOutput()))
        except Exception as e:
            result.append((-1, f"Error en {line.strip()}: {str(e)}"))
    return result
def main(): 
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    startTime = 0
    startDT = None
    chunks = None
    if rank == 0:
        startTime = time.time()
        startDT = datetime.now()
        try:
            with open('../input.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print("No se encontro el archivo de Entrada")
            comm.Abort(1)
        if not lines:
            print("Input.txt esta vacio")
            comm.Abort(1)
        chunkSize = math.ceil(len(lines) / size)
        chunks = [lines[i:i + chunkSize] for i in range(0, len(lines), chunkSize)]
        while len(chunks) < size:
            chunks.append([])
    #Distribuir Carga entre los nodos Workers
    localLines = comm.scatter(chunks, root=0)
    localResults = worker(localLines)
    allResults = comm.gather(localResults, root=0)
    #Recoleccion de Datos
    if rank == 0:
        resultsRaw = [item for sublist in allResults for item in sublist]
        fails = [item for item in resultsRaw if item[0] == -1]
        goods = [item for item in resultsRaw if item[0] != -1]
        goods.sort(key=lambda x: x[0])
        endTime = time.time()
        endDT = datetime.now()
        timeElapsed = endTime - startTime
        with open('../output.txt', 'w', encoding='utf-8') as f:
            for _, outputLine in goods:
                f.write(outputLine + '\n')
            f.write('\n')
            f.write(f"{startDT.strftime('%Y-%m-%d %H:%M:%S')} | {endDT.strftime('%Y-%m-%d %H:%M:%S')} | {timeElapsed:.4f}\n")
        if fails:
            print(f"Se omitieron {len(fails)} lineas corruptas")
        else:
            print(f"Ejecucion exitosa. Tiempo invertido: {timeElapsed:.4f}s")

if __name__ == '__main__':
    main()