from mpi4py import MPI
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set
import re
import time
import math

#Palos verdes para Jaspe Verde
GREEN_TILES: Set[str] = {'P2', 'P3', 'P4', 'P6', 'P8', 'DV'}

#Palos rojos para Jaspe Rojo
RED_TILES: Set[str] = {'P1', 'P5', 'P7', 'P9', 'DR'}

#Chinos impares para Gran Muralla China
ODD_CHINOS: Set[str] = {'C1', 'C3', 'C5', 'C7', 'C9'}

#Chinos pares para Ciudad Prohibida
EVEN_CHINOS: Set[str] = {'C2', 'C4', 'C6', 'C8'}

#Mapeo de flor propia según el viento propio
OWN_FLOWER_MAP = {
    'E': {'R1', 'G1'},
    'S': {'R2', 'G2'},
    'W': {'R3', 'G3'},
    'N': {'R4', 'G4'},
}

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
    MARAVILLAS = 'Maravillas'

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
                    # Si las dos primeras son iguales es Pung, si no, es Chow
                    type = GroupType.PUNG if tilesList[0] == tilesList[1] else GroupType.CHOW
                elif len(tilesList) == 4:
                    type = GroupType.KUNG
                elif len(tilesList) == 14:
                    # Caso especial para 13 MARAVILLAS
                    type = GroupType.MARAVILLAS
                else:
                    raise ValueError(f"Grupo invalido en: {line}")
            isHonor = all(is_honor_scoring(t) for t in tilesList)
            newGame.groups.append(Group(tiles=tilesList, type=type, isVisible=isVisible, isHonor=isHonor))
        return newGame

class scoreManager:
    def calcBase(self): 
        score = 0
        for flor in self.flowers:
            score += 4
        hayChow = False
        dragones = set()
        
        for g in self.groups:
            subscore = 0
            tp = g.type
            ab = g.isVisible
            hn = g.isHonor
            
            if tp == GroupType.KUNG:
                subscore = 8
            elif tp == GroupType.PUNG:
                subscore = 2
            elif tp == GroupType.EYE:
                value = g.tiles[0].value
                if value == 'DR': 
                    subscore = 4
            elif tp == GroupType.MARAVILLAS:
                continue
            else:
                hayChow = True
                continue 
                
            # Multiplicadores por cerrado
            if ab == False:
                subscore *= 2
                
            # Multiplicadores por honor
            if hn == True:
                subscore *= 2
                
            score += subscore
        
        # Mahjong con chow o puro pung
        if hayChow:
            score += 20
        else:
            score += 30
        
        self.baseScore = round(score / 10) * 10
    def calcDoubles(self): 
        doubles = 0
        rojas = 0
        negras = 0
        for flor in self.flowers:
            if flor.value.startswith('R'): rojas += 1
            if flor.value.startswith('G'): negras += 1
            
        tiene_ramillete_rojo = (rojas == 4)
        tiene_ramillete_negro = (negras == 4)
        
        if tiene_ramillete_rojo:
            doubles += 4
            self.log.append("Ramillete Rojo: +4 dobles")
        if tiene_ramillete_negro:
            doubles += 4
            self.log.append("Ramillete Negro: +4 dobles")
        
        flor_propia_roja = ""
        flor_propia_negra = ""
        viento = getattr(self, 'ownWind', '').value
        if viento == 'E': flor_propia_roja, flor_propia_negra = 'R1', 'G1'
        elif viento == 'S': flor_propia_roja, flor_propia_negra = 'R2', 'G2'
        elif viento == 'W': flor_propia_roja, flor_propia_negra = 'R3', 'G3'
        elif viento == 'N': flor_propia_roja, flor_propia_negra = 'R4', 'G4'

        for flor in self.flowers:
            if flor.value == flor_propia_roja and not tiene_ramillete_rojo:
                doubles += 1
                self.log.append(f"Flor Propia ({flor.value}): +1 doble")
            elif flor.value == flor_propia_negra and not tiene_ramillete_negro:
                doubles += 1
                self.log.append(f"Flor Propia ({flor.value}): +1 doble")
        
        pungs_dragones = 0
        ojos_dragon = 0
        
        for g in self.groups:
            ficha = g.tiles[0].value
            
            if g.type in (GroupType.PUNG, GroupType.KUNG):
                if ficha == viento:
                    doubles += 1
                    self.log.append(f"Viento Propio ({ficha}): +1 doble")
                if ficha == getattr(self, 'roundWind', '').value:
                    doubles += 1
                    self.log.append(f"Viento Predominante ({ficha}): +1 doble")
                
                if ficha in ['DR', 'DV', 'DB']:
                    pungs_dragones += 1
                    doubles += 1
                    self.log.append(f"Dragón ({ficha}): +1 doble")
                    
            elif g.type == GroupType.EYE:
                if ficha in ['DR', 'DV', 'DB']:
                    ojos_dragon += 1
        
        if pungs_dragones == 3:
            doubles += 4
            self.log.append("Escolares Mayores: +4 dobles")
        elif pungs_dragones == 2 and ojos_dragon == 1:
            doubles += 3
            self.log.append("Escolares Menores: +3 dobles")
        
        # --- LÓGICA DE PINTAS Y HONORES ---
        pintas = set()
        tiene_letras = False
        cant_chows = 0
        cant_pungs = 0
        todas_las_fichas = []
        
        for g in self.groups:
            for t in g.tiles:
                todas_las_fichas.append(t.value)
                if t.value in ['E', 'S', 'W', 'N', 'DR', 'DV', 'DB']:
                    tiene_letras = True
                else:
                    pintas.add(t.value[0])
            
            if g.type == GroupType.CHOW:
                cant_chows += 1
            elif g.type in (GroupType.PUNG, GroupType.KUNG):
                cant_pungs += 1

        if len(pintas) == 1:
            pinta_actual = list(pintas)[0]
            
            if not tiene_letras:
                # Limpio puro (sin honores)
                if cant_chows == 0:
                    doubles += 5
                    self.log.append("Limpio (Pungs de pinta): +5 dobles")
                elif cant_pungs == 0:
                    doubles += 4
                    self.log.append("Limpio (Puros Chows): +4 dobles")
                else:
                    doubles += 3
                    self.log.append("Limpio (Pungs y Chows): +3 dobles")
            else:
                # Tiene honores: Revisar si tiene el 1 y el 9 de la pinta
                tiene_1 = f"{pinta_actual}1" in todas_las_fichas
                tiene_9 = f"{pinta_actual}9" in todas_las_fichas
                
                if tiene_1 and tiene_9:
                    doubles += 3
                    self.log.append("Limpio (Honores con Ases y Nueves): +3 dobles")
                else:
                    doubles += 2
                    self.log.append("Sucio (Honores con pinta): +2 dobles")
        else:
            # Fallback por si hay más de una pinta
            if cant_chows == 0:
                doubles += 2
                self.log.append("Sucio (Pinta sin chow): +2 dobles")
            else:
                doubles += 1
                self.log.append("Sucio (Pinta con chow): +1 doble")

        self.doubles = doubles   



class styleManager:
    #Detecta el estilo de mano tradicional.
    def detectStyle(self, game=None) -> Style:

        #Retorna el Style correspondiente o Style.TRADICIONAL si no califica.
        target = game if game is not None else self

        groups = getattr(target, 'groups', [])
        if not groups:
            return Style.TRADICIONAL

        final_tile = getattr(target, 'finalTile', None)
        final_tile_val = (
            final_tile.value if hasattr(final_tile, 'value') else str(final_tile) if final_tile else ''
        )

        own_wind = getattr(target, 'ownWind', None)
        own_wind_val = (
            own_wind.value if hasattr(own_wind, 'value') else str(own_wind) if own_wind else ''
        )

        round_wind = getattr(target, 'roundWind', None)
        round_wind_val = (
            round_wind.value if hasattr(round_wind, 'value') else str(round_wind) if round_wind else ''
        )

        flowers = getattr(target, 'flowers', [])
        flower_vals = [f.value if hasattr(f, 'value') else str(f) for f in flowers]

        #Agrupa las 4 combinaciones principales
        melds = [g for g in groups if g.type != GroupType.EYE]

        #Agrupa los ojos
        eyes = [g for g in groups if g.type == GroupType.EYE]

        #Jugadas de 20.000 puntos
        if self._is_grandes_samurais(groups):
            return Style.GRANDES_SAMURAIS

        if self._is_flor_del_cerezo(final_tile_val, own_wind_val, flower_vals, groups):
            return Style.LA_FLOR_DEL_CEREZO

        #Jugadas de 15.000 puntos
        if self._is_jaspe_rojo(melds, eyes):
            return Style.JASPE_ROJO

        if self._is_bendicion_celestial(melds, eyes, own_wind_val, round_wind_val):
            return Style.BENDICION_CELESTIAL

        if self._is_gran_muralla_china(melds, eyes):
            return Style.GRAN_MURALLA_CHINA

        if self._is_ciudad_prohibida(melds, eyes):
            return Style.CIUDAD_PROHIBIDA

        #Jugadas de 10.000 puntos
        if self._is_tifon_oriental(melds, eyes):
            return Style.TIFON_ORIENTAL

        if self._is_rosa_de_los_vientos(melds, eyes):
            return Style.ROSA_DE_LOS_VIENTOS

        if self._is_armonia_celeste(melds, eyes, own_wind_val, round_wind_val):
            return Style.ARMONIA_CELESTE

        #Jugadas de 7.500 puntos
        if self._is_hijos_de_la_noche(groups):
            return Style.HIJOS_DE_LA_NOCHE

        #Jugadas de 5.000 puntos
        if self._is_ases_y_nueves(melds, eyes):
            return Style.ASES_Y_NUEVES

        if self._is_jaspe_verde(melds, eyes):
            return Style.JASPE_VERDE

        #Jugadas de 2.500 puntos
        if self._is_gran_seguidilla_real(melds, eyes, own_wind_val, round_wind_val):
            return Style.GRAN_SEGUIDILLA_REAL

        if self._is_siete_samurais(groups):
            return Style.SIETE_SAMURAIS

        if self._is_trece_maravillas(groups):
            return Style.TRECE_MARAVILLAS

        return Style.TRADICIONAL

    #Validaciones individuales
    def _is_grandes_samurais(self, groups) -> bool:

        #GRANDES SAMURAIS: 7 pares de vientos y dragones, se pueden repetir.
        if len(groups) != 7:
            return False
        for g in groups:
            if len(g.tiles) != 2 or g.tiles[0].value != g.tiles[1].value:
                return False
            if g.tiles[0].value not in MAJOR_HONORS:
                return False
        return True

    def _is_flor_del_cerezo(
        self, final_tile_val: str, own_wind_val: str, flower_vals: List[str], groups
    ) -> bool:
        #LA FLOR DEL CEREZO: Mahjong limpio de Ruedas (B) con B5 al final y flor propia.
        if final_tile_val != 'B5':
            return False
        own_flowers = OWN_FLOWER_MAP.get(own_wind_val, set())
        if not any(f in own_flowers for f in flower_vals):
            return False
        # Verificar que TODA la mano esté compuesta exclusivamente por Ruedas (B)
        all_tiles = [t.value for g in groups for t in g.tiles]
        return all(t.startswith('B') for t in all_tiles)

    def _is_jaspe_rojo(self, melds, eyes) -> bool:
        #JASPE ROJO: Pungs y Ojos formados únicamente por palos rojos (P1, P5, P7, P9) y dragón rojo (DR).
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        all_tiles = [t.value for g in melds + eyes for t in g.tiles]
        return all(t in RED_TILES for t in all_tiles)

    def _is_bendicion_celestial(self, melds, eyes, own_wind_val: str, round_wind_val: str) -> bool:
        #BENDICIÓN CELESTIAL: Pungs de 2, 4 y 8 de ruedas (B2, B4, B8), pung de dragón blanco (DB) y ojos del viento propio o predominante.
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        meld_vals = {m.tiles[0].value for m in melds}
        if meld_vals != {'B2', 'B4', 'B8', 'DB'}:
            return False
        eye_val = eyes[0].tiles[0].value
        return eye_val in {own_wind_val, round_wind_val}

    def _is_gran_muralla_china(self, melds, eyes) -> bool:
        #GRAN MURALLA CHINA: Pungs/Kongs de Chinos impares
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type in (GroupType.PUNG, GroupType.KUNG) for m in melds):
            return False
        all_tiles = [t.value for g in melds + eyes for t in g.tiles]
        if not all(t in ODD_CHINOS for t in all_tiles):
            return False
        return set(all_tiles) == ODD_CHINOS

    def _is_ciudad_prohibida(self, melds, eyes) -> bool:
        #CIUDAD PROHIBIDA: Pungs/Kongs de Chinos pares y dragón rojo (DR) como ojos o como pung.
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type in (GroupType.PUNG, GroupType.KUNG) for m in melds):
            return False
        all_tiles = [t.value for g in melds + eyes for t in g.tiles]
        allowed = EVEN_CHINOS | {'DR'}
        if not all(t in allowed for t in all_tiles):
            return False
        return set(all_tiles) == allowed

    def _is_tifon_oriental(self, melds, eyes) -> bool:
        #TIFÓN ORIENTAL: 3 Pungs de vientos distintos, 1 pung de dragón (DR, DV o DB) y ojos (pares del viento restante).
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        wind_melds = [m.tiles[0].value for m in melds if m.tiles[0].value in WINDS]
        dragon_melds = [m.tiles[0].value for m in melds if m.tiles[0].value in DRAGONS]
        if len(set(wind_melds)) != 3 or len(dragon_melds) != 1:
            return False
        eye_val = eyes[0].tiles[0].value
        return eye_val in WINDS and eye_val not in wind_melds

    def _is_rosa_de_los_vientos(self, melds, eyes) -> bool:
        #ROSA DE LOS VIENTOS: 4 Pungs de los cuatro vientos (E, S, W, N) y ojos de cualquier ficha.
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        meld_tiles = {m.tiles[0].value for m in melds}
        return meld_tiles == WINDS

    def _is_armonia_celeste(
        self, melds, eyes, own_wind_val: str, round_wind_val: str
    ) -> bool:
        #ARMONÍA CELESTE: Pungs de los tres dragones (DB, DV, DR), pung del viento propio o predominante, y ojos de cualquier honor (mayor o menor).
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        dragon_melds = {m.tiles[0].value for m in melds if m.tiles[0].value in DRAGONS}
        if dragon_melds != DRAGONS:
            return False
        wind_melds = [m.tiles[0].value for m in melds if m.tiles[0].value in WINDS]
        if len(wind_melds) != 1 or wind_melds[0] not in {own_wind_val, round_wind_val}:
            return False
        eye_val = eyes[0].tiles[0].value
        return eye_val in HONOR_SCORING

    def _is_hijos_de_la_noche(self, groups) -> bool:
        #HIJOS DE LA NOCHE: 7 pares de la misma pinta (C, P o B) sin repetir número.
        if len(groups) != 7:
            return False
        first_tile = groups[0].tiles[0].value
        suit = first_tile[0]
        if suit not in {'C', 'P', 'B'}:
            return False
        pair_vals = []
        for g in groups:
            if len(g.tiles) != 2 or g.tiles[0].value != g.tiles[1].value:
                return False
            val = g.tiles[0].value
            if val[0] != suit:
                return False
            pair_vals.append(val)
        return len(set(pair_vals)) == 7

    def _is_ases_y_nueves(self, melds, eyes) -> bool:
        #ASES Y NUEVES: Pungs y Ojos compuestos exclusivamente de unos (ases) y nueves de cualquier pinta (C1, C9, P1, P9, B1, B9).
        if len(melds) != 4 or len(eyes) != 1:
            return False
        if not all(m.type == GroupType.PUNG for m in melds):
            return False
        all_tiles = [t.value for g in melds + eyes for t in g.tiles]
        return all(t in MINOR_HONORS for t in all_tiles)

    def _is_jaspe_verde(self, melds, eyes) -> bool:
        #JASPE VERDE: Pungs, Chows y Ojos de puros palos verdes (P2, P3, P4, P6, P8 y DV).
        if len(melds) != 4 or len(eyes) != 1:
            return False
        all_tiles = [t.value for g in melds + eyes for t in g.tiles]
        return all(t in GREEN_TILES for t in all_tiles)

    def _is_gran_seguidilla_real(self, melds, eyes, own_wind_val: str, round_wind_val: str) -> bool:
        #GRAN SEGUIDILLA REAL: Seguidilla del 1 al 9 (tres Chows continuos) de una misma pinta, un trío (Pung) de dragón y ojos del viento propio o predominante.
        if len(melds) != 4 or len(eyes) != 1:
            return False

        eye_val = eyes[0].tiles[0].value
        if eye_val not in {own_wind_val, round_wind_val}:
            return False

        #Debe tener exactamente 1 Pung de dragón
        dragon_melds = [m for m in melds if m.type == GroupType.PUNG and m.tiles[0].value in DRAGONS]
        if len(dragon_melds) != 1:
            return False

        #Los otros tres melds deben ser Chows
        chow_melds = [m for m in melds if m.type == GroupType.CHOW]
        if len(chow_melds) != 3:
            return False

        #Todos los Chows deben pertenecer a la misma pinta (C, P, o B)
        chow_tiles = [t.value for m in chow_melds for t in m.tiles]
        suit = chow_tiles[0][0]
        if suit not in {'C', 'P', 'B'}:
            return False
        if not all(t[0] == suit for t in chow_tiles):
            return False

        #Y deben cubrir exactamente los números del 1 al 9
        ranks = {int(t[1]) for t in chow_tiles if t[1].isdigit()}
        if ranks != set(range(1, 10)):
            return False

        return True

    def _is_siete_samurais(self, groups) -> bool:
        #7 SAMURAIS: 7 pares de honores (vientos, dragones, ases y nueves) sin repetir
        if len(groups) != 7:
            return False
        pair_vals = []
        for g in groups:
            if len(g.tiles) != 2 or g.tiles[0].value != g.tiles[1].value:
                return False
            val = g.tiles[0].value
            if val not in HONOR_SCORING:
                return False
            pair_vals.append(val)

        if len(set(pair_vals)) != 7:
            return False

        #Debe incluir honores menores (ases y nueves) para diferenciarse de Grandes Samurais
        return any(v in MINOR_HONORS for v in pair_vals)

    def _is_trece_maravillas(self, groups) -> bool:
        #13 MARAVILLAS: 1 de cada uno de los 13 honores (E, S, W, N, DR, DV, DB, C1, C9, P1, P9, B1, B9) más uno repetido
        all_tiles = [t.value for g in groups for t in g.tiles]
        if len(all_tiles) != 14:
            return False
        return set(all_tiles) == HONOR_SCORING       

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
            with open('input.txt', 'r', encoding='utf-8') as f:
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
        with open('output.txt', 'w', encoding='utf-8') as f:
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