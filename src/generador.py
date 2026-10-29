import random

# Definición de fichas
SUITS = ['C', 'P', 'B']
HONORS = ['E', 'S', 'W', 'N', 'DR', 'DV', 'DB']
FLOWERS = ['R1', 'R2', 'R3', 'R4', 'G1', 'G2', 'G3', 'G4']
WINDS = ['E', 'S', 'W', 'N']

def gen_pung_or_kung(tile, is_kung=False):
    num = 4 if is_kung else 3
    bracket = random.choice(['[', '{'])
    close = ']' if bracket == '[' else '}'
    return f"{bracket}{'-'.join([tile]*num)}{close}"

def gen_chow(suit):
    start = random.randint(1, 7)
    tiles = [f"{suit}{start+i}" for i in range(3)]
    bracket = random.choice(['[', '{'])
    close = ']' if bracket == '[' else '}'
    return f"{bracket}{'-'.join(tiles)}{close}"

def gen_eye():
    # Siempre con paréntesis, que es lo único que el parser acepta como EYE
    if random.random() < 0.3:
        tile = random.choice(HONORS)
    else:
        tile = f"{random.choice(SUITS)}{random.randint(1, 9)}"
    return f"({tile}-{tile})"

def gen_random_hand():
    groups = []
    hand_tiles = []
    
    # Generar 4 grupos (3 o 4 fichas)
    for _ in range(4):
        if random.random() < 0.5:
            tile = random.choice(HONORS) if random.random() < 0.3 else f"{random.choice(SUITS)}{random.randint(1, 9)}"
            is_kung = random.random() < 0.3
            g = gen_pung_or_kung(tile, is_kung)
        else:
            g = gen_chow(random.choice(SUITS))
        groups.append(g)
        hand_tiles.extend(g.replace('[','').replace(']','').replace('{','').replace('}','').split('-'))
        
    # Generar ojos (siempre con paréntesis)
    eye = gen_eye()
    groups.append(eye)
    hand_tiles.extend(eye.replace('(','').replace(')','').split('-'))
    
    # Elegir pieza ganadora
    winner = random.choice(hand_tiles)
    return " ".join(groups), winner

def gen_specific_hand(hand_id):
    hand_type = hand_id % 5
    
    if hand_type == 0:
        # 13 Maravillas: bloque único de 14 fichas con []
        tiles = "C1-C9-P1-P9-B1-B9-E-S-W-N-DR-DV-DB-DB"
        groups = f"[{tiles}]"
        winner = "DB"
        
    elif hand_type == 1:
        # 7 Samurais: 7 pares de honores (incluye menores), todos con ()
        pares = ["E-E", "S-S", "W-W", "N-N", "DR-DR", "DV-DV", "C1-C1"]
        random.shuffle(pares)
        groups = " ".join([f"({p})" for p in pares])
        winner = random.choice(["E", "S", "W", "N", "DR", "DV", "C1"])
        
    elif hand_type == 2:
        # Grandes Samurais: 7 pares de honores mayores, todos con ()
        pares = ["E-E", "E-E", "S-S", "S-S", "W-W", "DR-DR", "DR-DR"]
        random.shuffle(pares)
        groups = " ".join([f"({p})" for p in pares])
        winner = random.choice(["E", "S", "W", "DR"])
        
    elif hand_type == 3:
        # Hijos de la Noche: 7 pares de la misma pinta sin repetir número
        suit = random.choice(SUITS)
        numeros = list(range(1, 10))
        random.shuffle(numeros)
        pares = [f"{suit}{n}-{suit}{n}" for n in numeros[:7]]
        groups = " ".join([f"({p})" for p in pares])
        winner = f"{suit}{numeros[0]}"
        
    else:
        # Limpio de una pinta (tradicional)
        groups = "[C1-C2-C3] [C4-C5-C6] [C7-C8-C9] [C1-C1-C1] (C9-C9)"
        winner = "C9"
        
    return groups, winner

def generate_input_file(filename="input.txt", num_lines=5000):
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(1, num_lines + 1):
            vp = random.choice(WINDS)
            vr = random.choice(WINDS)
            
            # 10% de casos clásicos forzados
            if random.random() < 0.10:
                groups, winner = gen_specific_hand(i)
            else:
                groups, winner = gen_random_hand()
                
            # Flores (0 a 4)
            num_flores = random.randint(0, 4)
            flores = " ".join(random.sample(FLOWERS, num_flores)) if num_flores > 0 else ""
            
            line = f"{i} [{vp} / {vr}] {groups} <{flores}> *{winner}*\n"
            f.write(line)
            
    print(f"Archivo '{filename}' generado con {num_lines} casos de prueba.")

if __name__ == '__main__':
    generate_input_file()