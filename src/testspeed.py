#!/opt/rh/rh-python36/root/usr/bin/python
import subprocess
import time
import sys
import os

# 1. Validar argumentos de la terminal
# Uso esperado: python testspeed.py <numero_procesos> <archivo_mpi.py>
if len(sys.argv) < 3:
    print("[TESTSPEED - ERROR] Faltan argumentos.")
    print("Uso correcto: python testspeed.py <np> <pyfile>")
    print("Ejemplo:      python testspeed.py 2 andres.py")
    sys.exit(1)

NUMERO_PROCESOS = sys.argv[1]
ARCHIVO_MPI = sys.argv[2]

# 2. Resolver la ruta exacta usando la variable de entorno $HOME del sistema
# Esto convierte '$HOME/runmpi.sh' en '/home/admin/runmpi.sh' dinámicamente
ruta_script_bash = os.path.expandvars("$HOME/runmpi.sh")

# Construimos la llamada exacta pactada
comando = [ruta_script_bash, NUMERO_PROCESOS, ARCHIVO_MPI]

print("==========================================================")
print(f"[TESTSPEED] Lanzando: {ruta_script_bash} {NUMERO_PROCESOS} {ARCHIVO_MPI}")
#print("==========================================================")
sys.stdout.flush()

# 3. Registrar el tiempo de inicio 
inicio = time.perf_counter()

# 4. Ejecutar el script de Bash sin interrumpir sus salidas a pantalla
try:
    subprocess.run(
        comando,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
except subprocess.CalledProcessError as e:
    print(f"\n[TESTSPEED - ERROR] El script bash falló con código de salida: {e.returncode}")
    sys.exit(1)

# 5. calcular el tiempo total
fin = time.perf_counter()
tiempo_total = fin - inicio

#print("\n" + "="*58)
print(f"[TESTSPEED] Medición finalizada")
print(f"[TESTSPEED] Tiempo total: {tiempo_total:.6f} segundos")
print("="*58)
