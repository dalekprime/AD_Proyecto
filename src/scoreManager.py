def esHonor(grupo):
    return True

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
                subscore = 4
            elif tp == GroupType.PUNG:
                subscore = 2
            elif tp == GroupType.EYE:
                dragon = g.tiles[0].value
                if ficha in ['DR', 'DV', 'DB']:
                    dragones.add(ficha)
            else:
                continue
                hayChow = True
            if ab == False:
                subscore *= 2
            if hn == True:
                subscore *= 2
            score += subscore
        
        if hayChow:
            score += 20
        else:
            score += 30
        
        if 'DR' in dragones:
            score += 4


        self.baseScore = score + 300
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

        
        pintas = set()
        tiene_letras = False
        cant_chows = 0
        cant_pungs = 0
        
        for g in self.groups:
            ficha = g.tiles[0].value
            if ficha in ['E', 'S', 'W', 'N', 'DR', 'DV', 'DB']:
                tiene_letras = True
            else:
                pinta = ficha[0]
                pintas.add(pinta)
            
            if g.type == GroupType.CHOW:
                cant_chows += 1
            elif g.type in (GroupType.PUNG, GroupType.KUNG):
                cant_pungs += 1

        
        if len(pintas) == 1:
            pinta_actual = list(pintas)[0]
            
            if not tiene_letras:
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
                
                tiene_pung_1 = any(g.type in (GroupType.PUNG, GroupType.KUNG) and g.tiles[0].value == f"{pinta_actual}1" for g in self.groups)
                tiene_pung_9 = any(g.type in (GroupType.PUNG, GroupType.KUNG) and g.tiles[0].value == f"{pinta_actual}9" for g in self.groups)
                
                if tiene_pung_1 and tiene_pung_9:
                    doubles += 3
                    self.log.append("Limpio (Honores con Ases y Nueves): +3 dobles")
                else:
                   
                    if cant_chows == 0:
                        doubles += 2
                        self.log.append("Sucio (Pinta sin chow): +2 dobles")
                    else:
                        doubles += 1
                        self.log.append("Sucio (Pinta con chow): +1 doble")

        self.doubles = doubles
        
        