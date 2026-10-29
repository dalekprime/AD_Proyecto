#!/bin/bash

NODOS=$(grep -v '^#' "machinefiles" | awk '{print $1}')

echo "Preparando ejecución..."

for nodo in $NODOS; do
    # -q y la redirección ocultan banners de SSH, barras de progreso y advertencias
    /usr/bin/scp -q $HOME/$2 $nodo:$HOME/$2 #> /dev/null 2>&1
done

mpiexec \
  --mca orte_base_help_aggregate 0 \
  --mca btl tcp,self \
  --mca shmem_mmap_relocate_backing_file 1 \
  -n $1 \
  --hostfile machinefiles \
  python $HOME/$2
