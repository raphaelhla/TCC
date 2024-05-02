import docker
import time
import paramiko
import sys

def calcular_media(lista):
    if not lista:
        return 0

    soma = sum(lista)
    media = soma / len(lista)
    media = round(media, 2)

    return media

def gerar_mensagem(num_replicas, num_testes, imagem, historico_tempo, historico_ram, historico_cpu):
    media_tempo = calcular_media(historico_tempo)
    media_ram = calcular_media(historico_ram)
    media_cpu = calcular_media(historico_cpu)

    mensagem = [
        f"Número de replicas: {num_replicas}\n",
        f"Número de testes: {num_testes}\n",
        f"Imagem: {imagem}\n",
        f"Tempo médio gasto: {media_tempo}\n",
        f"Uso médio de RAM: {media_ram}\n",
        f"Uso médio de CPU: {media_cpu}\n",
        f"Histórico de tempo: [{', '.join(map(str, historico_tempo))}]\n",
        f"Histórico de RAM: [{', '.join(map(str, historico_ram))}]\n",
        f"Histórico de CPU: [{', '.join(map(str, historico_cpu))}]\n",
        "\n"
    ]

    return ''.join(mensagem)

def escrever_mensagem_arquivo(mensagem, nome_arquivo):
    try:
        with open(nome_arquivo, "a") as arquivo:
            arquivo.write(mensagem)
    except Exception as e:
        print(f"Ocorreu um erro ao escrever no arquivo: {e}")

def obter_consumo_cpu_ssh(host, private_key):
    while True:
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=host, username="ubuntu", pkey=private_key)

            comando = 'top -bn2 | grep "Cpu(s)" | awk \'{print $2 + $4}\' | tail -n1'

            stdin, stdout, stderr = ssh_client.exec_command(comando)

            output = stdout.read().decode().strip()
            cpu_usado = float(output)
            break
        except paramiko.ssh_exception.AuthenticationException as e:
            print("Erro de autenticação SSH para o worker: ", host) #:", e)
            time.sleep(3)
        except paramiko.ssh_exception.SSHException as e:
            print("Erro no SSH para o worker: ", host) #", e)
            time.sleep(3)
        except Exception as e:
            print("Erro inesperado no SSH para o worker: ", host) #", e)
            time.sleep(3)
        finally:
            ssh_client.close()

    cpu_usado = round(cpu_usado, 2)
    print(f" * Consumo de CPU atual: {cpu_usado}%")

    return cpu_usado

def obter_consumo_memoria_ssh(host, private_key):
    while True:
        try:

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=host, username="ubuntu", pkey=private_key)

            comando = "free -m | grep Mem | awk '{print $3,$2}'"
            stdin, stdout, stderr = ssh_client.exec_command(comando)

            output = stdout.read().decode().strip().split()
            mem_usada_mb = float(output[0])
            mem_total_mb = float(output[1])

            consumo_percentual = (mem_usada_mb / mem_total_mb) * 100
            break
        except paramiko.ssh_exception.AuthenticationException as e:
            print("Erro de autenticação SSH para o worker: ", host) #:", e)
            time.sleep(3)
        except paramiko.ssh_exception.SSHException as e:
            print("Erro no SSH para o worker: ", host) #", e)
            time.sleep(3)
        except Exception as e:
            print("Erro inesperado no SSH para o worker: ", host) #", e)
            time.sleep(3)
        finally:
            ssh_client.close()

    #print(f" * Porcentagem de memória RAM atual: {consumo_percentual:.2f}%")
    print(f" * Consumo de memória RAM atual: {mem_usada_mb:.2f} MB")

    return consumo_percentual, mem_usada_mb

def verificar_consumo_cpu_hosts(lista_hosts, private_key):
    result = []
    for host in lista_hosts:
        cpu = obter_consumo_cpu_ssh(host, private_key)
        result.append(cpu)
    return result

def verificar_consumo_memoria_hosts(lista_hosts, private_key):
    result = []
    for host in lista_hosts:
        _, mem_ram = obter_consumo_memoria_ssh(host, private_key)
        result.append(mem_ram)
    return result

def calcula_tempo_criacao_servico(client, service_name, image, replicas):
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

    tempo_inicial = time.time()
    while True:
        service.reload()
        tasks = service.tasks()

        running_tasks = sum(1 for task in tasks if task['Status']['State'] == 'running')

        if running_tasks == replicas:
            break

    tempo_final = time.time()
    tempo_total = tempo_final - tempo_inicial
    tempo_total = round(tempo_total, 2)
    print(f" * Todas as réplicas estão prontas. Tempo total: {tempo_total:.2f} segundos.")

    return tempo_total

def remove_servico(client, service_name):
    try:
        service = client.services.get(service_name)
        service.remove()
        print(f" * Serviço '{service_name}' removido com sucesso.")
    except docker.errors.NotFound:
        print(f"Serviço '{service_name}' não encontrado.")
    except Exception as e:
        print(f"Erro ao remover o serviço '{service_name}': {e}")

if __name__ == "__main__":
    workers = ["", ""]
    private_key_path = "/home/ubuntu/raphael-key.pem"
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

    service_name = "ping-pod-service"
    image = "raphaelhla/ping-pod:1.0"

    if len(sys.argv) == 1:
        num_replicas = int(input("Digite o número de replicas: "))
        num_testes = int(input("Digite o número de testes: "))
    elif len(sys.argv) == 3:
        num_replicas = int(sys.argv[1])
        num_testes = int(sys.argv[2])
    else:
        print("Uso: python3 docker-swarm-bench.py <numero_de_pods> <numero_de_testes>")
        sys.exit(1)

    historico_tempo = []
    historico_cpu = []
    historico_ram = []

    client = docker.from_env()
    
    for i in range(1, num_testes + 1):
        print(f"\nTeste {i}:")
        
        #cpu_antes = verificar_consumo_cpu_hosts(workers, private_key)
        ram_antes = verificar_consumo_memoria_hosts(workers, private_key)
        time.sleep(2)

        tempo_gasto = calcula_tempo_criacao_servico(client, service_name, image, num_replicas)
        time.sleep(25)
        
        cpu_depois = verificar_consumo_cpu_hosts(workers, private_key)
        ram_depois = verificar_consumo_memoria_hosts(workers, private_key)
        time.sleep(2)

        remove_servico(client, service_name)
        time.sleep(30)
    
        historico_tempo.append(tempo_gasto)
        for i in range(len(workers)):
            #diferenca_cpu = cpu_depois[i] - cpu_antes[i]
            diferenca_ram = ram_depois[i] - ram_antes[i]

            historico_cpu.append(cpu_depois[i])        
            historico_ram.append(diferenca_ram)

    result = gerar_mensagem(num_replicas, num_testes, image, historico_tempo, historico_ram, historico_cpu)
    escrever_mensagem_arquivo(result, "resultados-t2-xlarge.txt")


