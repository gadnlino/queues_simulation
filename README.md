# Trabalho de simulação - Teoria de Filas
#### Guilherme Avelino do Nascimento - DRE 117078497
#### Link para o repositório no GitHub: https://github.com/gadnlino/queues_simulation/blob/simulator3/README_simulator_3.md
#### Observação: no relatório impresso, algumas tabelas podem ter ficado mal formatadas devido do PDF a partir desse arquivo README. Todos os resultados numéricos foram truncados para 3 casas decimais a fim de melhorar a apresentação. Em caso de qualquer dúvida, recomenda-se consultar a versão do README disponível online no GitHub, pelo link acima.
## Introdução

### Visão geral

A implementação foi realizada em Python 3. As instruções para a execução do simulador estão ne seção **Instruções para execução do simulador**.

O ponto inicial é o arquivo `start_simulator_3.py`, onde é criado uma instância do o simulador(classe Simulator3), com os parâmetros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

A execução do simulador é da seguinte forma:

A princípio é gerado um evento inicial de chegada de um cliente na fila 1(evento ARRIVAL para a fila 1). Em seguida o programa permanece em loop, tratando a lista principal de eventos e realizando coletas de amostras das estatísticas para cada cliente(tempo de espera, tempo de serviço, tempo total), e também relativo as filas(número de cliente da fila e na fila de espera). A simulação acaba quando o número de total de coletas da simulação(coletas da rodada x número de rodadas) são realizadas.

Ao final da simulação, são gerados alguns arquivos para a análise do simulador e das métricas. Os arquivos serão descritos mais adiante na seção **Arquivos da simulação**.

Os evento gerados são representados pela tupla (event_type, event_queue), e podem 4 configurações:

- `(ARRIVAL, 1)`: é a chegada de um novo cliente à fila 1. Caso o sistema se encontre totalmente ocioso, o cliente recém chegado inicia imediatamente o serviço. Caso haja um cliente oriundo da fila 2 em serviço, esse tem o serviço interrompido, e o cliente recém chegado na fila 1 inicia o seu serviço imediatamente. Caso haja cliente oriundos da fila 1 em serviço ou na fila de espera, o cliente recém chegado vai para a fila de espera. Após esse tratamento, caso a simulação ainda não tenha terminado, é programado um novo evento para a próxima chegada de um cliente à fila 1.

- `(DEPARTURE, 1)`: é a saída do cliente da fila 1 após a execução de seu primeiro serviço. O cliente recém saído da fila 1 tem o seu evento de chegada à fila 2 programado. Se houver clientes em alguma das filas, esse tem o seu serviço iniciado, seguindo a ordem de prioridade das filas.

- `(ARRIVAL, 2)`: é a chegada de um cliente na fila 2. Caso o sistema se encontre totalmente ocioso, o cliente recém chegado inicia o seu serviço imediatamente. Caso contrário, ele é direcionado para a fila de espera.

- `(DEPARTURE, 2)`: é a saída de um cliente do sistema após o término do seu segundo serviço. Se houverem clientes em alguma das filas de espera, esses tem o seu serviço iniciado, seguindo a ordem de prioridade das filas. O cliente é removido do sistema, e suas métricas(coletadas na entrada e saída de serviço) são utilizadas para incrementar o estimador com as métricas da rodada corrente.

Caso haja uma partida e uma chegada para o exato mesmo instante em qualquer uma das filas, o processamento da partida é realizado previamente ao processamento da chegada.

### Simulador

O simulador pode ser inicializado com os seguintes parâmetros:

- `arrival_process`: O processo de chegada de clientes ao sistema. Valores válidos: 'exponential', 'deterministic'.
- `inter_arrival_time`: O tempo entre chegadas ao sistema. Só é considerado quando o arrival_process = 'deterministic'.
- `service_process`: O processo de serviço do sistema. Valores válidos: 'exponential', 'deterministic'.
- `utilization_pct`: A porcentagem de utilização do sistema($\rho$). Só é considerado quando o arrival_process = 'exponential'.
- `service_rate`: A taxa de serviço do sistema($\mu$). Só é considerado quando o service_process = 'exponential'.
- `service_time`: O tempo de serviço do sistema. Só é considerado quando o service_process = 'deterministic'.
- `number_of_rounds`: O número de rodadas da simulação.,
- `samples_per_round`: O número de amostras que serão coletadas a cada rodada de simulação.
- `arrivals_until_steady_state`: O número de chegada à fila 1 processados até o sistema atingir o estado de equilíbrio.
- `predefined_system_arrival_times`: Instantes de chegada pré determinados. Podem ser utilizados para depurar o simulador.
- `confidence`: float: A significância do intervalo de confiança determinado nas métricas coletadas no sistema.,
- `seed`: A semente inicial para geração de variáveis aleatórias no sistema. Será usada durante toda a simulação.
- `save_raw_event_log_file`: Caso True, salva um arquivo .csv com todos os eventos da simulação(para depuração).
- `save_metric_per_round_file`: Caso True, salva um arquivo .csv ao final da simulação com a evolução das métricas a cada rodada executada.
- `plot_metrics_per_round`: Caso True, gera gráficos ao final da simulação com a evolução de cada uma das métricas a cada rodada executada.

### Estruturas e variáveis internas

Ao longo do código, são utilizadas diversas variáveis e estruturas de controle. Dentre elas, as mais relevantes são:

- `__event_q`: É a lista principal de eventos do simulador. De maneira geral, os eventos são inseridos na lista de maneira que permaneça sempre de maneira crescente pelo `timestamp` dos eventos. Se houver uma chegada e uma partida com o mesmo instante, a partida é inserida em uma posição antecedente a da chegada, a fim de que seja processada primeiro.

- `__waiting_qs`: representação das filas de espera do sistema(lista de listas). É gerenciada utilizando a estratégia FIFO, suportada pelas APIs padrão de listas do Python. Os clientes que têm seus serviços interrompidos são postos execpcionalmente na primeira posição da fila.

- `__arrival_rate`: A taxa de chegada de clientes ao sistema. É obtida pela relação $$\rho = {2\lambda}$$, descrita no enunciado do trabalho.

- `__current_timestamp`, `__current_service`, `__interrupted_service`: Armazenam o tempo corrente de simulação , o serviço corrente em execução e o ultimo serviço interrompido. O timestamp é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor de current_service é modificado. Sempre que um cliente inicia o seu serviço, o simulador calcula os tempos de espera para esse cliente. Da mesma forma, quando um cliente sai do serviço, é calculado o seu tempo de serviço. Finalmentem sempre que um cliente é interrompido e retorna para o serviço, o valor de interrupted_service é atualizado.

- `__current_round`: O número de rodadas da simulação, o número de amostras coletadas a cada rodada, e o contador da rodada corrente.

- `__metric_estimators_current_round`, `__metrics_per_round`, `__metric_estimators_simulation`: No tratamento de cada tipo de evento, `__metric_estimators_current_round` é increntado com a métrica calculada para cada cliente. Ao final de cada rodada, o método `__generate_round_metrics` é chamado e as métricas para a rodada atual são geradas. O resultado é armazenado como um registro na lista `__metrics_per_round` e incrementado no estimador global das métricas da simulação, `__metric_estimators_simulation`. Essas estruturas são usadas gerar os gráficos e os arquivos .csv ao final da simulação.

- `__clients_in_system`: Armazena todos os clientes presentes no sistema, seus eventos, e as métricas calculadas para o cliente(tempo de espera, tempo de serviço, etc.).

- `__metric_estimators_current_round`: os estimadores para as métricas da rodada atual. Cada métrica tem o estimador associado(ver seção **Classe Estimator** abaixo). São obtidos utilizando o cálculo incremental para a média e variância. 

- `__metrics_per_round`: Dataframe com as evolução de cada uma das métricas coletadas ao longo das rodadas. É utilizado para salvar o arquivo .csv com a evolução das métricas ao final da simulação.

- `__metric_estimators_simulation`: Os estimadores para as métricas globais da simulação. É utilizada para gerar o arquivo .csv com as métricas globais da simulação.

- `__execution_parameters`: Parâmetros utilizados na execução da simulação. 

### Estimadores

Para a estimativa das métricas da simulação, foram utilizados 2 tipos de estimadores:

- `IncrementalEstimator`: como o nome sugere, realiza a estimativa da média e da variância do parametro coletado utilizando o cálculo incremental. E usado para calcular o valor médio e variãncia das métricas dos clientes(tempo de espera e tempo total). A implementação está no arquivo `utils/incremental_estimator.py`.

- `AreaEstimator`: usa o cálculo de área x tempo. É usado para calcular o valor esperado e variância dos parâmetros relacionados à fila(número de clientes). A implementação está no arquivo `utils/area_estimator.py`.

### Geração de VA's

A geração de variáveis aleatórias é feita usando a função [random](https://docs.python.org/3/library/random.html#random.random), disponível na biblioteca padrão do Python. A $s$ inicial utilizada é a informada na configuração dos parâmetros do simulador.

Para gerar amostras de variáveis aleatórias exponenciais, é usado o seguinte cálculo(como também indicado nos materiais de aula): $x_0 = {\log{u_0} \over -\lambda}$

### Coleta das amostras

Após o tratamento de cada evento que altere o número de clientes no sistema, em qualquer uma das filas, calcula-se o número de clientes nas filas de esperas.

Sempre que um cliente é posto em serviço, o seu tempo de espera na fila é incrementado; Quando o serviço termina, o seu tempo de serviço efetivo é coletado e guardado na estrutura de dados do cliente.

Quando um cliente termina o seu segundo serviço e é removido do sistema, calcula-se o seu tempo total em cada uma das filas. Se o cliente tiver a sua atribuição de cor igual a da rodada corrente, cada uma das suas métricas($X_1$, $W_1$, $T_1$, $X_2$, $W_2$, $T_2$) é então adicionada ao estimador da rodada. Caso contrário, os valores são descartados.

Quando há o final da rodada, é obtido os valores de $X_i$, com a média e a variância das métricas para aquela rodada, e então adicionado no estimador geral da simulação.

### Arquivos de saída da simulação

Ao final da execução, o simulador salva os arquivos para análise das métricas na pasta `results_{timestamp}_simulator3`. Estes são:

- Arquivos .png(exemplo: `W1_est_mean_X_round.png`) com os valores médios de cada uma das métricas, a cada rodada;
- `simulation_metrics.csv`: onde são armazenados os resultados finais(média, variância, intervalos de confiança) de cada uma das métricas. As colunas do arquivo representam:
    - mean: $\hat{\mu}$
    - variance: $\hat{\sigma}^2$
    - lower_t: $t_{\alpha/2;n-1}$
    - mean_analytical: $\mu$
    - upper_t: $t_{1 - \alpha/2;n-1}$
    - precision_t: $t_{1 - \alpha/2;n-1} \frac{\hat{\sigma}}{\hat{\mu}\sqrt{n}}$. será mencionado adiante por $pr(t)$
    - lower_chi2: ${\chi^2}_{\alpha/2;n-1}$
    - upper_chi2: ${\chi^2}_{1-\alpha/2;n-1}$
    - precision_chi2: $\frac{{\chi^2}_{1-\alpha/2;n-1} - {\chi^2}_{\alpha/2;n-1}}{{\chi^2}_{1-\alpha/2;n-1} + {\chi^2}_{\alpha/2;n-1}}$. Será mencionado adiante por $pr({ \chi^2 })$
    - rounds: $n$, número de rodadas
    - confidence: ${1- \alpha}$
    - mean_cov: $\frac{Cov(X_1, X_2) + ... + Cov(X_{n-1}, X_n)}{n}$, a média da covâriancia entre rodadas da simulação
    - mean_cov_var: $\frac{\frac{Cov(X_1, X_2) + ... + Cov(X_{n-1}, X_n)}{n}}{\sigma^2}$, a razão entre a média da covariância entre rodadas da simulação, e a variância obtida para a métrica especificada.
- `execution_parameters.csv`: os parâmetros utilizados para a simulação. As colunas do arquivo representam:
    - confidence: ${1- \alpha}$
    - utilization_pct: $\rho$, a taxa de utilização do sistema
    - arrival_process: processo de chegada
    - inter_arrival_time: tempo entre chegadas(somente para processo de chegada determinístico).
    - service_process: processo de realização dos serviços no sistema
    - service_rate: $\mu$, a taxa de serviço.
    - service_time: o tempo de serviço(somente para processo de serviço determinístico).
    - number_of_rounds: $n$, o número de rodadas da simulação.
    - samples_per_round: $k$, o número de amostras em cada rodada da simulação.
    - arrivals_until_steady_state: $t$, o número de chegadas desprezadas na fase transiente.
    - predefined_system_arrival_times: tempos de chegadas pré-determindos, informados na inicialização do simulador.
    - seed: $s$, a seed utilizada na simulação.
    - simulation_time: o tempo total de simulação.
- `metric_per_round_evolution.csv`: evolução das métricas, rodada a rodada. É a representação tabular dos dados apresentados nos arquivos .png .
- `event_log_raw.csv`: Lista com todos os eventos tratados na simulação.

## Corretude do simulador e análise dos resultados

### Cenários controlados

1) Chegadas a cada 2 segundos, serviço constante = 1 segundo:

Nesse cenário, o tempo de espera para os clientes em ambas as filas é; o cliente chega ao sistema pela fila 1 e tem os seus 2 serviços realizados antes que um novo cliente chegue e o interrompa. A variância dos tempo de espera e de serviço também deve ser nula para esse cenário.

Parâmetros alvo: $E[W_1] = 0$, $V[W_1] = 0$, $E[W_2] = 0$, $E[T_1] = E[X] = 1$, $E[T_2] = E[X] = 1$

###### Tabela 1

| ${1- \alpha}$ 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 10               	| 2                 	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|---------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $E[T_1]$   	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606     	| 0.33215132908679623                                           	|                           	|                             	|                                                                                                                   	|
| $V[T_1]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[T_2]$   	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606     	| 0.33215132908679623                                           	|                           	|                             	|                                                                                                                   	|
| $V[T_2]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[W_1]$   	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_1]$ 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[W_2]$   	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_2]$ 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[X_1]$   	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606     	| 0.33215132908679623                                           	|                           	|                             	|                                                                                                                   	|
| $V[X_1]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[X_2]$   	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606     	| 0.33215132908679623                                           	|                           	|                             	|                                                                                                                   	|
| $V[X_2]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|

Utilizando um número de amostras por rodada:

###### Tabela 2


| ${1- \alpha}$ 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 10               	| 1000              	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|---------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $E[T_1]$   	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267      	| 0.22281388519649376                                           	|                           	|                             	|                                                                                                                   	|
| $V[T_1]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[T_2]$   	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267      	| 0.22281388519649376                                           	|                           	|                             	|                                                                                                                   	|
| $V[T_2]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[W_1]$   	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_1]$ 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[W_2]$   	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_2]$ 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[X_1]$   	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267      	| 0.22281388519649376                                           	|                           	|                             	|                                                                                                                   	|
| $V[X_1]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|
| $E[X_2]$   	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267      	| 0.22281388519649376                                           	|                           	|                             	|                                                                                                                   	|
| $V[X_2]$ 	| 0.0                	| 0.0                 	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.7263419942725865                                                                                                	|


Com um número grande de rodadas e de amostras por rodada:

###### Tabela 3

| ${1- \alpha}$ 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$       	| $t_{\alpha/2;n-1}$ 	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|------------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $E[T_1]$   	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836      	| 0.0005941463981405022                                         	|                           	|                             	|                                                                                                                   	|
| $V[T_1]$ 	| 0.0                	| 0.0                    	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|
| $E[T_2]$   	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836      	| 0.0005941463981405022                                         	|                           	|                             	|                                                                                                                   	|
| $V[T_2]$ 	| 0.0                	| 0.0                    	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|
| $E[W_1]$   	| 0.0                	| 0.0                    	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_1]$ 	| 0.0                	| 0.0                    	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|
| $E[W_2]$   	| 0.0                	| 0.0                    	| 0.0                	| 0.0                    	| 0.0                                                           	|                           	|                             	|                                                                                                                   	|
| $V[W_2]$ 	| 0.0                	| 0.0                    	| 0.0                	| 0.0                    	| 0.0                                                           	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|
| $E[X_1]$   	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836      	| 0.0005941463981405022                                         	|                           	|                             	|                                                                                                                   	|
| $V[X_1]$ 	| 0.0                	| 0.0                    	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|
| $E[X_2]$   	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836      	| 0.0005941463981405022                                         	|                           	|                             	|                                                                                                                   	|
| $V[X_2]$ 	| 0.0                	| 0.0                    	|                    	|                        	|                                                               	| 0.0                       	| 0.0                         	| 0.04822073339236929                                                                                               	|

Como esperado, o tempo de espera e a sua variância foram nulos(com precisão de 4.8% pela $\chi^2$). O tempo total não foi exatamente igual a 1 por causa dos clientes que não tiveram sua amostra coletada por estarem fora da cor da rodada. Porém, com uma boa precisão(0.059% pela distribuição t), o valor real está contido no intervalo de confiança.

2) Chegadas e serviços exponenciais, fixando $E[Nq_1] = 1$:

Para que $E[Nq_1] = 1$, o valor de $\rho$ deve ser apropriado:

$E[Nq_1] = 1 = \lambda E[W_1]$

$\frac{\rho}{2} E[W_1] = 1$

$\rho = \frac{2}{E[W_1]}$

$\rho = \frac{2}{\frac{\rho_1}{1-\rho_1}}$

$\rho = \frac{2}{\frac{\frac{\rho}{2}}{1-\frac{\rho}{2}}}$

$\rho \frac{\frac{\rho}{2}}{1-\frac{\rho}{2}} = 2$

$\rho (- \frac{2}{\rho - 2} - 1) = 2$

$\rho = \sqrt{5} - 1 = 1.2360679774997896964091736687313$

Rodando a simulação com esse valor para $\rho$ e um número de rodadas e coletas por rodada razoável, obtive os seguintes valores:

###### Tabela 4

| ${1- \alpha}$ 	| $\rho$             	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------------------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 1.2360679774997898 	| 1.0   	| 200 	| 1000 	| 0   	| 100000 	|

| metric    	| $\hat{\mu}$        	| $\hat{\sigma}^2$     	| $t_{\alpha/2;n-1}$ 	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	|
|-----------	|--------------------	|----------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|
| $E[Nq_1]$ 	| 1.0223135198009698 	| 0.053628265261648156 	| 0.9900226891614518 	| 1.0546043504404878     	| 0.03158603502162882                                           	|

O valor alvo está dentro do IC, com precisão de 3%.

3) $V[W_1]$ para chegadas e serviços exponenciais

$V[W_1]$ é um dos valores que podem ser obtidos analiticamente(olhar seção **Obtenção dos valores analíticos**). Quero testar se o simulador converge para esses valores com uma signficância razoável no intervalo.

###### Tabela 5

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 200 	| 1000 	| 0   	| 100000 	|

| metric     	| $\hat{\mu}$         	| $\hat{\sigma}^2$      	| $t_{\alpha/2;n-1}$  	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|---------------------	|-----------------------	|---------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $V[W_1]$ 	| 0.23321915896621948 	| 0.0061345276204282035 	| 0.22229789496520694 	| 0.2345679012345679 	| 0.244140422967232      	| 0.046828331126065055                                          	| 0.005087400463141368      	| 0.007543717452937571        	| 0.1944655260220003                                                                                                	|

Mesmo com um número pequeno de amostras, o intervalo de confiança pela distribuição t já contém o valor analítico. Testando para as outras taxas de utilização:

###### Tabela 6

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.4    	| 1.0   	| 200 	| 1000 	| 0   	| 100000 	|

| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$     	| $t_{\alpha/2;n-1}$ 	| $\mu$  	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|----------------------	|--------------------	|--------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $V[W_1]$ 	| 0.5400784761128288 	| 0.023057594053774756 	| 0.5189051378014886 	| 0.5625 	| 0.5612518144241689     	| 0.0392041883685747                                            	| 0.019121800719826467      	| 0.028354257319990483        	| 0.1944655260220003                                                                                                	|

A partir de $\rho=0.4$, foi preciso aumentar o número de amostras por rodada para 2000:


###### Tabela 7

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.4    	| 1.0   	| 200 	| 2000 	| 0   	| 100000 	|

| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$     	| $t_{\alpha/2;n-1}$ 	| $\mu$  	| $t_{1 - \alpha/2;n-1}$ 	|   	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	| $pr(t)$ 	|
|------------	|--------------------	|----------------------	|--------------------	|--------	|------------------------	|---	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|---------------------------------------------------------------	|
| $V[W_1]$ 	| 0.5518384454432985 	| 0.013368070041296753 	| 0.53571652778966   	| 0.5625 	| 0.5679603630969371     	|   	| 0.011086220476525004      	| 0.016438909321527025        	| 0.1944655260220003                                                                                                	| 0.029214922930365227                                          	|

Para $\rho=0.6$:

###### Tabela 8

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.6    	| 1.0   	| 200 	| 2000 	| 0   	| 100000 	|


| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $V[W_1]$ 	| 1.0433874152391551 	| 0.05058689214110876 	| 1.0120255891760541 	| 1.0408163265306123 	| 1.0747492413022561     	| 0.030057700145743545                                          	| 0.04195201235227223       	| 0.06220743384771249         	| 0.1944655260220003                                                                                                	|

Para $\rho=0.8$:

###### Tabela 9

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.8    	| 1.0   	| 200 	| 2000 	| 0   	| 100000 	|


| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $V[W_1]$ 	| 1.7591048192846979 	| 0.15553337569379302 	| 1.7041134996799967 	| 1.7777777777777781 	| 1.814096138889399      	| 0.0312609680798113                                            	| 0.128984759136729         	| 0.1912616444709501          	| 0.1944655260220003                                                                                                	|

Para $\rho=0.9$:

###### Tabela 10

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$ 	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|-----	|------	|-----	|--------	|
| 0.95         	| 0.9    	| 1.0   	| 200 	| 2000 	| 0   	| 100000 	|


| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| $pr(t)$ 	| ${\chi^2}_{\alpha/2;n-1}$ 	| ${\chi^2}_{1-\alpha/2;n-1}$ 	| $pr({ \chi^2 })$ 	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|------------------------	|---------------------------------------------------------------	|---------------------------	|-----------------------------	|-------------------------------------------------------------------------------------------------------------------	|
| $V[W_1]$ 	| 2.3551656920552086 	| 0.40446563672113695 	| 2.266486208062589  	| 2.3057851239669422 	| 2.4438451760478284     	| 0.03765318265791922                                           	| 0.33542577275677016       	| 0.49737725080676537         	| 0.1944655260220003                                                                                                	|

De forma geral, as outras métricas também se mantiveram dentro dos intervalos de confiança. Os dados para esse teste estão na pasta `files/tests/correctness/3`.

## Obtenção dos melhores parâmetros de simulação

### Número de amostras por rodada

Utilizando como base $n = 3300$ rodadas de simulação(precisão de 5% para intervalos de confiança com a distribuição $\chi^2$), e iniciando com $k = 50$ amostras por rodada, foi aumentando-se o valor de $k$, com o objetivo de que:

- $W_2$, que é  métricas mais crítica, tivese baixa covariância entre as rodadas ;
- O valor analítico estivesse contido no intervalo de confiança de 95%, para todos os valores de $\rho$ ;
- Se possível, utilizar um único valor $k$ para para os todos os valores de $\rho$ especificados("one size fits all")

Com $k=50$:

###### Tabela 11

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$  	| $k$ 	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|------	|-----	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 3300 	| 50  	| 0   	| 100000 	|


| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$    	| $t_{\alpha/2;n-1}$ 	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| mean_cov            	| mean_cov_var       	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|------------------------	|---------------------	|--------------------	|
| $E[W_2]$   	| 0.5188093565987869 	| 0.09620391380100349 	| 0.5082229917569027 	| 0.5277777777777777 	| 0.5293957214406712     	| 0.08995108640195859 	| 0.1613545491714309 	|
| $V[W_2]$ 	| 1.3961475008876056 	| 3.786746159765684   	| 1.329729838885159  	|                    	| 1.4625651628900522     	| 0.08995108640195859 	| 0.1613545491714309 	|

Com $k=200$:

###### Tabela 12

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$  	| $k$ 	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|------	|-----	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 3300 	| 200 	| 0   	| 100000 	|


| metric      	| $\hat{\mu}$               	| $\hat{\sigma}^2$             	| $t_{\alpha/2;n-1}$            	| $\mu$    	| $t_{1 - \alpha/2;n-1}$            	| ${1- \alpha}$ 	| mean_cov             	| mean_cov_var         	|
|-------------	|--------------------	|----------------------	|--------------------	|--------------------	|--------------------	|------------	|----------------------	|----------------------	|
| $E[W_2]$ 	| 0.5259460939556508 	| 0.026158010670828586 	| 0.5204259189898711 	| 0.5277777777777777 	| 0.5314662689214306 	| 0.95       	| 0.025640044888092503 	| 0.023699462289277225 	|
| $V[W_2]$  	| 1.4724587117315704 	| 1.1375833428086584   	| 1.436055299049282  	|                    	| 1.5088621244138587 	| 0.95       	| 0.025640044888092503 	| 0.023699462289277225 	|

Com $k=500$:


###### Tabela 13

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$  	| $k$ 	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|------	|-----	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 3300 	| 500 	| 0   	| 100000 	|


| metric     	| $\hat{\mu}$        	| $\hat{\sigma}^2$     	| $t_{\alpha/2;n-1}$ 	| $\mu$              	| $t_{1 - \alpha/2;n-1}$ 	| mean_cov             	| mean_cov_var         	|
|------------	|--------------------	|----------------------	|--------------------	|--------------------	|------------------------	|----------------------	|----------------------	|
| $E[W_2]$   	| 0.5264975364581754 	| 0.009737571464964243 	| 0.5231295075075206 	| 0.5277777777777777 	| 0.5298655654088302     	| 0.009712947604901984 	| 0.007527052458936212 	|
| $V[W_2]$ 	| 1.4866630199215638 	| 0.41992724294746886  	| 1.4645454447395154 	|                    	| 1.5087805951036122     	| 0.009712947604901984 	| 0.007527052458936212 	|

Com $k=1000$:

###### Tabela 14

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$  	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|------	|------	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 3300 	| 1000 	| 0   	| 100000 	|


| metric      	| $\hat{\mu}$               	| $\hat{\sigma}^2$              	| $t_{\alpha/2;n-1}$            	| $\mu$    	| $t_{1 - \alpha/2;n-1}$            	| ${1- \alpha}$ 	| mean_cov             	| mean_cov_var         	|
|-------------	|--------------------	|-----------------------	|--------------------	|--------------------	|--------------------	|------------	|----------------------	|----------------------	|
| $E[W_2]$ 	| 0.5272496612129796 	| 0.0049782743101671805 	| 0.5248414759271138 	| 0.5277777777777777 	| 0.5296578464988453 	| 0.95       	| 0.004952935843448389 	| 0.003593132503179382 	|
| $V[W_2]$  	| 1.4892347387653133 	| 0.20285390144015686   	| 1.4738623213240816 	|                    	| 1.504607156206545  	| 0.95       	| 0.004952935843448389 	| 0.003593132503179382 	|

Com $k=2000$:

###### Tabela 15

| ${1- \alpha}$ 	| $\rho$ 	| $\mu$ 	| $n$  	| $k$  	| $t$ 	| $s$    	|
|--------------	|--------	|-------	|------	|------	|-----	|--------	|
| 0.95         	| 0.2    	| 1.0   	| 3300 	| 2000 	| 0   	| 100000 	|


| metric      	| $\hat{\mu}$               	| $\hat{\sigma}^2$              	| $t_{\alpha/2;n-1}$            	| $\mu$    	| $t_{1 - \alpha/2;n-1}$            	| ${1- \alpha}$ 	| mean_cov              	| mean_cov_var         	|
|-------------	|--------------------	|-----------------------	|--------------------	|--------------------	|--------------------	|------------	|-----------------------	|----------------------	|
| $E[W_2]$ 	| 0.5274856548276599 	| 0.0024898840167682495 	| 0.5257825552329782 	| 0.5277777777777777 	| 0.5291887544223415 	| 0.95       	| 0.0024778216942935557 	| 0.001728231254712837 	|
| $V[W_2]$  	| 1.4923618888673191 	| 0.09904385299896964   	| 1.4816204057457254 	|                    	| 1.5031033719889129 	| 0.95       	| 0.0024778216942935557 	| 0.001728231254712837 	|

Aqui a simulação já fica significativamente mais lenta, levando 276 segundos, contra 157 segundos com $k=1000$, para as mesmas 3300 rodadas. A relação entre a autocovariância e a variância já é baixa o suficiente para $k=1000$(0,35%). Realizei um último teste, com a maior taxa de utilização especificada, para confirmar se o $k=1000$ atende todos os critérios necessários:

###### Tabela 16

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9            	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric      	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$   	| $t_{1 - \alpha/2;n-1}$            	| ${1- \alpha}$ 	| mean_cov           	| mean_cov_var       	|
|-------------	|--------------------	|--------------------	|--------------------	|-------------------	|--------------------	|------------	|--------------------	|--------------------	|
| $E[W_2]$ 	| 24.732225893701486 	| 193.66961231002122 	| 24.257239435090884 	| 25.36363636363637 	| 25.207212352312087 	| 0.95       	| 176.13210137618066 	| 0.5924679584969877 	|
| $V[W_2]$  	| 568.7950124906531  	| 426787.6816180937  	| 546.4974995394372  	|                   	| 591.092525441869   	| 0.95       	| 176.13210137618066 	| 0.5924679584969877 	|

Será necessário um valor maior de $k$ para essa taxa de utilização!

###### Tabela 17

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9            	| exponential     	| exponential     	| 1.0          	| 3300             	| 5000              	| 0                           	| 100000 	|

| metric      	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$   	| $t_{1 - \alpha/2;n-1}$            	| ${1- \alpha}$ 	| mean_cov          	| mean_cov_var        	|
|-------------	|-------------------	|--------------------	|--------------------	|-------------------	|--------------------	|------------	|-------------------	|---------------------	|
| $E[W_2]$ 	| 25.19073470689688 	| 41.772294326007554 	| 24.970140221396115 	| 25.36363636363637 	| 25.411329192397645 	| 0.95       	| 40.83508451218092 	| 0.07509593846468973 	|
| $V[W_2]$  	| 736.3220614355928 	| 282519.78562533064 	| 718.1804892612905  	|                   	| 754.463633609895   	| 0.95       	| 40.83508451218092 	| 0.07509593846468973 	|


Foi obtido uma razão de 7.5%, o que é razoável tendo em vista a taxa de utilização e o tempo da simulação.

Com os valores obtidos, foi criado o seguinte mapeamento entre a taxa de utilização e o número de amostras por rodada, a ser utilizado nas análises do simulador nas seções adiante:

`
samples_per_round_rho = {
        0.2: 1000,
        0.4: 1000,
        0.6: 1000,
        0.8: 1000,
        0.9: 5000
    }
`

Os testes para essa seção estão na pasta `files/tests/nsamples`.

### Determinando a fase transiente

Para que o simulador colete as métricas com qualidade, o sistema deve primeiro ter entrado em equilíbrio para que então realize-se a amostragem. Dentre as métricas, a mais crítica e a que não possui valores bem determinados analiticamente é $V[W_2]$, a variância do tempo de espera na fila 2. Para ter uma valor de referência para essa métrica, realizei execuções da simulador com um número de rodadas bem elevado: Eis os resultados obtidos:

Com $\rho = 0.2$


$n=250$, $k=1000$:

###### Tabela 18

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 250            	| 1000                	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|---------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 1.507307311682581 	| 0.3060421522680684 	| 1.4383969175010178 	|                 	| 1.5762177058641442 	| 0.045717547873259996 	| 0.25867034356285545 	| 0.3678078865871109 	| 0.17420803752131986 	| 0.95       	|



$n=375$, $k=1000$:

###### Tabela 19

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 375            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$            	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|--------------------	|---------------------	|--------------------	|-----------------	|--------------------	|---------------------	|---------------------	|--------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 1.5028552119831318 	| 0.26232429089708953 	| 1.4508484993102133 	|                 	| 1.5548619246560502 	| 0.03460527152465446 	| 0.22844128052695511 	| 0.3043899286750083 	| 0.1425379122626913 	| 0.95       	|




$n=500$, $k=1000$:

###### Tabela 20


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|---------------------	|---------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 1.501001831728403 	| 0.2512124187933888 	| 1.4569627461929933 	|                 	| 1.5450409172638129 	| 0.029339794665472728 	| 0.22273869336631497 	| 0.28554797647172175 	| 0.12357058886753942 	| 0.95       	|





$n=1000$, $k=1000$:


###### Tabela 21

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 1000            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|---------------------	|---------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 1.4963616725098399 	| 0.2330798577317204 	| 1.4664026974067792 	|                 	| 1.5263206476129005 	| 0.020021212554054993 	| 0.21391781747159536 	| 0.25495075370208303 	| 0.0875147935972195 	| 0.95       	|






$n=1500$, $k=1000$:

###### Tabela 22

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 1500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$            	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|--------------------	|---------------------	|--------------------	|-----------------	|--------------------	|----------------------	|---------------------	|---------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 1.4939057805187077 	| 0.22273787571089557 	| 1.4700028964436367 	|                 	| 1.5178086645937787 	| 0.016000262122803664 	| 0.20761386056847067 	| 0.23958544346978586 	| 0.07149291739188425 	| 0.95       	|



Como a variância para $\rho = 2$ converge para 1.49, com $t = k \times n = 1000 \times 1000 = 1000000$ é um número razoável de chegadas para desconsiderar na fase transiente.

Realizando esse procedimento para as demais taxas de utilização:

Com $\rho = 0.4$

$n=500$, $k=1000$:

###### Tabela 23

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 6.118931786215855 	| 3.9957704386605015 	| 5.943293979755738 	|                 	| 6.294569592675972 	| 0.028703998115451723 	| 3.542868982249575 	| 4.541909865305822 	| 0.12357058886753942 	| 0.95       	|





$n=1000$, $k=1000$:


###### Tabela 24

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 1000            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$          	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$          	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|------------------	|-----------------	|------------------	|----------------------	|-------------------	|--------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 6.155599276867935 	| 3.9920599461503836 	| 6.03161314615998 	|                 	| 6.27958540757589 	| 0.020142008134590786 	| 3.663863360853791 	| 4.3666522796080525 	| 0.0875147935972195 	| 0.95       	|






$n=1500$, $k=1000$:


###### Tabela 25

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 1500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 6.213807623089972 	| 4.303488038040681 	| 6.108741291609895 	|                 	| 6.318873954570049 	| 0.016908526599642298 	| 4.011279009626264 	| 4.628997590868464 	| 0.07149291739188425 	| 0.95       	|




$n=2500$, $k=1000$:


###### Tabela 26

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 2500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$            	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-----------------	|-------------------	|--------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 6.2456774286608 	| 4.562690677928951 	| 6.1619054071500186 	|                 	| 6.329449450171581 	| 0.013412799887224332 	| 4.319906192761265 	| 4.826637108443365 	| 0.05540135753966874 	| 0.95       	|



$n=5000$, $k=1000$:

###### Tabela 27

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 5000            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 6.300643912637873 	| 5.1892434085449874 	| 6.2374870898007835 	|                 	| 6.363800735474962 	| 0.010023867990763484 	| 4.991669389022246 	| 5.398842105731972 	| 0.03918697524325843 	| 0.95       	|

Aumentando o número de rodadas, o valor da variância vai se aproximando de 6.30, com o valor real podendo ser ainda maior. Com $t = k \times n = 1000 \times 1000 = 1000000$, o simulador consegue uma inicialização a partir de um valor próximo ao valor real da métrica.

Com $\rho = 0.6$

$n=500$, $k=1000$:

###### Tabela 28

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$             	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|------------------	|-------------------	|--------------------	|-----------------	|--------------------	|---------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 26.1790102756033 	| 171.2924105928418 	| 25.029039508771675 	|                 	| 27.328981042434926 	| 0.04392720560193613 	| 151.87723561706338 	| 194.70455109139104 	| 0.12357058886753942 	| 0.95       	|



$n=1000$, $k=1000$:

###### Tabela 29

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 1000            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$         	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|--------------------	|------------------	|-------------------	|-----------------	|--------------------	|---------------------	|--------------------	|--------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 25.508346149605558 	| 165.732894023483 	| 24.70947095393951 	|                 	| 26.307221345271607 	| 0.03131818860308207 	| 152.10760516922085 	| 181.28433171239246 	| 0.0875147935972195 	| 0.95       	|



$n=1500$, $k=1000$:

###### Tabela 30

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 1500            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|--------------------	|-------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 25.776174545154525 	| 188.1569990011762 	| 25.081448697439647 	|                 	| 26.470900392869403 	| 0.026952247956649363 	| 175.38104299026134 	| 202.38891972801423 	| 0.07149291739188425 	| 0.95       	|


$n=2500$, $k=1000$:

###### Tabela 31

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 2500            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 25.77697296649876 	| 207.06461190087387 	| 25.212632200545137 	|                 	| 26.341313732452384 	| 0.021893213244513685 	| 196.04653534355197 	| 219.0430625684734 	| 0.05540135753966874 	| 0.95       	|



$n=5000$, $k=1000$:

###### Tabela 32

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 5000            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$       	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 25.343549183904084 	| 182.80791995767316 	| 24.968692070386922 	|                 	| 25.718406297421247 	| 0.014791026734141715 	| 175.847734685355 	| 190.19171347861234 	| 0.03918697524325843 	| 0.95       	|




$n=7500$, $k=1000$:

###### Tabela 33

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 7500            	| 1000                	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 25.472091615271292 	| 191.09994563964324 	| 25.159182767635507 	|                 	| 25.785000462907078 	| 0.012284379797385265 	| 185.12771342228996 	| 197.36731714379536 	| 0.03199937971322402 	| 0.95       	|

$V[W_2]$ está se aproximando de 25; Então, novamente $t = 1000000$ é a melhor escolha.

Com $\rho = 0.8$

$n=500$, $k=1000$:

###### Tabela 34

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8            	| exponential     	| exponential     	| 1.0          	| 500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$       	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|--------------------	|-----------------	|--------------------	|-------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 157.3283175029853 	| 19000.84143792785 	| 145.21664395200438 	|                 	| 169.43999105396622 	| 0.076983430212753 	| 16847.186994467025 	| 21597.864667362242 	| 0.12357058886753942 	| 0.95       	|






$n=1000$, $k=1000$:


###### Tabela 35

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 1000            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|--------------------	|-------------------	|-------------------	|-----------------	|--------------------	|---------------------	|-------------------	|--------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 148.81978718966923 	| 8528.780389918495 	| 130.4952665955566 	|                 	| 167.14430778378187 	| 0.12313228596919193 	| 6574.802862955274 	| 11509.498720579792 	| 0.2728717962830997 	| 0.95       	|



$n=1500$, $k=1000$:

###### Tabela 36


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 1500            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$             	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|------------------	|--------------------	|--------------------	|-----------------	|--------------------	|---------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 151.884103908869 	| 15287.066827117651 	| 145.62207092880297 	|                 	| 158.14613688893505 	| 0.04122902146378188 	| 14249.067207885046 	| 16443.358245371266 	| 0.07149291739188425 	| 0.95       	|



$n=2500$, $k=1000$:

###### Tabela 37

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 2500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|-------------------	|-----------------	|-------------------	|---------------------	|-------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 153.7155343173541 	| 19447.68767856399 	| 148.2463511615394 	|                 	| 159.1847174731688 	| 0.03557989880530409 	| 18412.86038606708 	| 20572.714139232612 	| 0.05540135753966874 	| 0.95       	|




$n=5000$, $k=1000$:

###### Tabela 38

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 5000            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 152.5555100759755 	| 17871.354345189004 	| 148.84915531707802 	|                 	| 156.26186483487297 	| 0.024295122195531524 	| 17190.924649700075 	| 18593.196103767998 	| 0.03918697524325843 	| 0.95       	|



$n=7500$, $k=1000$:

###### Tabela 39

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 7500            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|--------------------	|--------------------	|-------------------	|-----------------	|--------------------	|----------------------	|--------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 152.77174298574312 	| 17772.693613685595 	| 149.7541254939989 	|                 	| 155.78936047748732 	| 0.019752458358911453 	| 17217.263558310515 	| 18355.57223844713 	| 0.03199937971322402 	| 0.95       	|

$V[W_2] \rightarrow 152$, então o simulador pode partir de $t = 5000000$

Com $\rho = 0.9$


$n=500$, $k=1000$:

###### Tabela 40

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9            	| exponential     	| exponential     	| 1.0          	| 500            	| 1000                	| 0                           	| 100000 	|




| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 723.1048658740433 	| 249872.68465741078 	| 679.1833691518525 	|                 	| 767.0263625962341 	| 0.060740148206721356 	| 221550.8116829997 	| 284025.1283045169 	| 0.12357058886753942 	| 0.95       	|




$n=1000$, $k=1000$:

###### Tabela 41


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 1000            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$     	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|---------------------	|-------------------	|--------------------	|--------------------	|------------	|
| $V[W_2]$ 	| 734.6962574233289 	| 313078.60962166503 	| 699.9745336206397 	|                 	| 769.4179812260181 	| 0.04725997097693495 	| 287339.6848576919 	| 342456.13614076306 	| 0.0875147935972195 	| 0.95       	|



$n=1500$, $k=1000$:

###### Tabela 42


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 1500            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|----------------------	|--------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 728.3074340601064 	| 274060.41462002636 	| 701.7933625210934 	|                 	| 754.8215055991194 	| 0.036405054100854914 	| 255451.57296063827 	| 294789.94429971796 	| 0.07149291739188425 	| 0.95       	|





$n=2500$, $k=1000$:

###### Tabela 43


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9             	| exponential     	| exponential     	| 1.0          	| 2500            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|---------------------	|-------------------	|-------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 735.0586904842246 	| 276086.92017848475 	| 714.4518505362299 	|                 	| 755.6655304322193 	| 0.02803427837091453 	| 261396.1104110581 	| 292058.2323354391 	| 0.05540135753966874 	| 0.95       	|



$n=5000$, $k=1000$:

###### Tabela 44


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 5000            	| 1000                	| 0                           	| 100000 	|



| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$          	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$       	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|-------------------	|-----------------	|------------------	|----------------------	|-------------------	|------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 746.2794301408759 	| 365976.9011273024 	| 729.5070347889388 	|                 	| 763.051825492813 	| 0.022474685318300967 	| 352042.7836239432 	| 380759.071790274 	| 0.03918697524325843 	| 0.95       	|



$n=7500$, $k=1000$:

###### Tabela 45

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 7500            	| 1000                	| 0                           	| 100000 	|




| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$         	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	| ${1- \alpha}$ 	|
|------------	|-------------------	|------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|--------------------	|---------------------	|------------	|
| $V[W_2]$ 	| 744.8111420045384 	| 370575.028388694 	| 731.0318901961971 	|                 	| 758.5903938128797 	| 0.018500329857118764 	| 358993.8627526612 	| 382728.51888446446 	| 0.03199937971322402 	| 0.95       	|



$n=10000$, $k=1000$:

###### Tabela 46


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 10000            	| 1000                	| 0                           	| 100000 	|


| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$          	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$       	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|------------------	|-----------------	|-------------------	|---------------------	|--------------------	|--------------------	|----------------------	|------------	|
| $V[W_2]$ 	| 747.3857470297525 	| 372246.8718398691 	| 735.426159731805 	|                 	| 759.3453343276999 	| 0.01600189372820793 	| 362140.11244431476 	| 382784.75597652484 	| 0.027713725782808826 	| 0.95       	|







$n=12500$, $k=1000$:

###### Tabela 47


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9              	| exponential     	| exponential     	| 1.0          	| 12500            	| 1000                	| 0                           	| 100000 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$       	| ${1- \alpha}$ 	|
|------------	|-------------------	|-------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|--------------------	|----------------------	|------------	|
| $V[W_2]$ 	| 747.1079948112645 	| 363110.3211755632 	| 736.5433612238578 	|                 	| 757.6726283986711 	| 0.014140704771972818 	| 354273.3273623051 	| 372283.72349808924 	| 0.024788688120851787 	| 0.95       	|

$V[W_2] \rightarrow 747$, porém utilizarei $t = 7500000$ para tentar obter um menor tempo de simulação. 

Ao final, tenho obtive esse mapeamento para o tamanho da fase transiente para cada taxa de utilização:

`
arrivals_until_steady_state_rho = {
        0.2: 1000000,
        0.4: 1000000,
        0.6: 1000000,
        0.8: 5000000,
        0.9: 7500000
    }
`

E os valores de referência para $V[W_2]$:

$\rho = 0.2 : V[W_2] \rightarrow 1.49$

$\rho = 0.4 : V[W_2] \rightarrow 6.30$

$\rho = 0.6 : V[W_2] \rightarrow 25$

$\rho = 0.8 : V[W_2] \rightarrow 152$

$\rho = 0.9 : V[W_2] \rightarrow 747$


## Análise dos resultados

### Obtenção dos valores analíticos

Para realizar a comparação com os valores obtidos no simulador, primeiro deduziu-se os valores analíticos para as variáveis interessadas:

Da fila 1:

$E[W_1] = {\rho_1 E[X_{1r}] \over {1-\rho_1}} = {\rho_1 \over {({1-\rho_1}) \mu}}$

$E[Nq_1] = {\lambda E[W_1]} = {\lambda \rho_1 \over {({1-\rho_1}) \mu}}$

$E[T_1] = {E[W_1] + E[X_1]} = {E[W_1] + E[X]} = {{\rho_1 \over {({1-\rho_1}) \mu}} + {1 \over \mu}}$

$E[N_1] = {\lambda E[T_1]} = {\lambda ({{\rho_1 \over {({1-\rho_1}) \mu}} + {1 \over \mu}})}$

A variância de $W_1$(extraída da página 92 da apostila):

$V[W_{1}] = {E[W_{1}^2] - (E[W_{1}])^2}$

Com $E[W_1^2] = { 2(E[W_1])^2 + \frac{\lambda E[X^3]}{3(1 - \rho_1)}}$ e $E[X^3] = - ({{({-1})^3 \frac{d}{ds^3} {E[e^{-sX}]}}(0)}) = {\frac{6}{\mu^3}}$ , obtenho $V[W_1] = {E[W_1]^2 + \frac{\lambda}{3({1-\rho_1})} \frac{6}{\mu^3}}$:

Da fila 2:

$E[T_2] = {\frac{\rho(1-\rho_1)E[W_1] + \rho_2E[X] + \rho_1(1-\rho)E[X] + (1-\rho_2)E[X]}{(1-\rho_1)(1-\rho)}}$

Observação: O valor de $E[T_2]$ foi obtido da página 111 da apostila. A fórmula apresentada no slide 17 é diferente, e apresentava resultados discrepantes em relação com a fórmula da apostila e os resultados simulados.

Exemplos:

Com a fórmula dos slides:

###### Tabela 48


| metric       	| $\mu$   	|
|--------------	|----------------------	|
| $E[T_2]$  	| 1.3888888888888888   	|

Com a fórmula da página 111:

###### Tabela 49


| metric       	| $\mu$   	|
|--------------	|----------------------	|
| $E[T_2]$  	| 1.5277777777777777   	|

$E[W_2] = E[T_2] - E[X_2] = E[T_2] - E[X] = E[T_2] - {\frac{1}{\mu}}$

$E[N_2] = {\lambda E[T_2]}$

$E[Nq_2] = \lambda E[W_2] = \lambda (E[T_2] - E[X_2]) = \lambda (E[T_2] - {\frac{1}{\mu}})$

Tenho então os valores obtidos analiticamente:

###### Tabela 50

| rho 	|  mu  	|  E_W1                	|  Var_W1             	|  E_NQ1                 	|  E_T1               	|  E_N1                	|  E_W2                	|  E_NQ2                	|  E_T2               	|  E_N2               	|
|-----	|------	|----------------------	|---------------------	|------------------------	|---------------------	|----------------------	|----------------------	|-----------------------	|---------------------	|---------------------	|
| 0.2 	| 1    	|  0.11111111111111112 	|  0.2345679012345679 	|   0.011111111111111113 	|  1.1111111111111112 	|  0.11111111111111112 	|   0.5277777777777777 	|   0.05277777777777777 	|  1.5277777777777777 	|  0.1527777777777778 	|
| 0.4 	| 1    	|  0.25                	|  0.5625             	|   0.05                 	|  1.25               	|  0.25                	|   1.5000000000000004 	|   0.3000000000000001  	|  2.5000000000000004 	|  0.5000000000000001 	|
| 0.6 	| 1    	|  0.4285714285714286  	|  1.0408163265306123 	|   0.1285714285714286   	|  1.4285714285714286 	|  0.42857142857142855 	|   3.6428571428571423 	|   1.0928571428571427  	|  4.642857142857142  	|  1.3928571428571426 	|
| 0.8 	| 1    	|  0.6666666666666667  	|  1.7777777777777781 	|   0.2666666666666667   	|  1.6666666666666667 	|  0.6666666666666667  	|   10.66666666666667  	|   4.266666666666668   	|  11.66666666666667  	|  4.666666666666668  	|
| 0.9 	| 1    	|  0.8181818181818181  	|  2.3057851239669422 	|   0.36818181818181817  	|  1.8181818181818181 	|  0.8181818181818181  	|   25.36363636363637  	|   11.413636363636368  	|  26.36363636363637  	|  11.863636363636367 	|

O arquivo com as funções para geração dos valores acima é o `utils/analitical_values.py`.

### Comparação com valores analíticos

Tendo os valores analíticos, executei o simulador com as taxas de utilização especificadas e com os parâmetros do número de rodadas, quantidade de amostras por rodada e tamanho da fase transiente obtidos nas seções anteriores:

Com $\rho = 0.2$:

###### Tabela 51

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 1000000                     	| 100000 	|


| metric       	| $\hat{\mu}$                 	| $\hat{\sigma}^2$               	| $t_{\alpha/2;n-1}$              	| $\mu$      	| $t_{1 - \alpha/2;n-1}$              	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$           	| ${\chi^2}_{1-\alpha/2;n-1}$           	| $pr({ \chi^2 })$      	|
|--------------	|----------------------	|------------------------	|----------------------	|----------------------	|----------------------	|-----------------------	|----------------------	|----------------------	|---------------------	|
| $E[N_1]$  	| 0.11111385586814172  	| 3.394435442405805e-05  	| 0.11091500189916326  	| 0.11111111111111112  	| 0.11131270983712019  	| 0.0017896415116260948 	|                      	|                      	|                     	|
| $E[N_2]$  	| 0.15305478606950135  	| 0.00011822098783625486 	| 0.15268368023797294  	| 0.1527777777777778   	| 0.15342589190102976  	| 0.0024246600910597764 	|                      	|                      	|                     	|
| $E[Nq_1]$ 	| 0.011106630772771598 	| 4.2376797118511435e-06 	| 0.011036369736395303 	| 0.011111111111111113 	| 0.011176891809147892 	| 0.006326044127490279  	|                      	|                      	|                     	|
| $E[Nq_2]$ 	| 0.05287451148130004  	| 6.045617621878595e-05  	| 0.052609129871331    	| 0.05277777777777777  	| 0.05313989309126908  	| 0.005019083912726116  	|                      	|                      	|                     	|
| $E[T_1]$  	| 1.1098586447303318   	| 0.001834989638044129   	| 1.1083965776624964   	| 1.1111111111111112   	| 1.1113207117981672   	| 0.0013173452986804577 	|                      	|                      	|                     	|
| $E[T_2]$  	| 1.5279266508728657   	| 0.007101954927434553   	| 1.525050316026162    	| 1.5277777777777777   	| 1.5308029857195695   	| 0.0018825084601153078 	|                      	|                      	|                     	|
| $E[W_1]$  	| 0.11077689812802899  	| 0.00037731025493030885 	| 0.1101139190987331   	| 0.11111111111111112  	| 0.11143987715732488  	| 0.005984813083768232  	|                      	|                      	|                     	|
| $V[W_1]$   	| 0.23392398648584675  	| 0.005670604307950095   	| 0.2313537969052475   	| 0.2345679012345679   	| 0.23649417606644602  	| 0.010987285310968984  	| 0.005406600519628728 	| 0.005954525257882207 	| 0.04822803206158341 	|
| $E[W_2]$  	| 0.5271238427696624   	| 0.004930775980247694   	| 0.5247271734149517   	| 0.5277777777777777   	| 0.5295205121243731   	| 0.004546691233160447  	|                      	|                      	|                     	|
| $V[W_2]$   	| 1.4875210880946588   	| 0.19713820105230626    	| 1.472366788058283    	|         **1.49             	| 1.5026753881310346   	| 0.010187620301764493  	| 0.187960126005225    	| 0.2070086949663688   	| 0.04822803206158341 	|

Todos os valores dentro dos respectivos ICs.

Com $\rho = 0.4$:

###### Tabela 52

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 1000000                     	| 100000 	|


| metric       	| $\hat{\mu}$                	| $\hat{\sigma}^2$               	| $t_{\alpha/2;n-1}$             	| $\mu$    	| $t_{1 - \alpha/2;n-1}$             	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$           	| ${\chi^2}_{1-\alpha/2;n-1}$           	| $pr({ \chi^2 })$      	|
|--------------	|---------------------	|------------------------	|---------------------	|--------------------	|---------------------	|-----------------------	|----------------------	|----------------------	|---------------------	|
| $E[N_1]$  	| 0.2502316577792978  	| 0.00023007190018756933 	| 0.24971395287802334 	| 0.25               	| 0.25074936268057224 	| 0.002068902495666908  	|                      	|                      	|                     	|
| $E[N_2]$  	| 0.5011100309181759  	| 0.002773075950575948   	| 0.4993126862439397  	| 0.5000000000000001 	| 0.502907375592412   	| 0.0035867265936443643 	|                      	|                      	|                     	|
| $E[Nq_1]$ 	| 0.05002915887894833 	| 6.358445990641023e-05  	| 0.04975699782363904 	| 0.05               	| 0.05030131993425761 	| 0.005440048591818409  	|                      	|                      	|                     	|
| $E[Nq_2]$ 	| 0.30086087579048876 	| 0.002184583620958604   	| 0.2992656034932583  	| 0.3000000000000001 	| 0.3024561480877192  	| 0.005302358749834063  	|                      	|                      	|                     	|
| $E[T_1]$  	| 1.2490473270885951  	| 0.003367849073735964   	| 1.2470665901656803  	| 1.25               	| 1.25102806401151    	| 0.0015857981358733527 	|                      	|                      	|                     	|
| $E[T_2]$  	| 2.4977042810101833  	| 0.048758058383054116   	| 2.490167711857282   	| 2.5000000000000004 	| 2.5052408501630845  	| 0.0030173985007757964 	|                      	|                      	|                     	|
| $E[W_1]$  	| 0.24928736489113465 	| 0.0013500307074397616  	| 0.24803329335592503 	| 0.25               	| 0.25054143642634424 	| 0.005030626144077823  	|                      	|                      	|                     	|
| $V[W_1]$   	| 0.5586537554493778  	| 0.026500879072746314   	| 0.5530975201778499  	| 0.5625             	| 0.5642099907209057  	| 0.009945758383130485  	| 0.025267089499518162 	| 0.027827749076675422 	| 0.04822803206158341 	|
| $E[W_2]$  	| 1.497701293496728   	| 0.04363146421443235    	| 1.4905719361962777  	| 1.5000000000000004 	| 1.5048306507971783  	| 0.004760199735025381  	|                      	|                      	|                     	|
| $V[W_2]$   	| 6.315013506857641   	| 5.226069984599711      	| 6.236987730689815   	| **6.30                   	| 6.393039283025466   	| 0.012355599252969914  	| 4.982762181931732    	| 5.487733587605654    	| 0.04822803206158341 	|

Todos os valores dentro dos respectivos ICs.

Com $\rho = 0.6$:

###### Tabela 53


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 1000000                     	| 100000 	|


| metric       	| $\hat{\mu}$                	| $\hat{\sigma}^2$               	| $t_{\alpha/2;n-1}$             	| $\mu$     	| $t_{1 - \alpha/2;n-1}$             	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|--------------	|---------------------	|------------------------	|---------------------	|---------------------	|---------------------	|-----------------------	|---------------------	|--------------------	|---------------------	|
| $E[N_1]$  	| 0.4289960151931458  	| 0.0009415850330882953  	| 0.4279486931116292  	| 0.42857142857142855 	| 0.4300433372746624  	| 0.0024413328898756042 	|                     	|                    	|                     	|
| $E[N_2]$  	| 1.3974744928766953  	| 0.05300469028094872    	| 1.3896165722531018  	| 1.3928571428571426  	| 1.405332413500289   	| 0.0056229438631242535 	|                     	|                    	|                     	|
| $E[Nq_1]$ 	| 0.1288432680194267  	| 0.00040303516620919945 	| 0.12815806075652367 	| 0.1285714285714286  	| 0.12952847528232972 	| 0.005318145631013579  	|                     	|                    	|                     	|
| $E[Nq_2]$ 	| 1.0969698618858614  	| 0.04942219958760339    	| 1.0893821379420026  	| 1.0928571428571427  	| 1.1045575858297203  	| 0.006916984875787198  	|                     	|                    	|                     	|
| $E[T_1]$  	| 1.4267800861792381  	| 0.00683220839408703    	| 1.4239589046017096  	| 1.4285714285714286  	| 1.4296012677567667  	| 0.0019773065273732977 	|                     	|                    	|                     	|
| $E[T_2]$  	| 4.6317981201956675  	| 0.465660097219863      	| 4.6085072883895535  	| 4.642857142857142   	| 4.6550889520017815  	| 0.005028464367771281  	|                     	|                    	|                     	|
| $E[W_1]$  	| 0.42767912145068515 	| 0.0037855411192107918  	| 0.4255791447759863  	| 0.4285714285714286  	| 0.429779098125384   	| 0.004910168790975197  	|                     	|                    	|                     	|
| $V[W_1]$   	| 1.0364170489144606  	| 0.1021256500373346     	| 1.0255097327031377  	| 1.0408163265306123  	| 1.0473243651257835  	| 0.010524060968262899  	| 0.09737103182903556 	| 0.1072389695349379 	| 0.04822803206158341 	|
| $E[W_2]$  	| 3.631496097034844   	| 0.45376176973723314    	| 3.6085047488562583  	| 3.6428571428571423  	| 3.6544874452134297  	| 0.006331095384450095  	|                     	|                    	|                     	|
| $V[W_2]$   	| 25.344478653701888  	| 196.98122568144532     	| 24.865448441928194  	|      **25               	| 25.82350886547558   	| 0.018900771971639134  	| 187.81045886649065  	| 206.84386001053414 	| 0.04822803206158341 	|

Todos os valores dentro dos respectivos ICs.

Com $\rho = 0.8$:

###### Tabela 54


| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 5000000                     	| 100000 	|


| metric       	| $\hat{\mu}$                	| $\hat{\sigma}^2$              	| $t_{\alpha/2;n-1}$             	| $\mu$    	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$      	|
|--------------	|---------------------	|-----------------------	|---------------------	|--------------------	|--------------------	|-----------------------	|---------------------	|---------------------	|---------------------	|
| $E[N_1]$  	| 0.6682160355009901  	| 0.0035490136359533127 	| 0.666182722109681   	| 0.6666666666666667 	| 0.6702493488922991 	| 0.0030428982294396297 	|                     	|                     	|                     	|
| $E[N_2]$  	| 4.738442236350634   	| 2.510375982224474     	| 4.684364329608454   	| 4.666666666666668  	| 4.792520143092815  	| 0.011412591743194655  	|                     	|                     	|                     	|
| $E[Nq_1]$ 	| 0.26773643106427036 	| 0.0020450557866095705 	| 0.26619294374199814 	| 0.2666666666666667 	| 0.2692799183865426 	| 0.0057649506872739145 	|                     	|                     	|                     	|
| $E[Nq_2]$ 	| 4.337950192555727   	| 2.4760291883608696    	| 4.284243505061282   	| 4.266666666666668  	| 4.3916568800501725 	| 0.012380660245156837  	|                     	|                     	|                     	|
| $E[T_1]$  	| 1.664020073430284   	| 0.015308425864963634  	| 1.6597971252271613  	| 1.6666666666666667 	| 1.6682430216334065 	| 0.002537798834612128  	|                     	|                     	|                     	|
| $E[T_2]$  	| 11.690222147049623  	| 13.337780957409416    	| 11.56557214863023   	| 11.66666666666667  	| 11.814872145469016 	| 0.01066275703330861   	|                     	|                     	|                     	|
| $E[W_1]$  	| 0.6646929921000729  	| 0.010629703676546583  	| 0.6611740585502958  	| 0.6666666666666667 	| 0.6682119256498501 	| 0.005294073491972906  	|                     	|                     	|                     	|
| $V[W_1]$   	| 1.7603729171034022  	| 0.3493852296744516    	| 1.740198418152757   	| 1.7777777777777781 	| 1.7805474160540473 	| 0.011460355220552453  	| 0.33311905781543677 	| 0.36687856564260335 	| 0.04822803206158341 	|
| $E[W_2]$  	| 10.690808580952668  	| 13.27178260758967     	| 10.566467363145609  	| 10.66666666666667  	| 10.815149798759727 	| 0.011630665432415662  	|                     	|                     	|                     	|
| $V[W_2]$   	| 156.8669310917295   	| 21010.950852118665    	| 151.91957306331963  	|   **152                 	| 161.81428912013936 	| 0.031538565802099204  	| 20032.753411430265  	| 22062.9461600168    	| 0.04822803206158341 	|

A exceção de $E[Nq_2]$, os valores analíticos, quando o valor referência para $V[W_2]$ estão dentro do intervalo de confiança obtidos.

Se executar mais uma vez a simulação, aumentando o número de coletas por rodada, consigo obter o valor de $E[Nq_2]$ dentro do IC obtido:

###### Tabela 55

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 3300             	| 5000              	| 5000000                     	| 100000 	|


| metric       	| $\hat{\mu}$                	| $\hat{\sigma}^2$              	| $t_{\alpha/2;n-1}$            	| $\mu$    	| $t_{1 - \alpha/2;n-1}$             	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$      	|
|--------------	|---------------------	|-----------------------	|--------------------	|--------------------	|---------------------	|-----------------------	|---------------------	|---------------------	|---------------------	|
| $E[N_1]$  	| 0.6671008098123893  	| 0.0006916075116141041 	| 0.6662032149922558 	| 0.6666666666666667 	| 0.6679984046325228  	| 0.0013455160103702333 	|                     	|                     	|                     	|
| $E[N_2]$  	| 4.677657964511077   	| 0.47057066709579337   	| 4.654244649251222  	| 4.666666666666668  	| 4.701071279770932   	| 0.005005349992985789  	|                     	|                     	|                     	|
| $E[Nq_1]$ 	| 0.26699063795972333 	| 0.0004000243225777419 	| 0.2663079948891346 	| 0.2666666666666667 	| 0.26767328103031207 	| 0.002556805271545589  	|                     	|                     	|                     	|
| $E[Nq_2]$ 	| 4.277687071159835   	| 0.46386913956549497   	| 4.254441071494866  	| 4.266666666666668  	| 4.3009330708248035  	| 0.0054342450203272614 	|                     	|                     	|                     	|
| $E[T_1]$  	| 1.6666803400487724  	| 0.0030441664972305155 	| 1.6647971910316925 	| 1.6666666666666667 	| 1.6685634890658523  	| 0.0011298801406781451 	|                     	|                     	|                     	|
| $E[T_2]$  	| 11.665350667460888  	| 2.6114065991712834    	| 11.610195305941895 	| 11.66666666666667  	| 11.720506028979882  	| 0.004728135749304307  	|                     	|                     	|                     	|
| $E[W_1]$  	| 0.6666913651556826  	| 0.002117639255000446  	| 0.6651207257964995 	| 0.6666666666666667 	| 0.6682620045148657  	| 0.002355871759065456  	|                     	|                     	|                     	|
| $V[W_1]$   	| 1.7789735670271807  	| 0.07544345548218692   	| 1.769598782968877  	| 1.7777777777777781 	| 1.7883483510854843  	| 0.0052697714187904775 	| 0.07193106827092834 	| 0.07922082670814833 	| 0.04822803206158341 	|
| $E[W_2]$  	| 10.66570862644188   	| 2.598002074890685     	| 10.610695005122425 	| 10.66666666666667  	| 10.720722247761335  	| 0.005157990270151295  	|                     	|                     	|                     	|
| $V[W_2]$   	| 162.97677193201042  	| 5643.917288997072     	| 160.41263740173974 	|  **152                  	| 165.5409064622811   	| 0.015733128714442535  	| 5381.1559562800785  	| 5926.502049105222   	| 0.04822803206158341 	|

152, que era o valor referência obtido para $V[W_2]$, está fora do IC; preciso determinar novamente esse valor, utilizando $k=5000$ amostras:

###### Tabela 56

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| collect_all 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 7500             	| 5000              	| False       	| 5000000                     	| 100000 	|


| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|-------------------	|--------------------	|----------------------	|-------------------	|-------------------	|---------------------	|
| $V[W_2]$ 	| 162.61484124641493 	| 5850.3872874612125 	| 160.8835111851632 	| 164.34617130766665 	| 0.010646814571052588 	| 5667.551696769544 	| 6042.258354985377 	| 0.03199937971322402 	|


162.61484124641493 parece um valor mais apropriado, e está dentro do intervalo de confiança obtido acima!

Com $\rho = 0.9$:

###### Tabela 57

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9             	| exponential     	| exponential     	| 1.0          	| 3300             	| 5000              	| 7500000                     	| 100000 	|

| metric       	| $\hat{\mu}$                	| $\hat{\sigma}^2$              	| $t_{\alpha/2;n-1}$            	| $\mu$     	| $t_{1 - \alpha/2;n-1}$             	| $pr(t)$           	| ${\chi^2}_{\alpha/2;n-1}$          	| ${\chi^2}_{1-\alpha/2;n-1}$          	| $pr({ \chi^2 })$      	|
|--------------	|---------------------	|-----------------------	|--------------------	|---------------------	|---------------------	|-----------------------	|---------------------	|---------------------	|---------------------	|
| $E[N_1]$  	| 0.8181365655037685  	| 0.0013343345673498235 	| 0.8168898055177348 	| 0.8181818181818181  	| 0.8193833254898021  	| 0.0015239020459450827 	|                     	|                     	|                     	|
| $E[N_2]$  	| 11.899071782461721  	| 10.164347472703751    	| 11.790256413616273 	| 11.863636363636367  	| 12.00788715130717   	| 0.009144861955184881  	|                     	|                     	|                     	|
| $E[Nq_1]$ 	| 0.36811816322674007 	| 0.0008616065780756041 	| 0.3671163079500804 	| 0.36818181818181817 	| 0.36912001850339976 	| 0.002721558936070837  	|                     	|                     	|                     	|
| $E[Nq_2]$ 	| 11.448988808045312  	| 10.132441062494927    	| 11.34034436196268  	| 11.413636363636368  	| 11.557633254127945  	| 0.009489435958421574  	|                     	|                     	|                     	|
| $E[T_1]$  	| 1.8166641264859886  	| 0.004799936607238246  	| 1.8142994690301513 	| 1.8181818181818181  	| 1.819028783941826   	| 0.0013016481260140667 	|                     	|                     	|                     	|
| $E[T_2]$  	| 26.305466369622312  	| 46.03333290135228     	| 26.07389402287392  	| 26.36363636363637   	| 26.537038716370706  	| 0.008803202478699102  	|                     	|                     	|                     	|
| $E[W_1]$  	| 0.8169514255898758  	| 0.0036140649707058757 	| 0.8148995620958001 	| 0.8181818181818181  	| 0.8190032890839515  	| 0.002511610151844937  	|                     	|                     	|                     	|
| $V[W_1]$   	| 2.30105007195304    	| 0.16484423652779068   	| 2.2871924927133267 	| 2.3057851239669422  	| 2.3149076511927533  	| 0.006022284959645203  	| 0.15716965714208628 	| 0.17309780699120447 	| 0.04822803206158341 	|
| $E[W_2]$  	| 25.305626838697258  	| 45.988809947084796    	| 25.074166506206357 	| 25.36363636363637   	| 25.53708717118816   	| 0.009146595496972693  	|                     	|                     	|                     	|
| $V[W_2]$   	| 749.7937897484463   	| 402803.95113153924    	| 728.1318497834983  	|   **747                  	| 771.4557297133944   	| 0.028890529984538157  	| 384050.7877516766   	| 422971.9040040995   	| 0.04822803206158341 	|

Todos os valores dentro dos respectivos ICs.

Os arquivos completos da análise estão na pasta `files/tests/comparison_analytical_values`.


## Chegando ao fator mínimo

As configurações da máquina em que os testes foram executados:

- Processador: Intel(R) Core(TM) i5-1035G1 CPU @ 1.00GHz   1.19 GHz

- RAM: 20,0 GB

- Sistema Operacional: Windows 10

O objetivo foi fazer a métrica mais crítica(para essa simulação, $V[W_2]$) estivesse dentro dos intervalos de confiança de 5%, com o menor número de eventos de chegada desprezados na fase transiente.

$\rho = 0.6 : V[W_2] \rightarrow 25$

Os valores de $t$ utilizados(começando com um valor pequeno, até atingir o valor obtido na seção **Determinando a fase transiente**):

`
 t_values = [
            1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 750000,
            900000, 1000000
        ]
`

$t = 1000$:

###### Tabela 58

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 1000                        	| 100000 	| 131.40929007530212 	|

| metric     	| $\hat{\mu}$             	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|------------------	|--------------------	|-------------------	|-----------------	|-------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.4761789638118 	| 196.13441822026996 	| 24.99817951843843 	|     **25            	| 25.95417840918517 	| 0.018762603530629793 	| 187.00307584151085 	| 205.95465382680123 	| 0.04822803206158341 	|

$t = 5000$:

###### Tabela 59

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 5000                        	| 100000 	| 133.51163792610168 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$          	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|------------------	|-----------------	|--------------------	|----------------------	|-------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.48996363361754 	| 196.48314369508233 	| 25.0115394373075 	|      **25           	| 25.968387829927575 	| 0.018769120395254888 	| 187.3355658603762 	| 206.32083960437805 	| 0.04822803206158341 	|

$t = 10000$:

###### Tabela 60

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|-------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 10000                       	| 100000 	| 133.1740369796753 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|-------------------	|----------------------	|-------------------	|-------------------	|---------------------	|
| $V[W_2]$ 	| 25.48615839623788 	| 196.39836914189442 	| 25.00783742143699 	|    **25             	| 25.96447937103877 	| 0.018767872637545063 	| 187.2547381181417 	| 206.2318204821171 	| 0.04822803206158341 	|

$t = 25000$:

###### Tabela 61

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 25000                       	| 100000 	| 133.36272311210632 	|

| metric     	| $\hat{\mu}$             	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.4710829893768 	| 195.99766588717245 	| 24.993250212704723 	|     **25            	| 25.948915766048877 	| 0.018759813898426136 	| 186.87269022561645 	| 205.81105445409207 	| 0.04822803206158341 	|

$t = 50000$:

###### Tabela 62

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 50000                       	| 100000 	| 134.92953896522522 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.46575711155191 	| 195.67667492118963 	| 24.988315775395325 	|       **25          	| 25.943198447708493 	| 0.018748366053487762 	| 186.56664349245864 	| 205.47399182184017 	| 0.04822803206158341 	|


$t = 100000$:

###### Tabela 63

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|-------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 100000                      	| 100000 	| 136.1565020084381 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$          	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|-------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.420344312551485 	| 194.0155746075754 	| 24.944933796487177 	|     **25            	| 25.895754828615793 	| 0.018701969974087643 	| 184.98287828314025 	| 203.72972203397558 	| 0.04822803206158341 	|

$t = 250000$:

###### Tabela 64

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 250000                      	| 100000 	| 142.87065196037292 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|-------------------	|-----------------	|--------------------	|---------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.37225576623659 	| 200.97113050908447 	| 24.88839843616056 	|       **25          	| 25.856113096312622 	| 0.01907033156744035 	| 191.61460747974155 	| 211.03353500503434 	| 0.04822803206158341 	|

$t = 500000$:

###### Tabela 65

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|-------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 500000                      	| 100000 	| 150.7587537765503 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|-------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.312700682242323 	| 199.12723447851047 	| 24.831068145544194 	|         **25        	| 25.79433321894045 	| 0.019027307387868266 	| 189.85655689189397 	| 209.09731711877333 	| 0.04822803206158341 	|

$t = 750000$:

###### Tabela 66

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 750000                      	| 100000 	| 156.05911779403687 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$        	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|-------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.362575047962892 	| 197.84813999305752 	| 24.882491887519162 	|     **25            	| 25.842658208406622 	| 0.018928801966513677 	| 188.6370126362652 	| 207.75417977269376 	| 0.04822803206158341 	|

$t = 900000$:

###### Tabela 67

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time  	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 900000                      	| 100000 	| 162.858726978302 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|-------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.39756675623378 	| 197.13337265146615 	| 24.918351580317267 	|       **25          	| 25.87678193215029 	| 0.018868546759460366 	| 187.95552239808308 	| 207.00362481278444 	| 0.04822803206158341 	|

$t = 1000000$:

###### Tabela 68

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 1000000                     	| 100000 	| 167.53655791282654 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$           	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|-------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.344478653701888 	| 196.98122568144532 	| 24.865448441928194 	|     **25            	| 25.82350886547558 	| 0.018900771971639134 	| 187.81045886649065 	| 206.84386001053414 	| 0.04822803206158341 	|

A partir de $t=25000$ o valor referência ficou consistentemente dentro dos ICs obtidos.

Comprovando independência das seeds:

`
seed_values = [100000, 0, 500, 38973879268268725687256]
`

$s= 100000$, $t=25000$:

###### Tabela 69

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$   	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 25000                       	| 100000 	| 170.78981590270996 	|

| metric     	| $\hat{\mu}$             	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|------------------	|--------------------	|--------------------	|-----------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.4710829893768 	| 195.99766588717245 	| 24.993250212704723 	|                 	| 25.948915766048877 	| 0.018759813898426136 	| 186.87269022561645 	| 205.81105445409207 	| 0.04822803206158341 	|

$s= 0$, $t=25000$:

###### Tabela 70

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$ 	| simulation_time   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|------	|-------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 25000                       	| 0    	| 148.6248140335083 	|

| metric     	| $\hat{\mu}$              	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$         	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$        	| $pr({ \chi^2 })$      	|
|------------	|-------------------	|--------------------	|--------------------	|-----------------	|--------------------	|---------------------	|--------------------	|-------------------	|---------------------	|
| $V[W_2]$ 	| 25.31240089974998 	| 179.80215574382663 	| 24.854735654046415 	|                 	| 25.770066145453548 	| 0.01808067308653003 	| 171.43118720381253 	| 188.8046528475406 	| 0.04822803206158341 	|

$s= 500$, $t=25000$:

###### Tabela 71

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$ 	| simulation_time   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|------	|-------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 25000                       	| 500  	| 135.1620237827301 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$           	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$          	| $pr(t)$          	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|-------------------	|-----------------	|------------------	|----------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.209481198700736 	| 184.77815259325962 	| 24.74552626510627 	|                 	| 25.6734361322952 	| 0.018403985783665276 	| 176.17551879367454 	| 194.02979241186372 	| 0.04822803206158341 	|

$s= 38973879268268725687256$, $t=25000$:

###### Tabela 72

| ${1- \alpha}$ 	| $\rho$ 	| arrival_process 	| service_process 	| $\mu$ 	| $n$ 	| $k$ 	| $t$ 	| $s$                  	| simulation_time    	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|-----------------------	|--------------------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 25000                       	| 3,89738792682687E+022 	| 157.39960312843323 	|

| metric     	| $\hat{\mu}$               	| $\hat{\sigma}^2$           	| $t_{\alpha/2;n-1}$            	| $\mu$ 	| $t_{1 - \alpha/2;n-1}$            	| $pr(t)$        	| ${\chi^2}_{\alpha/2;n-1}$         	| ${\chi^2}_{1-\alpha/2;n-1}$         	| $pr({ \chi^2 })$      	|
|------------	|--------------------	|--------------------	|--------------------	|-----------------	|--------------------	|--------------------	|--------------------	|--------------------	|---------------------	|
| $V[W_2]$ 	| 25.088778819327313 	| 167.79297166577726 	| 24.646661661258044 	|                 	| 25.530895977396582 	| 0.0176221075267594 	| 159.98110933721378 	| 176.19418206948836 	| 0.04822803206158341 	|

Houve variação em relação ao valor médio, mas em todos eles, o valor referência pertencia ao IC.

Dessa forma, tenho o fator mínimo:

$f = k \times n + t = 3300 \times 1000 + 25000 = 3325000$

## Conclusões

### Aprendizados

- O obtenção de resultados simulados auxiliou na hora de determinar se o valor obtido analiticamente a partir de manipulações algébricas estava correto; Por exemplo, quando estava incialmente obtendo os valores analíticos para a fila 2, estava obtendo resultados discrepantes com os resultados simulados. Após revisão tanto do código do simulador quanto das fórmulas obtidas, encontrei no material da apostila novas fórmulas que convergiam com os resultados que estavam sendo obtidos na simulação.

### Dificuldades

- Erros devido a aritmética de ponto flutuante
    Nas operações aritméticas que eram feitas no sistema(ex: ao adicionar um evento de partida, somando o tempo atual com o tempo de serviço), a representação dos valores de tempo fazia com que o tempo de serviço efetivo na fila 2 de um cliente fosse sempre ligeiramente maior do que o tempo que foi de fato gerado para ele. Por exemplo:

    - ao chegar em serviço: client 4, service time queue 2: 0.5497878190747206
    - ao sair do serviço: client 4, effective service time queue 2: 0.549787819074723
    - - diferença: -0.0000000000000024

    - ao chegar em serviço: client 5, service time queue 2: 0.5181251288306629 
    - ao sair do serviço: client 5, effective service time queue 2: 0.5181251288306612
    - - diferença: 0.0000000000000017

    Não houve impacto estatístico na análise dos resultados. Porém, em outros contextos, isso poderia forçar que a implemetação do simulador tivesse tratamento para esse tipo de erro(uma alternativa em Python é o pacote [Decimal - https://docs.python.org/3/library/decimal.html#module-decimal](https://docs.python.org/3/library/decimal.html#module-decimal))

### Possíveis melhorias

- Output unificado

    A análise e depuração do simulador poderia ser simplificada e melhorada se houvesse um output único para as métricas, por meio de um arquivo unificado ou uma interface gráfica. Dividir as saídas em múltiplos arquivos tornou o processo de depuração demorado.

- Otimização de código para cenários de alta taxa de utilização

    Taxas altas de utilização dos sistema faziam com que o tempo de simulação disparasse(20 minutos, e as vezes até 30 minutos). Há otimizações à nivel de estrutura de dados que podem ser feitas(exemplo: estrutura para coleta de métricas dos clientes na fila 2) para que o tempo total de simulação diminua.

## Instruções para execução do simulador

Para a execução, é necessário instalar a versão [versão 3.11.1 do Python - https://www.python.org/downloads/release/python-3111/](https://www.python.org/downloads/release/python-3111/).

Após a instalação, para realizar o download das dependências do projeto, executar o seguinte comando abaixo a partir da pasta raiz:

`pip install -r requirements.txt`

Para executar o simulador, executar o comando a seguir a partir da pasta raiz do projeto:

`python src/start_simulator_3.py`