import pygame
import sys
import os
import re

# --- CONFIGURACIÓN DE ESTILO ---
COLOR_FONDO = (20, 60, 40)  # Verde tapete
COLOR_TEXTO = (240, 240, 240)
COLOR_VALORES = (255, 215, 0)
COLOR_ULTIMA = (255, 0, 0)  # Marco rojo
FUENTE_TAMANO = 22

class VisorMahjongCompleto:
    def __init__(self, archivo="soluciones_maestro.txt", carpeta_tiles="tiles"):
        pygame.init()
        self.screen = pygame.display.set_mode((1500, 750))
        pygame.display.set_caption("Visor Dataset Mahjong - Andres Sanoja - Daniela Ramos (Revisora)")
        self.clock = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("Segoe UI", FUENTE_TAMANO, bold=True)
        self.fuente_pequena = pygame.font.SysFont("Segoe UI", 18, bold=True)
        
        self.carpeta_tiles = carpeta_tiles
        self.imagenes = self.cargar_imagenes()
        self.datos = self.cargar_datos(archivo)
        self.indice = 0

    def cargar_imagenes(self):
        imgs = {}
        if not os.path.exists(self.carpeta_tiles):
            print(f"Error: No existe la carpeta '{self.carpeta_tiles}'")
            return imgs
        
        for f in os.listdir(self.carpeta_tiles):
            if f.lower().endswith(".png"):
                nombre = f.replace(".png", "").replace(".PNG", "")
                ruta = os.path.join(self.carpeta_tiles, f)
                img = pygame.image.load(ruta).convert_alpha()
                imgs[nombre] = pygame.transform.smoothscale(img, (60, 80))
        return imgs

    def cargar_datos(self, archivo):
        lineas = []
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    if "|" in linea:
                        lineas.append([p.strip() for p in linea.split("|")])
        except FileNotFoundError:
            print(f"Error: {archivo} no encontrado.")
            sys.exit()
        return lineas

    def dibujar_piedra(self, codigo, x, y, resaltado=False):
        if codigo in self.imagenes:
            self.screen.blit(self.imagenes[codigo], (x, y))
            if resaltado:
                pygame.draw.rect(self.screen, COLOR_ULTIMA, (x-3, y-3, 66, 86), 4)
        else:
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y, 60, 80))
            txt = self.fuente.render(codigo, True, (0, 0, 0))
            self.screen.blit(txt, (x + 5, y + 25))

    def mostrar_jugada(self):
        if not self.datos: return
        self.screen.fill(COLOR_FONDO)
        
        linea_visual = self.datos[self.indice][0]

        # --- LEYENDA PIEDRA GANADORA ---
        pygame.draw.rect(self.screen, COLOR_ULTIMA, (1200, 30, 30, 30), 3)
        leyenda_txt = self.fuente_pequena.render("= ULTIMA PIEDRA CARGADA", True, COLOR_TEXTO)
        self.screen.blit(leyenda_txt, (1240, 35))

        # --- VALIDACIÓN DE PUNTOS TOTALES (< 300) ---
        try:
            # El campo indexado con 3 corresponde a la columna de puntuación final
            puntos_totales = int(float(self.datos[self.indice][3]))
        except:
            puntos_totales = 0

        if puntos_totales < 300:
            # Recuadro rojo de advertencia elegante en la parte superior derecha
            pygame.draw.rect(self.screen, (220, 53, 69), (1200, 85, 250, 40), border_radius=6)
            # Icono gráfico circular de restricción (X blanca sobre fondo rojo)
            pygame.draw.circle(self.screen, (255, 255, 255), (1222, 105), 11)
            pygame.draw.line(self.screen, (220, 53, 69), (1216, 99), (1228, 111), 3)
            pygame.draw.line(self.screen, (220, 53, 69), (1228, 99), (1216, 111), 3)
            # Leyenda explícita solicitada
            txt_invalida = self.fuente_pequena.render("MANO NO VÁLIDA (<300)", True, (255, 255, 255))
            self.screen.blit(txt_invalida, (1242, 94))

        # 1. Extraer Vientos [Vp / Vr]
        match_vientos = re.search(r'\[(.*?)/(.*?)\]', linea_visual)
        if match_vientos:
            vp, vr = match_vientos.group(1).strip(), match_vientos.group(2).strip()
            self.screen.blit(self.fuente.render("Propio / Predominante:", True, COLOR_TEXTO), (50, 30))
            self.dibujar_piedra(vp, 400, 15)
            self.dibujar_piedra(vr, 470, 15)

        # 2. Extraer Última Piedra
        ultima_piedra = ""
        if "*" in linea_visual:
            ultima_piedra = linea_visual.split("*")[1].strip()

        # 3. Extraer y Dibujar la MANO
        self.screen.blit(self.fuente.render("MANO:", True, COLOR_TEXTO), (50, 140))
        try:
            parte_mano = linea_visual.split("]", 1)[1].split("<")[0]
            grupos = parte_mano.split(" ")
            x_pos = 150
            flag_ultima = False 
            grupos = list(filter(None, grupos))
            for grupo in grupos:
                oculta = False
                if grupo.startswith('{') and grupo.endswith('}'):
                    oculta = True
                    grupo_limpio = grupo[1:-1]
                else:
                    grupo_limpio = grupo.strip('[]()')
                piezas = grupo_limpio.split("-")
                mitad = len(piezas) // 2
                pos = 0
                for p in piezas:
                    es_ultima = (p == ultima_piedra) and not flag_ultima
                    if oculta and (pos == mitad):
                        self.dibujar_piedra("back", x_pos, 120, resaltado=es_ultima)
                    else:
                        self.dibujar_piedra(p, x_pos, 120, resaltado=es_ultima)
                    x_pos += 65
                    pos += 1
                    if es_ultima: flag_ultima = True
                x_pos += 25 
        except: pass

        # 4. Extraer y Dibujar FLORES
        self.screen.blit(self.fuente.render("FLORES:", True, COLOR_TEXTO), (50, 250))
        match_flores = re.search(r'<(.*?)>', linea_visual)
        if match_flores:
            contenido_flores = match_flores.group(1)
            flores = re.findall(r'[RG][1-4]', contenido_flores)
            x_f = 150
            for f in flores:
                self.dibujar_piedra(f, x_f, 230)
                x_f += 65

        # 5. PANEL DE DATOS TÉCNICOS
        self.dibujar_panel_datos()

    def dibujar_panel_datos(self):
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (50, 350, 1350, 330))
        
        base, dobles, total, tipo, history = self.datos[self.indice][1:]
        
        y_text = 370
        etiquetas = ["PUNTOS BASE (CUENTA):", "DOBLES TOTALES:", "PUNTUACIÓN FINAL:", "ESTILO DE MANO:"]
        valores = [base, dobles, total, tipo]
        
        # 1. Dibujar datos principales
        for i in range(len(etiquetas)):
            img_etiqueta = self.fuente.render(etiquetas[i], True, COLOR_TEXTO)
            img_valor = self.fuente.render(str(valores[i]), True, COLOR_VALORES)
            self.screen.blit(img_etiqueta, (100, y_text))
            self.screen.blit(img_valor, (450, y_text))
            
            # Alerta secundaria directamente junto al valor numérico en la tabla de datos
            if i == 2:
                try:
                    pt = int(float(total))
                except:
                    pt = 0
                if pt < 300:
                    pygame.draw.rect(self.screen, (220, 53, 69), (550, y_text - 2, 130, 26), border_radius=4)
                    txt_alerta = self.fuente_pequena.render("INVÁLIDA", True, (255, 255, 255))
                    self.screen.blit(txt_alerta, (580, y_text))
                    pygame.draw.circle(self.screen, (255, 255, 255), (565, y_text + 11), 7)
                    pygame.draw.line(self.screen, (220, 53, 69), (561, y_text + 7), (569, y_text + 15), 2)
                    pygame.draw.line(self.screen, (220, 53, 69), (569, y_text + 7), (561, y_text + 15), 2)
                    
            y_text += 45

        # 2. Renderizar el HISTORIAL (history)
        y_hist = 370
        x_hist = 700
        
        titulo_hist = self.fuente.render("DESGLOSE / HISTORIAL:", True, COLOR_TEXTO)
        self.screen.blit(titulo_hist, (x_hist, y_hist))
        y_hist += 35
        
        if isinstance(history, str):
            items_history = history.strip("[]").replace("'", "").split(",")
        else:
            items_history = history

        for item in items_history:
            txt_item = item.strip()
            if txt_item:
                img_item = self.fuente_pequena.render(f"• {txt_item}", True, (180, 200, 180))
                self.screen.blit(img_item, (x_hist + 10, y_hist))
                y_hist += 25

        # Info de navegación
        info = f"Examen {self.indice + 1} de {len(self.datos)} | [FLECHAS] Navegar | [ESC] Salir"
        img_info = self.fuente.render(info, True, (150, 150, 150))
        self.screen.blit(img_info, (50, 700))

    def run(self):
        ejecutando = True
        while ejecutando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ejecutando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.indice = (self.indice + 1) % len(self.datos)
                    if event.key == pygame.K_LEFT:
                        self.indice = (self.indice - 1) % len(self.datos)
                    if event.key == pygame.K_ESCAPE:
                        ejecutando = False
            
            self.mostrar_jugada()
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        VisorMahjongCompleto(archivo=sys.argv[1]).run()
    else:
        VisorMahjongCompleto().run()
