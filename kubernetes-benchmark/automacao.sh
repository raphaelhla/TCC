#!/bin/bash

declare -a num_replicas=(1 10 25 50 100 150)
num_testes=10
tempo_sleep=10

for num in "${num_replicas[@]}"; do
	echo -e "Iniciando o script com $num replicas e $num_testes testes..."

	python3 kube-bench.py $num $num_testes

	echo -e "\nScript finalizado\n"
	echo -e "=====================================================================================================\n"

	sleep $tempo_sleep
done

