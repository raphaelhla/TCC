import subprocess
import yaml
import time

def create_pods(namespace, num_pods):
    for i in range(num_pods):
        subprocess.run(['kubectl', 'run', f'pod-{i}', '--image=nginx', '--namespace', namespace, '--restart=Never'])

def get_pod_status(namespace):
    output = subprocess.check_output(['kubectl', 'get', 'pods', '--namespace', namespace, '-o', 'yaml'])
    pod_data = yaml.safe_load(output)
    pod_status = {}
    for pod in pod_data['items']:
        pod_name = pod['metadata']['name']
        pod_status[pod_name] = pod['status']['phase']
    return pod_status

def all_pods_running(pod_status, num_pods):
    return len(pod_status) == num_pods and all(status == 'Running' for status in pod_status.values())

def benchmark_creation_time(namespace, num_pods):
    start_time = time.time()
    create_pods(namespace, num_pods)
    while True:
        pod_status = get_pod_status(namespace)
        if all_pods_running(pod_status, num_pods):
            break
    end_time = time.time()
    return end_time - start_time

def kill_all_pods():
    subprocess.run(['kubectl', 'delete', 'pods', '--all'])

namespace = 'default'
num_pods = int(input("Digite o numero de pods: "))
creation_time = benchmark_creation_time(namespace, num_pods)
print(f'Tempo total para criar e iniciar todos os {num_pods} pods: {creation_time} segundos')
