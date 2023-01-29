# Trabalho de simulação - Teoria de Filas
#### Guilherme Avelino do Nascimento - DRE 117078497
#### Link para o repositório no GitHub: https://github.com/gadnlino/queues_simulation

## Introdução

### Visão geral

A implementação foi realizada em Python 3. As instruções para a execução do simulador estão ne seção **Instruções para execução do simulador**.

O ponto inicial é o arquivo `main.py`, onde é criado uma instância do o simulador(classe Simulator3), com os parâmetros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

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
- `utilization_pct`: A porcentagem de utilização do sistema(rho). Só é considerado quando o arrival_process = 'exponential'.
- `service_rate`: A taxa de serviço do sistema(mu). Só é considerado quando o service_process = 'exponential'.
- `service_time`: O tempo de serviço do sistema. Só é considerado quando o service_process = 'deterministic'.
- `number_of_rounds`: O número de rodadas da simulação.,
- `samples_per_round`: O número de amostras que serão coletadas a cada rodada de simulação.
- `arrivals_until_steady_state`: O número de chegada à fila 1 processados até o sistema atingir o estado de equilíbrio.
- `predefined_system_arrival_times`: Instantes de chegada pré determinados. Podem ser utilizados para depurar o simulador.
- `confidence`: float: A porcentagem do intervalo de confiança determinado nas métricas coletadas no sistema.,
- `seed`: A semente inicial para geração de variáveis aleatórias no sistema. Será usada durante toda a simulação.
- `save_raw_event_log_file`: Caso True, salva um arquivo .csv com todos os eventos da simulação(para depuração).
- `save_metric_per_round_file`: Caso True, salva um arquivo .csv ao final da simulação com a evolução das métricas a cada rodada executada.
- `plot_metrics_per_round`: Caso True, gera gráficos ao final da simulação com a evolução de cada uma das métricas a cada rodada executada.

### Estruturas e variáveis internas

Ao longo do código, são utilizadas diversas variáveis e estruturas de controle. Dentre elas, as mais relevantes são:

- `self.__event_q`: É a lista principal de eventos do simulador. De maneira geral, os eventos são inseridos na lista de maneira que permaneça sempre de maneira crescente pelo `timestamp` dos eventos. Se houver uma chegada e uma partida com o mesmo instante, a partida é inserida em uma posição antecedente a da chegada, a fim de que seja processada primeiro.

- `self.__waiting_qs`: representação das filas de espera do sistema(lista de listas). É gerenciada utilizando a estratégia FIFO, suportada pelas APIs padrão de listas do Python. Os clientes que têm seus serviços interrompidos são postos execpcionalmente na primeira posição da fila.

- `self.__arrival_rate`: A taxa de chegada de clientes ao sistema. É obtida pela relação $$\rho = {2\lambda}$$, descrita no enunciado do trabalho.

- `self.__current_timestamp`, `self.__current_service`, `self.__interrupted_service`: Armazenam o tempo corrente de simulação , o serviço corrente em execução e o ultimo serviço interrompido. O timestamp é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor de current_service é modificado. Sempre que um cliente inicia o seu serviço, o simulador calcula os tempos de espera para esse cliente. Da mesma forma, quando um cliente sai do serviço, é calculado o seu tempo de serviço. Finalmentem sempre que um cliente é interrompido e retorna para o serviço, o valor de interrupted_service é atualizado.

- `self.__current_round`: O número de rodadas da simulação, o número de amostras coletadas a cada rodada, e o contador da rodada corrente.

- `self.__metric_estimators_current_round`, `self.__metrics_per_round`, `self.__metric_estimators_simulation`: No tratamento de cada tipo de evento, `self.__metric_estimators_current_round` é increntado com a métrica calculada para cada cliente. Ao final de cada rodada, o método `self.__generate_round_metrics` é chamado e as métricas para a rodada atual são geradas. O resultado é armazenado como um registro na lista `self.__metrics_per_round` e incrementado no estimador global das métricas da simulação, `self.__metric_estimators_simulation`. Essas estruturas são usadas gerar os gráficos e os arquivos .csv ao final da simulação.

- `self.__clients_in_system`: Armazena todos os clientes presentes no sistema, seus eventos, e as métricas calculadas para o cliente(tempo de espera, tempo de serviço, etc.).

- `self.__metric_estimators_current_round`: os estimadores para as métricas da rodada atual. Cada métrica tem o estimador associado(ver seção **Classe Estimator** abaixo). São obtidos utilizando o cálculo incremental para a média e variância. 

- `self.__metrics_per_round`: Dataframe com as evolução de cada uma das métricas coletadas ao longo das rodadas. É utilizado para salvar o arquivo .csv com a evolução das métricas ao final da simulação.

- `self.__metric_estimators_simulation`: Os estimadores para as métricas globais da simulação. É utilizada para gerar o arquivo .csv com as métricas globais da simulação.

- `self.__execution_parameters`: Parâmetros utilizados na execução da simulação. 

### Estimadores

Para a estimativa das métricas da simulação, foram utilizados 2 tipos de estimadores:

- `IncrementalEstimator`: como o nome sugere, realiza a estimativa da média e da variância do parametro coletado utilizando o cálculo incremental. E usado para calcular o valor médio e variãncia das métricas dos clientes(tempo de espera e tempo total). A implementação está no arquivo `utils/incremental_estimator.py`.

- `AreaEstimator`: usa o cálculo de área x tempo. É usado para calcular o valor esperado e variância dos parâmetros relacionados à fila(número de clientes). A implementação está no arquivo `utils/area_estimator.py`.

### Geração de VA's

A geração de variáveis aleatórias é feita usando a função [random](https://docs.python.org/3/library/random.html#random.random), disponível na biblioteca padrão do Python. A seed inicial utilizada é a informada na configuração dos parâmetros do simulador.

Para gerar amostras de variáveis aleatórias exponenciais, é usado o seguinte cálculo(como também indicado nos materiais de aula): $x_0 = {\log{u_0} \over -\lambda}$

### Amostragem

- TODO: Descrever método batch
- TODO: seed utilizada por toda a simulação
- TODO: descrever conceito de cores

Para as métricas referentes ao número de clientes no sistema e em cada fila espera, a coleta é realizada a cada tratamento de evento da simulação. Isso permitiu uma maior precisão para as estimativas relacionados à fila 2, que tem seus eventos associados tratados somente após os eventos da fila 1 devido à precedência de prioridade.

Para a média dos tempos em fila espera, tempo de serviço e tempo total, é calculado o valor absoluto para cada um dos clientes, e, ao final da rodada, ou seja, após a partida de k clientes, calcula-se o valor médio e a variância para a rodada. Nesse momento, é incrementa-se o estimador global para a média e variância do valor médio das rodadas. No gráfico gerado ao final das rodadas, esse valor é representado por uma linha tracejada, por ex:

[Médias da simulação (linhas azuis e vermelhas tracejadas)](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png))

### Arquivos da simulação

Ao final da execução, o simulador salva os arquivos para análise das métricas na pasta `results_{timestamp}_simulator3`. Estes são:

- Arquivos .png(exemplo: `W1_est_mean_X_round.png`) com os valores médios de cada uma das métricas, a cada rodada;
- `simulation_metrics.csv`: onde são armazenados os resultados finais(média, variância, intervalos de confiança) de cada uma das métricas.
- `execution_parameters.csv`: os parâmetros utilizados para a simulação.
- `metric_per_round_evolution.csv`: evolução das métricas, rodada a rodada. É a representação tabular dos dados apresentados nos arquivos .png .
- `event_log_raw.csv`: Lista com todos os eventos tratados na simulação.

## Corretude do simulador e análise dos resultados

### Cenários controlados

1) Chegadas a cada 2 segundos, serviço constante = 1 segundo:

Nesse cenário, o tempo de espera para os clientes em ambas as filas é; o cliente chega ao sistema pela fila 1 e tem os seus 2 serviços realizados antes que um novo cliente chegue e o interrompa. A variância dos tempo de espera e de serviço também deve ser nula para esse cenário.

Parâmetros alvo: $E[W_1] = 0$, $Var[W_1] = 0$, $E[W_2] = 0$, $E[T_1] = E[X] = 1$, $E[T_2] = E[X] = 1$

| confidence 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 10               	| 2                 	| 0                           	| 100000 	|

| metric      	| mean               	| variance            	| lower_t            	| upper_t            	| precision_t         	| lower_chi2 	| upper_chi2 	| precision_chi2     	| confidence 	|
|-------------	|--------------------	|---------------------	|--------------------	|--------------------	|---------------------	|------------	|------------	|--------------------	|------------	|
| T1_est_mean 	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606 	| 0.33215132908679623 	|            	|            	|                    	| 0.95       	|
| T1_est_var  	| 0.0                	| 0.0                 	|                    	|                    	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| T2_est_mean 	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606 	| 0.33215132908679623 	|            	|            	|                    	| 0.95       	|
| T2_est_var  	| 0.0                	| 0.0                 	|                    	|                    	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| W1_est_mean 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                	| 0.0                 	|            	|            	|                    	| 0.95       	|
| W1_est_var  	| 0.0                	| 0.0                 	| 0.0                	| 0.0                	| 0.0                 	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| W2_est_mean 	| 0.0                	| 0.0                 	| 0.0                	| 0.0                	| 0.0                 	|            	|            	|                    	| 0.95       	|
| W2_est_var  	| 0.0                	| 0.0                 	| 0.0                	| 0.0                	| 0.0                 	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| X1_est_mean 	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606 	| 0.33215132908679623 	|            	|            	|                    	| 0.95       	|
| X1_est_var  	| 0.0                	| 0.0                 	|                    	|                    	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| X2_est_mean 	| 0.8181818181818182 	| 0.16363636363636366 	| 0.5464216398380759 	| 1.0899419965255606 	| 0.33215132908679623 	|            	|            	|                    	| 0.95       	|
| X2_est_var  	| 0.0                	| 0.0                 	|                    	|                    	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|

Utilizando um número de amostras por rodada:

| confidence 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 10               	| 1000              	| 0                           	| 100000 	|

| metric      	| mean               	| variance            	| lower_t            	| upper_t           	| precision_t         	| lower_chi2 	| upper_chi2 	| precision_chi2     	| confidence 	|
|-------------	|--------------------	|---------------------	|--------------------	|-------------------	|---------------------	|------------	|------------	|--------------------	|------------	|
| T1_est_mean 	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267 	| 0.22281388519649376 	|            	|            	|                    	| 0.95       	|
| T1_est_var  	| 0.0                	| 0.0                 	|                    	|                   	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| T2_est_mean 	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267 	| 0.22281388519649376 	|            	|            	|                    	| 0.95       	|
| T2_est_var  	| 0.0                	| 0.0                 	|                    	|                   	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| W1_est_mean 	| 0.0                	| 0.0                 	| 0.0                	| 0.0               	| 0.0                 	|            	|            	|                    	| 0.95       	|
| W1_est_var  	| 0.0                	| 0.0                 	| 0.0                	| 0.0               	| 0.0                 	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| W2_est_mean 	| 0.0                	| 0.0                 	| 0.0                	| 0.0               	| 0.0                 	|            	|            	|                    	| 0.95       	|
| W2_est_var  	| 0.0                	| 0.0                 	| 0.0                	| 0.0               	| 0.0                 	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| X1_est_mean 	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267 	| 0.22281388519649376 	|            	|            	|                    	| 0.95       	|
| X1_est_var  	| 0.0                	| 0.0                 	|                    	|                   	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|
| X2_est_mean 	| 0.9090909090909091 	| 0.09090909090909083 	| 0.7065328316395512 	| 1.111648986542267 	| 0.22281388519649376 	|            	|            	|                    	| 0.95       	|
| X2_est_var  	| 0.0                	| 0.0                 	|                    	|                   	|                     	| 0.0        	| 0.0        	| 0.7263419942725865 	| 0.95       	|

Com um número grande de rodadas e de amostras por rodada:

| confidence 	| arrival_process 	| inter_arrival_time 	| service_process 	| service_time 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|--------------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| deterministic   	| 2.0                	| deterministic   	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric      	| mean               	| variance               	| lower_t            	| upper_t           	| precision_t           	| lower_chi2 	| upper_chi2 	| precision_chi2      	| confidence 	|
|-------------	|--------------------	|------------------------	|--------------------	|-------------------	|-----------------------	|------------	|------------	|---------------------	|------------	|
| T1_est_mean 	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836 	| 0.0005941463981405022 	|            	|            	|                     	| 0.95       	|
| T1_est_var  	| 0.0                	| 0.0                    	|                    	|                   	|                       	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|
| T2_est_mean 	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836 	| 0.0005941463981405022 	|            	|            	|                     	| 0.95       	|
| T2_est_var  	| 0.0                	| 0.0                    	|                    	|                   	|                       	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|
| W1_est_mean 	| 0.0                	| 0.0                    	| 0.0                	| 0.0               	| 0.0                   	|            	|            	|                     	| 0.95       	|
| W1_est_var  	| 0.0                	| 0.0                    	| 0.0                	| 0.0               	| 0.0                   	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|
| W2_est_mean 	| 0.0                	| 0.0                    	| 0.0                	| 0.0               	| 0.0                   	|            	|            	|                     	| 0.95       	|
| W2_est_var  	| 0.0                	| 0.0                    	| 0.0                	| 0.0               	| 0.0                   	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|
| X1_est_mean 	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836 	| 0.0005941463981405022 	|            	|            	|                     	| 0.95       	|
| X1_est_var  	| 0.0                	| 0.0                    	|                    	|                   	|                       	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|
| X2_est_mean 	| 0.9996970614965162 	| 0.00030293850348381523 	| 0.9991030950881964 	| 1.000291027904836 	| 0.0005941463981405022 	|            	|            	|                     	| 0.95       	|
| X2_est_var  	| 0.0                	| 0.0                    	|                    	|                   	|                       	| 0.0        	| 0.0        	| 0.04822073339236929 	| 0.95       	|

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

| confidence 	| utilization_pct    	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| collect_all 	| arrivals_until_steady_state 	| seed   	|
|------------	|--------------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-------------	|-----------------------------	|--------	|
| 0.95       	| 1.2360679774997898 	| exponential     	| exponential     	| 1.0          	| 200              	| 1000              	| False       	| 0                           	| 100000 	|

| metric       	| mean               	| variance             	| lower_t            	| upper_t            	| precision_t         	| lower_chi2         	| upper_chi2        	| precision_chi2     	| confidence 	|
|--------------	|--------------------	|----------------------	|--------------------	|--------------------	|---------------------	|--------------------	|-------------------	|--------------------	|------------	|
| NQ1_est_mean 	| 1.0223135198009698 	| 0.053628265261648156 	| 0.9900226891614518 	| 1.0546043504404878 	| 0.03158603502162882 	|                    	|                   	|                    	| 0.95       	|

O valor alvo está dentro do IC, com precisão de 3%.

3) $Var[W_1]$ para chegadas e serviços exponenciais

$Var[W_1]$ é um dos valores que podem ser obtidos analiticamente(olhar seção **Obtenção dos valores analíticos**). Quero testar se o simulador converge para esses valores com uma signficância razoável no intervalo.

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| collect_all 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 200              	| 1000              	| False       	| 0                           	| 100000 	|

| metric     	| mean                	| variance              	| lower_t             	| mean_analytical    	| upper_t           	| precision_t          	| lower_chi2           	| upper_chi2           	| precision_chi2     	| confidence 	|
|------------	|---------------------	|-----------------------	|---------------------	|--------------------	|-------------------	|----------------------	|----------------------	|----------------------	|--------------------	|------------	|
| W1_est_var 	| 0.23321915896621948 	| 0.0061345276204282035 	| 0.22229789496520694 	| 0.2345679012345679 	| 0.244140422967232 	| 0.046828331126065055 	| 0.005087400463141368 	| 0.007543717452937571 	| 0.1944655260220003 	| 0.95       	|

Mesmo com um número pequeno de amostras, o intervalo de confiança pela distribuição t já contém o valor analítico. Testando para as outras taxas de utilização:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| collect_all 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 200              	| 1000              	| False       	| 0                           	| 100000 	|

| metric     	| mean               	| variance             	| lower_t            	| mean_analytical 	| upper_t            	| precision_t        	| lower_chi2           	| upper_chi2           	| precision_chi2     	| confidence 	|
|------------	|--------------------	|----------------------	|--------------------	|-----------------	|--------------------	|--------------------	|----------------------	|----------------------	|--------------------	|------------	|
| W1_est_var 	| 0.5400784761128288 	| 0.023057594053774756 	| 0.5189051378014886 	| 0.5625          	| 0.5612518144241689 	| 0.0392041883685747 	| 0.019121800719826467 	| 0.028354257319990483 	| 0.1944655260220003 	| 0.95       	|

A partir de $\rho=0.4$, foi preciso aumentar o número de amostras por rodada para 2000:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| collect_all 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-------------	|-----------------------------	|--------	|
| 0.95       	| 0.4             	| exponential     	| exponential     	| 1.0          	| 200              	| 2000              	| False       	| 0                           	| 100000 	|

| metric     	| mean               	| variance             	| lower_t          	| mean_analytical 	| upper_t            	| precision_t          	| lower_chi2           	| upper_chi2           	| precision_chi2     	| confidence 	|
|------------	|--------------------	|----------------------	|------------------	|-----------------	|--------------------	|----------------------	|----------------------	|----------------------	|--------------------	|------------	|
| W1_est_var 	| 0.5518384454432985 	| 0.013368070041296753 	| 0.53571652778966 	| 0.5625          	| 0.5679603630969371 	| 0.029214922930365227 	| 0.011086220476525004 	| 0.016438909321527025 	| 0.1944655260220003 	| 0.95       	|

Para $\rho=0.6$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.6             	| exponential     	| exponential     	| 1.0          	| 200              	| 2000              	| 0                           	| 100000 	|

| metric     	| mean               	| variance            	| lower_t            	| mean_analytical    	| upper_t            	| precision_t          	| lower_chi2          	| upper_chi2          	| precision_chi2     	| confidence 	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|--------------------	|----------------------	|---------------------	|---------------------	|--------------------	|------------	|
| W1_est_var 	| 1.0433874152391551 	| 0.05058689214110876 	| 1.0120255891760541 	| 1.0408163265306123 	| 1.0747492413022561 	| 0.030057700145743545 	| 0.04195201235227223 	| 0.06220743384771249 	| 0.1944655260220003 	| 0.95       	|

Para $\rho=0.8$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.8             	| exponential     	| exponential     	| 1.0          	| 200              	| 2000              	| 0                           	| 100000 	|

| metric     	| mean               	| variance            	| lower_t            	| mean_analytical    	| upper_t           	| precision_t        	| lower_chi2        	| upper_chi2         	| precision_chi2     	| confidence 	|
|------------	|--------------------	|---------------------	|--------------------	|--------------------	|-------------------	|--------------------	|-------------------	|--------------------	|--------------------	|------------	|
| W1_est_var 	| 1.7591048192846979 	| 0.15553337569379302 	| 1.7041134996799967 	| 1.7777777777777781 	| 1.814096138889399 	| 0.0312609680798113 	| 0.128984759136729 	| 0.1912616444709501 	| 0.1944655260220003 	| 0.95       	|

Para $\rho=0.9$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9             	| exponential     	| exponential     	| 1.0          	| 200              	| 2000              	| 0                           	| 100000 	|

| metric     	| mean               	| variance            	| lower_t           	| mean_analytical    	| upper_t            	| precision_t         	| lower_chi2          	| upper_chi2          	| precision_chi2     	| confidence 	|
|------------	|--------------------	|---------------------	|-------------------	|--------------------	|--------------------	|---------------------	|---------------------	|---------------------	|--------------------	|------------	|
| W1_est_var 	| 2.3551656920552086 	| 0.40446563672113695 	| 2.266486208062589 	| 2.3057851239669422 	| 2.4438451760478284 	| 0.03765318265791922 	| 0.33542577275677016 	| 0.49737725080676537 	| 0.1944655260220003 	| 0.95       	|

De forma geral, as outras métricas também se mantiveram dentro dos intervalos de confiança. Os dados para esse teste estão na pasta `files/tests/correctness/3`.

## Obtenção dos melhores parâmetros de simulação

### Número de amostras por rodada

Utilizando como base $n = 3300$ rodadas de simulação(precisão de 5% para intervalos de confiança com a distribuição $\chi^2$), e iniciando com $k = 50$ amostras por rodada, foi aumentando-se o valor de $k$, com o objetivo de que:

- $W_2$, que é  métricas mais crítica, tivese baixa covariância entre as rodadas ;
- O valor analítico estivesse contido no intervalo de confiança de 95%, para todos os valores de $\rho$ ;
- Se possível, utilizar um único valor $k$ para para os todos os valores de $\rho$ especificados("one size fits all")

Com $k=50$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 50                	| 0                           	| 100000 	|

| metric      	| mean               	| variance            	| lower_t            	| mean_analytical    	| upper_t            	| confidence 	| mean_cov            	| mean_cov_var       	|
|-------------	|--------------------	|---------------------	|--------------------	|--------------------	|--------------------	|------------	|---------------------	|--------------------	|
| W2_est_mean 	| 0.5188093565987869 	| 0.09620391380100349 	| 0.5082229917569027 	| 0.5277777777777777 	| 0.5293957214406712 	| 0.95       	| 0.08995108640195859 	| 0.1613545491714309 	|
| W2_est_var  	| 1.3961475008876056 	| 3.786746159765684   	| 1.329729838885159  	|                    	| 1.4625651628900522 	| 0.95       	| 0.08995108640195859 	| 0.1613545491714309 	|

Com $k=200$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 200               	| 0                           	| 100000 	|

| metric      	| mean               	| variance             	| lower_t            	| mean_analytical    	| upper_t            	| confidence 	| mean_cov             	| mean_cov_var         	|
|-------------	|--------------------	|----------------------	|--------------------	|--------------------	|--------------------	|------------	|----------------------	|----------------------	|
| W2_est_mean 	| 0.5259460939556508 	| 0.026158010670828586 	| 0.5204259189898711 	| 0.5277777777777777 	| 0.5314662689214306 	| 0.95       	| 0.025640044888092503 	| 0.023699462289277225 	|
| W2_est_var  	| 1.4724587117315704 	| 1.1375833428086584   	| 1.436055299049282  	|                    	| 1.5088621244138587 	| 0.95       	| 0.025640044888092503 	| 0.023699462289277225 	|

Com $k=500$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 500               	| 0                           	| 100000 	|

| metric      	| mean               	| variance             	| lower_t            	| mean_analytical    	| upper_t            	| confidence 	| mean_cov             	| mean_cov_var         	|
|-------------	|--------------------	|----------------------	|--------------------	|--------------------	|--------------------	|------------	|----------------------	|----------------------	|
| W2_est_mean 	| 0.5264975364581754 	| 0.009737571464964243 	| 0.5231295075075206 	| 0.5277777777777777 	| 0.5298655654088302 	| 0.95       	| 0.009712947604901984 	| 0.007527052458936212 	|
| W2_est_var  	| 1.4866630199215638 	| 0.41992724294746886  	| 1.4645454447395154 	|                    	| 1.5087805951036122 	| 0.95       	| 0.009712947604901984 	| 0.007527052458936212 	|

Com $k=1000$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric      	| mean               	| variance              	| lower_t            	| mean_analytical    	| upper_t            	| confidence 	| mean_cov             	| mean_cov_var         	|
|-------------	|--------------------	|-----------------------	|--------------------	|--------------------	|--------------------	|------------	|----------------------	|----------------------	|
| W2_est_mean 	| 0.5272496612129796 	| 0.0049782743101671805 	| 0.5248414759271138 	| 0.5277777777777777 	| 0.5296578464988453 	| 0.95       	| 0.004952935843448389 	| 0.003593132503179382 	|
| W2_est_var  	| 1.4892347387653133 	| 0.20285390144015686   	| 1.4738623213240816 	|                    	| 1.504607156206545  	| 0.95       	| 0.004952935843448389 	| 0.003593132503179382 	|

Com $k=2000$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 2000              	| 0                           	| 100000 	|

| metric      	| mean               	| variance              	| lower_t            	| mean_analytical    	| upper_t            	| confidence 	| mean_cov              	| mean_cov_var         	|
|-------------	|--------------------	|-----------------------	|--------------------	|--------------------	|--------------------	|------------	|-----------------------	|----------------------	|
| W2_est_mean 	| 0.5274856548276599 	| 0.0024898840167682495 	| 0.5257825552329782 	| 0.5277777777777777 	| 0.5291887544223415 	| 0.95       	| 0.0024778216942935557 	| 0.001728231254712837 	|
| W2_est_var  	| 1.4923618888673191 	| 0.09904385299896964   	| 1.4816204057457254 	|                    	| 1.5031033719889129 	| 0.95       	| 0.0024778216942935557 	| 0.001728231254712837 	|

Aqui a simulação já fica significativamente mais lenta, levando 276 segundos, contra 157 segundos com $k=1000$, para as mesmas 3300 rodadas. A relação entre a autocovariância e a variância já é baixa o suficiente para $k=1000$(0,35%). Realizei um último teste, com a maior taxa de utilização especificada, para confirmar se o $k=1000$ atende todos os critérios necessários:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9            	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric      	| mean               	| variance           	| lower_t            	| mean_analytical   	| upper_t            	| confidence 	| mean_cov           	| mean_cov_var       	|
|-------------	|--------------------	|--------------------	|--------------------	|-------------------	|--------------------	|------------	|--------------------	|--------------------	|
| W2_est_mean 	| 24.732225893701486 	| 193.66961231002122 	| 24.257239435090884 	| 25.36363636363637 	| 25.207212352312087 	| 0.95       	| 176.13210137618066 	| 0.5924679584969877 	|
| W2_est_var  	| 568.7950124906531  	| 426787.6816180937  	| 546.4974995394372  	|                   	| 591.092525441869   	| 0.95       	| 176.13210137618066 	| 0.5924679584969877 	|

Será necessário um valor maior de $k$ para essa taxa de utilização!

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.9            	| exponential     	| exponential     	| 1.0          	| 3300             	| 5000              	| 0                           	| 100000 	|

| metric      	| mean              	| variance           	| lower_t            	| mean_analytical   	| upper_t            	| confidence 	| mean_cov          	| mean_cov_var        	|
|-------------	|-------------------	|--------------------	|--------------------	|-------------------	|--------------------	|------------	|-------------------	|---------------------	|
| W2_est_mean 	| 25.19073470689688 	| 41.772294326007554 	| 24.970140221396115 	| 25.36363636363637 	| 25.411329192397645 	| 0.95       	| 40.83508451218092 	| 0.07509593846468973 	|
| W2_est_var  	| 736.3220614355928 	| 282519.78562533064 	| 718.1804892612905  	|                   	| 754.463633609895   	| 0.95       	| 40.83508451218092 	| 0.07509593846468973 	|


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

### Determinando a fase transiente

Para que o simulador colete as métricas com qualidade, o sistema deve primeiro ter entrado em equilíbrio para que então realize-se a amostragem. Dentre as métricas, a mais crítica e a que não possui valores bem determinados analiticamente é $Var[W_2]$, a variância do tempo de espera na fila 2. Para ter uma valor de referência para essa métrica, realizei execuções da simulador com um número de rodadas bem elevado: Eis os resultados obtidos:

Com $\rho = 0.2$



Conforme o enunciado da tarefa, a equação de equilibrio para esse sistema é $$2\lambda = {\mu}$$

Então, para $$\rho = 1.0$$ e $$\mu = 1.0$$, posso deduzir analiticamente que o sistema permanece em equilíbrio para taxas de chegada até no máximo 0.5. Esse valor será mencionado mais adiante na seção **Conclusão**.

Dado isso, analisei o número de serviços executados pelo sistema até que entrasse em equilibrio, para diferentes taxas até essa taxa de serviço crítica, incrementando o número de rodadas e o número de serviços por rodada, e configurando o número de serviços até a fase transiente para 0 nas configurações do simulador.

De maneira geral, observou-se que com 10000 serviços executados(realizando a execução com os parametros `number_of_rounds`=200, `samples_per_round`=50, `services_until_steady_state`=0), o sistema já se encontrava em equilibrio para as taxas de utilização menores do que 0.5:

[rho = 0.2](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_10000_services_lambda_02.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_10000_services_lambda_02.png))

[rho = 0.4](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_10000_services_lambda_04.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_10000_services_lambda_04.png))

Com relação ao número ótimo de amostras por rodada, após algumas simulações com diferentes valores, foi observado que com k = 50 amostras por rodada fornecia um resultado razoável em relação à variancia e oferecendo um tempo de simulação mais rápido do que com quantidades maiores. Não foi observado diferença considerável na co-variância para valores de k acima deste. Abaixo estão alguns resultados com diferentes valores de k(observar as colunas terminadas por '_cov_var', em especial 'N2_cov_var' e 'NQ2_cov_var', que apresentam os maiores valores).

[k = 50](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_50.csv)([link](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_50.csv))

[k = 100](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_100.csv)([link](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_100.csv))

[k = 200](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_200.csv)([link](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_200.csv))

[k = 1000](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_1000.csv)([link](https://github.com/gadnlino/queues_simulation/raw/main/files/metric_per_round_k_1000.csv))



## Análise dos resultados

### Obtenção dos valores analíticos

Para realizar a comparação com os valores obtidos no simulador, primeiro deduziu-se os valores analíticos para as variáveis interessadas:

Da fila 1:

$E[W_1] = {\rho_1 E[X_{1r}] \over {1-\rho_1}} = {\rho_1 \over {({1-\rho_1}) \mu}}$

$E[Nq_1] = {\lambda E[W_1]} = {\lambda \rho_1 \over {({1-\rho_1}) \mu}}$

$E[T_1] = {E[W_1] + E[X_1]} = {E[W_1] + E[X]} = {{\rho_1 \over {({1-\rho_1}) \mu}} + {1 \over \mu}}$

$E[N_1] = {\lambda E[T_1]} = {\lambda ({{\rho_1 \over {({1-\rho_1}) \mu}} + {1 \over \mu}})}$

A variância de $W_1$(extraída da página 92 da apostila):

$Var[W_{1}] = {E[W_{1}^2] - (E[W_{1}])^2}$

Com $E[W_1^2] = { 2(E[W_1])^2 + \frac{\lambda E[X^3]}{3(1 - \rho_1)}}$ e $E[X^3] = - ({{({-1})^3 \frac{d}{ds^3} {E[e^{-sX}]}}(0)}) = {\frac{6}{\mu^3}}$ , obtenho $Var[W_1] = {E[W_1]^2 + \frac{\lambda}{3({1-\rho_1})} \frac{6}{\mu^3}}$:

Da fila 2:

$E[T_2] = {\frac{\rho(1-\rho_1)E[W_1] + \rho_2E[X] + \rho_1(1-\rho)E[X] + (1-\rho_2)E[X]}{(1-\rho_1)(1-\rho)}}$

Observação: O valor de $E[T_2]$ foi obtido da página 111 da apostila. A fórmula apresentada no slide 17 é diferente, e apresentava resultados discrepantes em relação com a fórmula da apostila e os resultados simulados.

Exemplos:

Com a fórmula dos slides:

| metric       	| mean_analytical   	|
|--------------	|----------------------	|
| T2_est_mean  	| 1.3888888888888888   	|

Com a fórmula da página 111:

| metric       	| mean_analytical   	|
|--------------	|----------------------	|
| T2_est_mean  	| 1.5277777777777777   	|

$E[W_2] = E[T_2] - E[X_2] = E[T_2] - E[X] = E[T_2] - {\frac{1}{\mu}}$

$E[N_2] = {\lambda E[T_2]}$

$E[Nq_2] = \lambda E[W_2] = \lambda (E[T_2] - E[X_2]) = \lambda (E[T_2] - {\frac{1}{\mu}})$

Tenho então os valores obtidos analiticamente:

| rho 	|  mu  	|  E_W1                	|  Var_W1             	|  E_NQ1                 	|  E_T1               	|  E_N1                	|  E_W2                	|  E_NQ2                	|  E_T2               	|  E_N2               	|
|-----	|------	|----------------------	|---------------------	|------------------------	|---------------------	|----------------------	|----------------------	|-----------------------	|---------------------	|---------------------	|
| 0.2 	| 1    	|  0.11111111111111112 	|  0.2345679012345679 	|   0.011111111111111113 	|  1.1111111111111112 	|  0.11111111111111112 	|   0.5277777777777777 	|   0.05277777777777777 	|  1.5277777777777777 	|  0.1527777777777778 	|
| 0.4 	| 1    	|  0.25                	|  0.5625             	|   0.05                 	|  1.25               	|  0.25                	|   1.5000000000000004 	|   0.3000000000000001  	|  2.5000000000000004 	|  0.5000000000000001 	|
| 0.6 	| 1    	|  0.4285714285714286  	|  1.0408163265306123 	|   0.1285714285714286   	|  1.4285714285714286 	|  0.42857142857142855 	|   3.6428571428571423 	|   1.0928571428571427  	|  4.642857142857142  	|  1.3928571428571426 	|
| 0.8 	| 1    	|  0.6666666666666667  	|  1.7777777777777781 	|   0.2666666666666667   	|  1.6666666666666667 	|  0.6666666666666667  	|   10.66666666666667  	|   4.266666666666668   	|  11.66666666666667  	|  4.666666666666668  	|
| 0.9 	| 1    	|  0.8181818181818181  	|  2.3057851239669422 	|   0.36818181818181817  	|  1.8181818181818181 	|  0.8181818181818181  	|   25.36363636363637  	|   11.413636363636368  	|  26.36363636363637  	|  11.863636363636367 	|

O arquivo com as funções para geração dos valores acima é o `utils/analitical_values.py`.

Tendo os valores analíticos, executei o simulador com as taxas de utilização especificadas e com os parâmetros do número de rodadas, quantidade de amostras por rodada e tamanho da fase transiente obtidas nas seções anteriores:



## Chegando ao fator mínimo

As configurações da máquina em que executei os testes:

- Processador: Intel(R) Core(TM) i5-1035G1 CPU @ 1.00GHz   1.19 GHz

- RAM: 20,0 GB

- Sistema Operacional: Windows 10

Os valores abaixo mostram a quantidade de rodadas até que todas as métricas coletadas alcancem a precisão desejada:

| teste | utilizacao | taxa de serviço | seed     | número de rodadas | coletas por rodada | partidas desprezadas | fator mínimo | tempo(segundos) |
| ----- | ---------- | --------------- | -------- | ----------------- | ------------------ | -------------------- | ------------ | --------------- |
| 1     | 0.2        | 1.0             | 0        | 3071              | 50                 | 10000                | 163550       | 137,18          |
| 2     | 0.2        | 1.0             | 10^3     | 3071              | 50                 | 10000                | 163550       | 137,36          |
| 3     | 0.2        | 1.0             | 10^7 | 3071              | 50                 | 10000                | 163550       | 136,47          |
| 5     | 0.4        | 1.0             | 10^3     | 3071              | 50                 | 10000                | 163550       | 142,86          |
| 6     | 0.4        | 1.0             | 10^7 | 3071              | 50                 | 10000                | 163550       | 159,34          |
| 7     | 0.6        | 1.0             | 0        | 3071              | 50                 | 10000                | 163550       | 137,99          |
| 8     | 0.6        | 1.0             | 10^3     | 3071              | 50                 | 10000                | 163550       | 145,02          |
| 9     | 0.6        | 1.0             | 10^7 | 3071              | 50                 | 10000                | 163550       | 136,32          |
| 10    | 0.8        | 1.0             | 0        | 3071              | 50                 | 10000                | 163550       | 140,22          |
| 11    | 0.8        | 1.0             | 10^3     | 3071              | 50                 | 10000                | 163550       | 137,75          |
| 12    | 0.8        | 1.0             | 10^7 | 3071              | 50                 | 10000                | 163550       | 156,90          |
| 13    | 0.9        | 1.0             | 0        | 3598              | 50                 | 10000                | 189900       | 159,83          |
| 14    | 0.9        | 1.0             | 10^3     | 3166              | 50                 | 10000                | 168300       | 141,38          |
| 15    | 0.9        | 1.0             | 10^7 | 3453              | 50                 | 10000                | 182650       | 154,99          |

## Conclusões

### Aprendizados

O simulador me ajuda a avaliar se um resultado que obtive analiticamente através de manipulações algébricas está certo ou errado(mencionar caso do cálculo de $E[W_2] = 1$)

### Dificuldades

- Erro nunérico de ponto flutuante do Python:
    Ao calcula o tempo de serviço restante do cliente pertencente a fila 2, as operações aritméticas resultavam em um erro numérico, que fazia com o que o tempo de serviço resultante(considerando todas as interrupções) fosse ligeiramente maior do que o obtido inicialmente para o cliente. Por exemplo:

    client 4, service time queue 2: 0.5497878190747206 | client 4, effective service time queue 2: 0.549787819074723

    client 5, service time queue 2: 0.5181251288306629 | client 5, effective service time queue 2: 0.5181251288306612

    Solução: Decimal?(https://docs.python.org/3/library/decimal.html#module-decimal)

## Instruções para execução do simulador

Para a execução, é necessário instalar a versão [versão 3.11.1 do Python - https://www.python.org/downloads/release/python-3111/](https://www.python.org/downloads/release/python-3111/).

Após a instalação, para realizar o download das dependências do projeto, executar o seguinte comando abaixo a partir da pasta raiz:

`pip install -r requirements.txt`

Para executar o simulador, executar o comando a seguir a partir da pasta raiz do projeto:

`python src/start_simulator_3.py`