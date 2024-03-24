## DOCKER SWARM CLUSTER IMPLANTATION
### INSTALAÇÃO DOCKER SWARM
---
O script deve ser executado tanto no Manager quanto nos worker nodes!

##### REQUISITOS
 
Portas que precisam esta abertas:

<br>

Portas para todas as máquinas do cluster
| Protocolo | Range de Porta | Uso | Quem consome |
|--- |--- |--- |--- |
| TCP | 2377 | Docker | Todos |

<br>

##### CONFIGURANDO O AMBIENTE

- Logue como usuário root:
    `sudo su`
- Execute o script:
    `bash config-vm.sh`


##### INICIANDO O CLUSTER

###### No Manager:

- Para iniciar o cluster faça:
    ```bash
    docker swarm init
    ```
- Use o comando abaixo para obter o comando de join, que será usado no worker node:
    ```bash
    docker swarm join-token worker
    ```
