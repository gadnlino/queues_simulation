# Trabalho de simulação - Teoria de Filas
#### Guilherme Avelino do Nascimento - DRE 117078497
#### Link para o repositório no GitHub: https://github.com/gadnlino/queues_simulation

## Introdução

### Objetivo

O objetivo deste relatório é analisar o cenário descrito para o trabalho, que é o mesmo que está na página 111 da apostila da disciplina, e realizar comparações entre os valores analíticos lá apresentados e os obtidos nas simulações detalhadas a seguir.

### Visão geral

A implementação foi realizada em Python 3. Para a execução do simulador, ver seção **Instruções para execução do simulador**.

O ponto inicial é o arquivo `main.py`, onde é criado uma instância do o simulador(classe Simulator), com os parâmetros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

A execução do simulador é da seguinte forma:

No loop principal, é gerado o evento inicial de chegada do cliente(evento ARRIVAL). Em seguida o programa trata os eventos da lista de eventos e realiza a coleta de amostras das estatísticas  para o cliente associado a cada evento. O objetivo é que, a cada partida de um cliente, tenham sido coletadas uma amostra de uma das métricas de seu tempo de atraso e tempo de serviço em cada uma das filas. O simulador gera novas chegadas de cliente até que a quantidade de métricas a serem coletadas na simulação tenha sido atigida(seja atingindo a precisão alvo para as métricas, ou atingido o número de rodadas informado).

Ao final da simulação, há a opção de gerar arquivos com as métricas a cada rodada e gráficos com a evolução desses valores. Os arquivos são salvos na pasta de resultados da simulação('results_{timestamp}/').

Os eventos gerados na simulação são observados do ponto de vista do ciclo de vida de um freguês típico ao passar pelo sistema(chegada na fila 1, inicio do primeiro serviço, fim do serviço, chegada na fila 2, etc.), e são dos seguintes tipos:

- `EventType.ARRIVAL`: é a chegada de um novo cliente à fila 1. Caso o sistema se encontre vazio, o cliente recém chegado inicia imediatamente o serviço. Caso haja um cliente oriundo da fila 2 em serviço, esse tem o serviço interrompido, e o cliente recém chegado inicia o seu serviço imediatamente. Após esse tratamento, é programado um evento para a próxima chegada de um cliente na fila 1.

- `EventType.START_SERVICE_1`:é o início do primeiro serviço do cliente, que foi oriundo da fila 1. O tempo de serviço é obtido a partir da taxa/tempo especificados na inicialização do simulador. Um evento de término de serviço é agendado para o cliente.

- `EventType.END_SERVICE_1`: é o término do primeiro serviço do cliente. Caso não hajam clientes em nenhuma das duas filas, o cliente atual inicia o seu segundo serviço imediatamente. Se houver cliente na fila 1, esse tem prioridade no início do seu serviço; Caso contrário, o primeiro cliente da fila 2 tem a sua execução iniciada.

- `EventType.START_SERVICE_2`:é o início do segundo serviço do cliente, que foi oriundo da fila 2. É obtido o tempo de serviço taxa/tempo especificados e agendado o evento de partida da fila 2 para o momento do término do serviço.

- `EventType.HALT_SERVICE_2`: é a interrupção do segundo serviço do cliente. Acontece sempre que um novo cliente chega na fila 1 durante um serviço em execução oriundo da fila 2. Quando esse evento ocorre, é removido o evento de partida da fila 2 que havia sido agendado para o cliente que estava em execução.

- `EventType.DEPARTURE`:é o término do segundo serviço do cliente, e a sua subsequente partida da fila 2 e do sistema como um todo. Se houverem clientes em alguma das fila, eles tem o serviço iniciado seguindo a ordem de prioridade das filas.

Ao final de cada rodada, a média e a variância amostral são obtidas a partir das amostras obtidas durante o tratamento dos eventos.

**Observação**: poderia ter sido escolhido somente 2 tipos de eventos(chegadas e partidas, com o número da fila correspondente como parâmetro extra). Porém, foi escolhido particionar nos 6 eventos descritos acima a fim de  melhorar a legibilidade e a manutenibilidade do código do simulador.

### Simulador

O simulador é inicializado com os seguintes parâmetros:

- `arrival_process`:
    O processo de chegada de clientes ao sistema. Valores: 'exponential', 'deterministic'.

- `inter_arrival_time`:
    O tempo entre chegadas ao sistema. Só é considerado quando o arrival_process = 'deterministic'.

- `utilization_pct`:
    A porcentagem de utilização do sistema(rho). Só é considerado quando o arrival_process = 'exponential'.

- `service_process`:
    O processo de serviço do sistema. Valores: 'exponential', 'deterministic'.

- `service_time`:
    O tempo de serviço do sistema. Só é considerado quando o service_process = 'deterministic'.

- `service_rate`:
    A taxa de serviço do sistema(mu). Só é considerado quando o service_process = 'exponential'.

- `number_of_rounds`:
    O número de rodadas da simulação.

- `target_precision`:
    A precisão alvo para as métricas coletadas na simulação.
        
- `confidence`:
    A porcentagem do intervalo de confiança determinado nas métricas coletadas no sistema.

- `samples_per_round`:
    O número de amostras que serão coletadas a cada rodada de simulação.

- `services_until_steady_state`:
    O número de serviços executados no sistema(ciclo completo de um cliente no sistema) até atingir o estado de equilíbrio no sistema.

- `seed`:
    A semente inicial para geração de variáveis aleatórias no sistema. Será usada durante toda a simulação.

- `save_metric_per_round_file`:
    Caso True, salva um arquivo .csv com a evolução das métricas por rodada.

- `save_raw_event_log_file`:
    Caso True, salva um arquivo .csv com todos os eventos da simulação(para depuração).

- `plot_metrics_per_round`:
    Caso True, gera gráficos com o tempo de espera médio e o número médio de clientes em cada fila.

### Estruturas e variáveis internas

Ao longo do código, são utilizadas diversas variáveis e estruturas de controle. Dentre elas, as mais relevantes são:

- `self.__event_q`: É a lista principal de eventos do simulador. De maneira geral, os eventos são inseridos na lista de maneira que permaneça sempre de maneira crescente pelo `timestamp` dos eventos. A inserção ordenada é feita utilizando o [`insort`](https://docs.python.org/3/library/bisect.html#bisect.insort).

- `self.__waiting_qs`: representação das filas de espera do sistema(como uma lista de listas). É gerida utilizando a estratégia FIFO, suportada pelas APIs padrão de listas do Python.

- `self.__arrival_rate`: A taxa de chegada de clientes ao sistema. É obtida pela relação $$\rho = {\lambda \over \mu}$$

- `self.__current_timestamp`, `self.__current_service`: Armazenam o tempo corrente de simulação e o serviço corrente em execução. O tempo é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor do serviço corrente é modificado.

- `self.__current_round`: O número de rodadas da simulação, o número de amostras coletadas a cada rodada, e o contador da rodada corrente.

- `self.__metric_estimators_current_round`, `self.__metrics_per_round`, `self.__metric_estimators_simulation`: No tratamento de cada tipo de evento, `self.__metric_estimators_current_round` é increntado com a métrica calculada para cada cliente. Ao final de cada rodada, o método `self.__generate_round_metrics` é chamado e as métricas para a rodada atual são geradas. O resultado é armazenado como um registro na lista `self.__metrics_per_round` e incrementado no estimador global das métricas da simulação, `self.__metric_estimators_simulation`. Essas estruturas são usadas gerar os gráficos e os arquivos .csv ao final da simulação.

- `self.__clients_in_system`: Armazena todos os clientes presentes no sistema, seus eventos, e as métricas já calculadas para o cliente.

Cada evento é representado pela classe `Event`, com as seguintes propriedades:

- `client_id`: Id do cliente associado à esse evento.
- `type`: Tipo do evento.
- `timestamp`: Instante de ocorrência do evento.
- `queue_number`: Número da fila onde o evento irá ocorrer.
- `remaining_service_time`: Tempo restante de serviço do cliente associado ao evento. Será preenchido somente quando type = EventType.START_SERVICE_2.

Os tipos de evento tem a seguinte prioridade associadas entre si:

`{
    EventType.ARRIVAL: 1,
    EventType.START_SERVICE_1: 1,
    EventType.END_SERVICE_1: 1,
    EventType.START_SERVICE_2: 1,
    EventType.HALT_SERVICE_2: 1,
    EventType.DEPARTURE: 0
}`

Isso faz com que, caso haja uma partida e uma chegada para o mesmo instante, ocorra primeiro o tratamento da partida.

### Geração de VA's

A geração de variáveis aleatórias é feita usando a função [random](https://docs.python.org/3/library/random.html#random.random), disponível na biblioteca padrão do Python. A seed inicial utilizada é a informada na configuração dos parâmetros do simulador.

Para gerar amostras de variáveis aleatórias exponenciais, é usado o seguinte cálculo(como também indicado nos materiais de aula):

$$x_0 = {\log{u_0} \over -\lambda}$$

### Amostragem

Para as métricas referentes ao número de clientes no sistema e em cada fila espera, a coleta é realizada a cada tratamento de evento da simulação. Isso permitiu uma maior precisão para as estimativas relacionados à fila 2, que tem seus eventos associados tratados somente após os eventos da fila 1 devido à precedência de prioridade.

Para a média dos tempos em fila espera, tempo de serviço e tempo total, é calculado o valor absoluto para cada um dos clientes, e, ao final da rodada, ou seja, após a partida de k clientes, calcula-se o valor médio e a variância para a rodada. Nesse momento, é incrementa-se o estimador global para a média e variância do valor médio das rodadas. No gráfico gerado ao final das rodadas, esse valor é representado por uma linha tracejada, por ex:

[Médias da simulação (linhas azuis e vermelhas tracejadas)](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png))

## Determinação do intervalo de confiança e número de rodadas

Ao final de cada rodada, são determinados os intervalos de confiança para a média e variânciia de cada métrica, a partir do estimador global(`self.__metric_estimators_simulation`). O calculo é feito iterativamente, e a simulação e encerrada somente quando não há nenhuma métrica em que a precisão está acima do `target_precision` informado para a porcentagem de confiança `confidence`.

Os cálculos usados para determinar os valores máximos e mínimos do intervalo de confiança estão no arquivo `src/utils/estimator.py`.

## Teste de correção dos resultados

Conforme indicado na página 111 da apostila, o cenário pode ser caracterizado por um sistema de filas HOL em que a fila 1 tem prioridade e interrompe com continuidade os serviços a fila 2. Só há entradas exógenas na primeira fila, e ao final do primeiro serviço $$X_1$$, os clientes seguem para a segunda fila e recebem o serviço $$X_2$$, de modo que o serviço total é $$X = {X_1 + X_2}$$.

Nesse cenário, é mais prático analisar as duas filas de maneira separada.

### Fila 1

A fila 1 não sofre interrupção, então:

$$E[W_1] = {\rho_1 E[X_{1r}] \over {1-\rho_1}}$$

Como os tempos de serviços seguem uma distribuição exponencial,

$$E[X_{1r}] = E[X_1] = {1 \over \mu }$$

Dessa forma:

$$E[W_1] = {\rho_1 \over {({1-\rho_1}) \mu}}$$


Os resultados analíticos, para as diferentes taxas de utilização(com $$\mu = 1$$):

| $$\rho_1$$ 	| $$E[W_1]$$  	|
|------------	|------------	|
| 0,2        	| 0,25       	|
| 0,4        	| 0,66666... 	|
| 0,6        	| 1,5        	|
| 0,8        	| 4          	|
| 0,9        	| 9          	|

Ao rodar a simulação, com processos de chegadas e serviços exponenciais(fila 1 se comportando como uma fila M/M/1):

Com precisão de 5%:

| metric      	| lower               	| mean                	| upper              	| variance            	| precision            	| confidence 	| rounds 	|
|-------------	|---------------------	|---------------------	|--------------------	|---------------------	|----------------------	|------------	|--------	|
| W1_est_mean 	| 0.24417837568491232 	| 0.24891135818876323 	| 0.2536443406926141 	| 0.02541166057338099 	| 0.019014730939926075 	| 0.95       	| 3071   	|

Com 20000 rodadas:

| metric      	| lower              	| mean                	| upper               	| variance             	| precision            	| confidence 	| rounds 	|
|-------------	|--------------------	|---------------------	|---------------------	|----------------------	|----------------------	|------------	|--------	|
| W1_est_mean 	| 0.2498590794078621 	| 0.25179153846424845 	| 0.25372399752063485 	| 0.027602972390038418 	| 0.007674837161617935 	| 0.95       	| 20001  	|

Com 50000 rodadas:

| metric      	| lower               	| mean               	| upper              	| variance             	| precision            	| confidence 	| rounds 	|
|-------------	|---------------------	|--------------------	|--------------------	|----------------------	|----------------------	|------------	|--------	|
| W1_est_mean 	| 0.24913344201438836 	| 0.2503461970724465 	| 0.2515589521305046 	| 0.027179758079981704 	| 0.004844311885860886 	| 0.95       	| 50001  	|

Garantidamente pela Lei Forte dos Grandes Números, se o número de rodadas da simulação for infinitamente grande, o resultado convergirá para o valor calculado analiticamente.

Para $$E[W_2]$$:

Foram realizadas execuções com o simulador configurado para uma fila D/D/1. Em um cenário que há infinitas chegadas ao sistema, é necessário que cada cliente tenha os dois serviços executados e deixe o sistema antes que um novo cliente chegue ao sistema. Caso contrário, o simulador permanece em execução eternamente. Nesse cenário, os clientes teriam tempo de espera em fila nulo. Isso foi atestado ao rodar com os parâmetros abaixo:

| tempo entre chegadas 	| tempo de serviço 	| rodadas 	| amostras / rodada 	| fase transiente 	| termina execução? 	|
|-----------------------	|-----------------	|------------------	|-------------------	|-----------------------------	|-------------------	|
| 1.0                   	| 2.1             	| 20               	| 50                	| 10000                       	| não               	|
| 2.1                   	| 1.0             	| 20               	| 50                	| 10000                       	| sim               	|
| 2.0                   	| 1.0             	| 20               	| 50                	| 10000                       	| sim               	|

## Determinando a fase transiente

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

Ao executar a simulação para os diferentes valores da taxa de utilização, fica claro a relação entre essa taxa e a convergência da fila para um estado de equilibrio; Ao executar com taxas maiores do que 0.5, o número de clientes na fila 2 e o tempo de espera médio aumentam indefinidamente!

[Número médio de clientes na fila, lambda=0.49](https://github.com/gadnlino/queues_simulation/raw/main/images/q_size_lambda_049.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/q_size_lambda_049.png))

[Atraso médio, lambda=0.49](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_lambda_049.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_lambda_049.png))

[Número médio de clientes na fila, lambda=0.51](https://github.com/gadnlino/queues_simulation/raw/main/images/q_size_lambda_051.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/q_size_lambda_051.png))

[Atraso médio, lambda=0.51](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_lambda_051.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/wait_time_lambda_051.png))

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

### Dificuldades
- Amostragem de métricas

    Não pude utilizar um sistema de cores a cada **chegada**, como indicado nos materiais de aula. Na minha implementação, caso considerasse somente as chegadas, as métricas da segunda fila(W2 e X2) poderiam não ser calculadas para o número desejado de clientes, pois os eventos da fila 2 são resolvidos por último. Isso criou cenários em que o programa do simulador ficou execução indefinidamente(o caso da fila D/D/1 mencionado anteriormente, por exemplo). Perante isso, determinei que a rodada avançaria sempre que k clientes tivessem a sua **partida** do sistema.

### Pendências
- É possível melhorar a análise do simulador para cenários determinísticos, ao aceitar uma lista de instantes de chegada, por exemplo. Isso facilitaria a depuração do simulador ao gerar arquivos de logs menores com a lista dos eventos do sistema.

- É necessário uma análise detalhada do simulador comparativamente com os cenários obtidos analiticamente.

## Instruções para execução do simulador

Para a execução, é necessário instalar a versão [versão 3.11.1 do Python](https://www.python.org/downloads/release/python-3111/)([link](https://www.python.org/downloads/release/python-3111/)).

Após a instalação, para realizar o download das dependências do projeto, executar o seguinte comando abaixo a partir da pasta raiz:

`pip install -r requirements.txt`

Para executar o simulador, executar o comando a seguir a partir da pasta raiz do projeto:

`python src/main.py`