from typing import List, Set
from models import (
    Style,
    Tile,
    GroupType,
    WINDS,
    DRAGONS,
    MAJOR_HONORS,
    MINOR_HONORS,
    HONOR_SCORING,
)

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

        if self._is_flor_del_cerezo(final_tile_val, own_wind_val, flower_vals):
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
        self, final_tile_val: str, own_wind_val: str, flower_vals: List[str]
    ) -> bool:
        #LA FLOR DEL CEREZO: Mahjong con B5 al finaly flor propia.
        if final_tile_val != 'B5':
            return False
        own_flowers = OWN_FLOWER_MAP.get(own_wind_val, set())
        return any(f in own_flowers for f in flower_vals)

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