from dataclasses import dataclass, field
from enum import Enum
from typing import List
import re

class Tile(Enum):
    #Pintas
    CHARACTERS1 = 'C1'
    CHARACTERS2 = 'C2'
    CHARACTERS3 = 'C3'
    CHARACTERS4 = 'C4'
    CHARACTERS5 = 'C5'
    CHARACTERS6 = 'C6'
    CHARACTERS7 = 'C7'
    CHARACTERS8 = 'C8'
    CHARACTERS9 = 'C9'
    BAMBOO1 = 'P1'
    BAMBOO2 = 'P2'
    BAMBOO3 = 'P3'
    BAMBOO4 = 'P4'
    BAMBOO5 = 'P5'
    BAMBOO6 = 'P6'
    BAMBOO7 = 'P7'
    BAMBOO8 = 'P8'
    BAMBOO9= 'P9'
    CIRCLES1 = 'B1'
    CIRCLES2 = 'B2'
    CIRCLES3 = 'B3'
    CIRCLES4 = 'B4'
    CIRCLES5 = 'B5'
    CIRCLES6 = 'B6'
    CIRCLES7 = 'B7'
    CIRCLES8 = 'B8'
    CIRCLES9 = 'B9'
    #Vientos
    EAST_WIND = 'E'
    SOUTH_WIND = 'S'
    WEST_WIND = 'W'
    NORTH_WIND = 'N'
    #Dragones
    RED_DRAGON = 'DR'
    GREEN_DRAGON  = 'DV'
    WHITE_DRAGON  = 'DB'

class Wind(Enum):
    EAST_WIND = 'E'
    SOUTH_WIND = 'S'
    WEST_WIND = 'W'
    NORTH_WIND = 'N'    

class Flower(Enum):
    RED1 = 'R1'
    RED2 = 'R2'
    RED3 = 'R3'
    RED4 = 'R4'
    BLACK1 = 'G1'
    BLACK2 = 'G2'
    BLACK3 = 'G3'
    BLACK4 = 'G4'

class Style(Enum):
    TRADICIONAL = 'TRADICIONAL'
    GRAN_SEGUIDILLA_REAL = 'GRAN SEGUIDILLA REAL'
    SIETE_SAMURAIS = '7 SAMURAIS'
    TRECE_MARAVILLAS = '13 MARAVILLAS'
    ASES_Y_NUEVES = 'ASES Y NUEVES'
    JASPE_VERDE = 'JASPE VERDE'
    HIJOS_DE_LA_NOCHE = 'HIJOS DE LA NOCHE'
    TIFON_ORIENTAL = 'TIFON ORIENTAL'
    ROSA_DE_LOS_VIENTOS = 'ROSA DE LOS VIENTOS'
    ARMONIA_CELESTE = 'ARMONIA CELESTE'
    JASPE_ROJO = 'JASPE ROJO'
    BENDICION_CELESTIAL = 'BENDICION CELESTIAL'
    GRAN_MURALLA_CHINA = 'GRAN MURALLA CHINA'
    CIUDAD_PROHIBIDA = 'CIUDAD PROHIBIDA'
    GRANDES_SAMURAIS = 'GRANDES SAMURAIS'
    LA_FLOR_DEL_CEREZO = 'LA FLOR DEL CEREZO'
    PESCANDO_LA_LUNA = 'PESCANDO LA LUNA DEL FONDO DEL MAR'

class GroupType(Enum):
    PUNG = 'Pung'
    KUNG = 'Kung'
    CHOW = 'Chow'
    EYE = 'Ojo'

#Honores
WINDS = {'E', 'S', 'W', 'N'}
DRAGONS = {'DR', 'DV', 'DB'}
MAJOR_HONORS = WINDS | DRAGONS  
MINOR_HONORS = {'C1', 'C9', 'P1', 'P9', 'B1', 'B9'}
HONOR_SCORING = MAJOR_HONORS | MINOR_HONORS
def is_major_honor(t: Tile) -> bool: return t.value in MAJOR_HONORS
def is_minor_honor(t: Tile) -> bool: return t.value in MINOR_HONORS
def is_honor_scoring(t: Tile) -> bool: return t.value in HONOR_SCORING

CLASSIC_BASE = {
    Style.GRAN_SEGUIDILLA_REAL: 2500,
    Style.SIETE_SAMURAIS: 2500,
    Style.TRECE_MARAVILLAS: 2500,
    Style.ASES_Y_NUEVES: 5000,
    Style.JASPE_VERDE: 5000,
    Style.HIJOS_DE_LA_NOCHE: 7500,
    Style.TIFON_ORIENTAL: 10000,
    Style.ROSA_DE_LOS_VIENTOS: 10000,
    Style.ARMONIA_CELESTE: 10000,
    Style.JASPE_ROJO: 15000,
    Style.BENDICION_CELESTIAL: 15000,
    Style.GRAN_MURALLA_CHINA: 15000,
    Style.CIUDAD_PROHIBIDA: 15000,
    Style.GRANDES_SAMURAIS: 20000,
    Style.LA_FLOR_DEL_CEREZO: 20000,
    Style.PESCANDO_LA_LUNA: 20000,
}

@dataclass
class Group:
    tiles: List[Tile]
    type: GroupType 
    isVisible: bool
    isHonor: bool

@dataclass
class GameBase:
    ID: int
    ownWind: Wind
    roundWind: Wind
    finalTile: Tile
    originalString: str
    baseScore: int = 0
    doubles: int = 0
    total: int = 0
    style: Style = Style.TRADICIONAL
    groups: List[Group] = field(default_factory=list)
    flowers: List[Flower] = field(default_factory=list)
    log: List[str] = field(default_factory=list)
    #Construccion de Juegos desde linea
    @classmethod
    def parse(cls, line: str) -> "GameBase": 
        inputPatron = r'^(\d+)\s+\[([ESWN])\s*/\s*([ESWN])\]\s+(.*?)\s+<(.*?)>\s+\*(.*?)\*$'
        match = re.match(inputPatron, line.strip())
        if not match:
            raise ValueError(f"Linea Invalida: {line}")
        ID_ = int(match.group(1))
        ownWind_ = Wind(match.group(2))
        roundWind_ = Wind(match.group(3))
        try:
            finalTile_ = Tile(match.group(6))
        except ValueError:
            raise ValueError(f"Pieza final invalida en: {line}")
        #Flores
        flowersRaw = match.group(5)
        flowers_ = [Flower(f) for f in flowersRaw.split()] if flowersRaw.strip() else []
        newGame = cls(
            ID = ID_,
            ownWind = ownWind_,
            roundWind = roundWind_,
            finalTile = finalTile_,
            originalString = line.strip(),
            flowers = flowers_
        )
        #Lectura y Clasificacion de Grupos
        groupsRaw = match.group(4)
        groupsPatron = r'(\[.*?\]|\{.*?\}|\(.*?\))'
        groupsMatch = re.findall(groupsPatron, groupsRaw)
        for groupRaw in groupsMatch:
            isVisible = True
            type = None
            if groupRaw.startswith('['):
                tilesRaw = groupRaw.strip('[]')
                isVisible = True
            elif groupRaw.startswith('{'):
                tilesRaw = groupRaw.strip('{}')
                isVisible = False
            elif groupRaw.startswith('('):
                tilesRaw = groupRaw.strip('()')
                isVisible = False
                type = GroupType.EYE
            else:
                raise ValueError(f"Delimitador desconocido: {line}")
            try:
                tilesList = [Tile(t) for t in tilesRaw.split('-')]
            except ValueError:
                raise ValueError(f"Ficha invalida en: {line}")
            if type == GroupType.EYE and len(tilesList) != 2: raise ValueError(f"Ojos deben ser par en: {line}")
            if type != GroupType.EYE:
                if len(tilesList) == 3:
                    type = GroupType.PUNG if tilesList[0] == tilesList[1] else GroupType.CHOW
                elif len(tilesList) == 4:
                    type = GroupType.KUNG
                else:
                    raise ValueError(f"Grupo invalido en: {line}")
            isHonor = all(is_honor_scoring(t) for t in tilesList)
            newGame.groups.append(Group(tiles=tilesList, type=type, isVisible=isVisible, isHonor=isHonor))
        return newGame