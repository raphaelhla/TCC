## KUBERNETES CLUSTER IMPLANTATION
### INSTALAÇÃO KUBERNETES COM CONTAINERD
---
O script deve ser executado tanto no control plane quanto nos worker nodes!

Versão com o KUBEADM.

##### REQUISITOS
 
- Máquina Linux (aqui no caso vou utilizar Ubuntu 22.04)
- 2 GB de memória RAM
- 2 CPUs
- Conexão de rede entre as máquinas
- Hostname, endereço MAC e product_uuid únicos para cada nó.
- Swap desabilitado
 
Portas que precisam esta abertas:

<br>

Portas para control plane
| Protocolo | Range de Porta | Uso | Quem consome |
|--- |--- |--- |--- |
| TCP | 6443 | Kubernetes API server | Todos |
| TCP | 2379-2380 | etcd server client API | kube-apiserver, etcd |
| TCP | 10250 | Kubelet API | Self, Control plane |
| TCP | 10259 | kube-scheduler | Self |
| TCP | 10257 | kube-controller-manager | Self |

<br>

Portas para worker node
| Protocolo | Range de Porta | Uso | Quem consome |
|--- |--- |--- |--- |
| TCP | 10250 | Kubernetes API server | Self, Control plane |
| TCP | 30000-32767 | NodePort Services | Todos |

<br>

##### CONFIGURANDO O AMBIENTE

- Logue como usuário root:
    `sudo su`
- Execute o script:
    `bash config-vm.sh`


##### INICIANDO O CLUSTER

###### No control plane:

- Para iniciar o cluster faça:
    ```bash
    kubeadm init
    ```
- Após a inicialização, para configurar o kubectl, faça:
    ```bash
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```
- Use o comando abaixo para obter o comando de join, que será usado no worker node:
    ```bash
    kubeadm token create --print-join-command
    ```

