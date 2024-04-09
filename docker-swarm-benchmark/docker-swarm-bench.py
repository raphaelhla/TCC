import docker
import time
import psutil

def calcular_media(lista):
    if not lista:
        return 0

    soma = sum(lista)
    media = soma / len(lista)

    return media

def gerar_mensagem(replicas, num_testes, historico_tempo, historico_ram, historico_cpu):
    
    media_tempo = calcular_media(historico_tempo)
    media_ram = calcular_media(historico_ram)
    media_cpu = calcular_media(historico_cpu)

    mensagem = [
        f"Número de replicas: {replicas}\n",
        f"Número de testes: {num_testes}\n",
        f"Tempo médio gasto: {media_tempo}\n",
        f"Uso médio de RAM: {media_ram}\n",
        f"Uso médio de CPU: {media_cpu}\n",
        f"Histórico de tempo: [{', '.join(map(str, historico_tempo))}]\n",
        f"Histórico de RAM: [{', '.join(map(str, historico_ram))}]\n",
        "\n"
    ]

    return ''.join(mensagem)

def escrever_mensagem_arquivo(mensagem):
    nome_arquivo = "result.txt"

    try:
        with open(nome_arquivo, "a") as arquivo:
            arquivo.write(mensagem)
    except Exception as e:
        print(f"Ocorreu um erro ao escrever no arquivo: {e}")

def obter_consumo_cpu():
    import psutil

def calcular_uso_cpu():
    uso_cpu = psutil.cpu_percent(interval=1)
    return uso_cpu

def obter_consumo_memoria():
    mem = psutil.virtual_memory()

    consumo_percentual = mem.percent
    consumo_mb = mem.used / 1024 / 1024

    print(f" * Consumo de memória RAM atual: {consumo_percentual:.2f}%")
    print(f" * Consumo de memória RAM atual: {consumo_mb:.2f} MB")

    return consumo_percentual, consumo_mb

def cria_servico_e_aguarda(client, service_name, image, replicas):

    # Cria o serviço com o número especificado de réplicas
    service = client.services.create(
        image=image,
        name=service_name,
        mode={'Replicated': {'Replicas': replicas}},
        endpoint_spec={
            'Ports': [{
                'Protocol': 'tcp',
                'TargetPort': 8080,
                'PublishedPort': 80
            }]
        }
    )

    print(f" * Serviço {service_name} criado com {replicas} réplicas. Aguardando todas ficarem prontas...")

    start_time = time.time()
    while True:
        service.reload()
        tasks = service.tasks()

        running_tasks = sum(1 for task in tasks if task['Status']['State'] == 'running')

        #print(f"Réplicas em execução: {running_tasks}/{replicas}")

        if running_tasks == replicas:
            break

    end_time = time.time()
    total_time = end_time - start_time
    print(f" * Todas as réplicas estão prontas. Tempo total: {total_time:.2f} segundos.")
    return total_time

def remove_servico(client, service_name):
    #client = docker.from_env()

    try:
        service = client.services.get(service_name)
        service.remove()
        print(f" * Serviço '{service_name}' removido com sucesso.")
    except docker.errors.NotFound:
        print(f"Serviço '{service_name}' não encontrado.")
    except Exception as e:
        print(f"Erro ao remover o serviço '{service_name}': {e}")



if __name__ == "__main__":
    service_name = "pingpodswarm"
    image = "raphaelhla/ping-pod"
    replicas = int(input("Digite o número de replicas: "))
    
    num_testes = int(input("Digite o número de testes: "))

    historico_tempo = []
    historico_ram = []
    historico_cpu = []
    

    client = docker.from_env()

    
    for i in range(1, num_testes + 1):
        print(f"\nTeste {i}")
        tempo_gasto = cria_servico_e_aguarda(client, service_name, image, replicas)
        time.sleep(3)

        consumo_percentual, consumo_mb = obter_consumo_memoria()
        time.sleep(3)

        remove_servico(client, service_name)
        time.sleep(20)
    
        historico_tempo.append(tempo_gasto)
        historico_ram.append(consumo_mb)

    result = gerar_mensagem(replicas, num_testes, historico_tempo, historico_ram, historico_cpu)
    escrever_mensagem_arquivo(result)

