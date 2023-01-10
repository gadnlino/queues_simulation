# Trabalho de simulação - Teoria de Filas

## Introdução

### Visão geral

A implementação foi realizada em Python 3. Para a execução do simulador, ver seção **Instruções para execução do simulador**.

O ponto inicial é o arquivo `main.py`, onde é criado uma instância do o simulador(classe Simulator), com os parametros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

A execução do simulador é da seguinte forma:

No loop principal, é gerado o evento inicial de chegada do cliente(evento ARRIVAL). Em seguida o programa trata os eventos da lista de eventos e realiza a coleta das estatísticas apropriadas para o cliente associado a cada evento. O objetivo é que, a cada partida de um cliente, tenham sido coletadas uma amostra de uma das métricas de seu tempo de atraso e tempo de serviço em cada uma das filas. O simulador gera novas chegadas de cliente até que a quantidade de métricas a serem coletadas na simulação tenha sido atiginda.

Ao final da simulação, há a opção de gerar arquivos com as métricas a cada rodada e gráficos com a evolução desses valores. Os arquivos são salvos na pasta de resultados da simulação('results_{timestamp}').

Os eventos da simulação podem ser dos seguintes tipos:

- `EventType.ARRIVAL`: é a chegada de um novo cliente ao sistema. Caso o sistema se encontre vazio, o cliente recém chegado inicia imediatamente o serviço. Se o serviço corrente for um cliente oriudo da fila de menor prioridade, o serviço é interrompido e o cliente recém chegado inicia a sua execução. Nos demais casos, o cliente é enfileirado na fila de maior prioridade. É nesse momento que novas chegadas ao sistema são agendadas.

- `EventType.START_SERVICE_1`: início do primeiro serviço do cliente, oriundo da fila de maior prioridade. É obtido o tempo de serviço e agendado um evento de término desse primeiro serviço.

- `EventType.END_SERVICE_1`: término do primeiro serviço do cliente. Se não houverem serviços em execução, o cliente inicia o segundo serviço imediatamente. Caso contrário, é direcionado para a fila de menor prioridade.

- `EventType.START_SERVICE_2`: início do segundo serviço do cliente, oriundo da fila de menor prioridade. É obtido o tempo de serviço e agendado o evento de partida do sistema para o momento do término do serviço.

- `EventType.HALT_SERVICE_2`: interrupção do segundo serviço do cliente. Acontece sempre que um novo cliente chega ao sistema durante um serviço oriundo da fila de menor prioridade. Quando esse evento ocorre, é necessário remover a partida do cliente que teve seu serviço interrompido.

- `EventType.DEPARTURE`: o término do segundo serviço do cliente, e a sua subsequente partida do sistema. Se houverem novos cliente para serem servidos, tem-se o serviço iniciado, seguindo a ordem de prioridade das filas.

Ao final de cada rodada, a média e a variância amostral são obtidas a partir das amostras obtidas durante o tratamento dos eventos.

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

- `self.__utilization_pct`, `self.__service_rate`, `self.__arrival_rate`: São as indicações das taxas de utilização, de serviço e de chegada ao sistema. As duas primeiras são informadas no momento de instânciação da classe do simulador, e a última é derivada dessas, pela relação $$\rho = {\lambda \over \mu}$$

- `self.__current_timestamp`, `self.__current_service`: usadas para armazenar o tempo corrente de simulação e o serviço corrente em execução. O tempo é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor do serviço corrente é modificado.

- `self.__number_of_rounds`, `self.__samples_per_round`, `self.__current_round`: O número de rodadas da simulação, o número de amostras coletadas a cada rodada, e o contador da rodada corrente.

- `self.__metrics_per_round`: Ao final de cada rodada, o método `self.__generate_round_metrics` é chamado e as métricas para a rodada atual são geradas. O resultado é armazenado como um registro na lista `self.__metrics_per_round`. Essa lista é usada para gerar os gráficos e os arquivos .csv ao final da simulação.

- `self.__event_log_raw`, `self.__event_log_raw_file`: Log de todos os eventos de todas as rodadas de simulação. Ao final, há a opção de salvar esse log no arquivo indicado pela varíavel `self.__event_log_raw_file`. Não interferem nas funções essenciais do simulador, mas foram utilizadas na depuração do simulador nas etapas iniciais de implementação.

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

A geração de variáveis aleatórias é feita usando a função [random](https://docs.python.org/3/library/random.html#random.random), disponível na biblioteca padrão da linguagem. A seed utilizado é a informada na configuração dos parametros do simulador.

Para gerar amostras de variáveis aleatórias exponenciais, é usado o seguinte cálculo(como também indicado nos materiais de aula):

$$x_0 = {\log{u_0} \over -\lambda}$$

### Amostragem

Para as métricas referentes ao número de clientes no sistema e em cada fila de espera, a coleta é realizada a cada tratamento de evento da simulação. Isso permitiu uma maior precisão para as estimativas relacionados à fila 2, que tem seus eventos associados tratados somente após os eventos da fila 1 por conta da precedência de prioridade.

Para a média dos tempos em fila de espera, tempo de serviço e tempo total, é calculado o valor absoluto para cada um dos clientes, e, ao final da rodada, ou seja, após a partida de k clientes, calcula-se o valor médio e a variância para a rodada. Nesse momento, é incrementa-se o estimador para a média do valor médio das rodadas. No gráfico gerado ao final das rodadas, esse valor é apresentado por uma linha tracejada, por ex:

[Médias da simulação tracejado em azul e vermelho](./images/example_mean_values.png)

### Intervalo de confiança

## Teste de correção dos resultados

Foram realizadas execuções com o simulador configurado para uma fila D/D/1. Pela forma como foi configurada da rede de filas do problema e a prioridade preemptiva, para a fila convergir com os tempos determinísticos é necessário que o cliente tenha os dois serviços executados e deixe o sistema antes que um novo cliente chegue ao sistema. Caso contrário, o simulador permanece em execução eternamente. Isso foi atestado ao rodar com os parâmetros abaixo:

| inter_arrival_time(s) 	| service_time(s) 	| number_of_rounds 	| samples_per_round 	| services_until_steady_state 	| E[W1] 	| E[W2] 	| termina execução? 	|
|-----------------------	|-----------------	|------------------	|-------------------	|-----------------------------	|-------	|-------	|-------------------	|
| 1.0                   	| 2.1             	| 20               	| 50                	| 10000                       	| -     	| -     	| não               	|
| 2.1                   	| 1.0             	| 20               	| 50                	| 10000                       	| 0     	| 0     	| sim               	|
| 2.0                   	| 1.0             	| 20               	| 50                	| 10000                       	| 0     	| 0     	| sim               	|

## Determinando a fase transiente

Conforme o enunciado da tarefa, a equação de equilibrio para esse sistema é $$2\lambda = {\mu}$$

Então, para $$\rho = 1.0$$ e $$\mu = 1.0$$, posso deduzir analiticamente que o sistema permanece em equilíbrio para taxas de chegada até no máximo 0.5. Esse valor será mencionado mais adiante na seção **Conclusão**.

Dado isso, analisei o número de serviços executados pelo sistema até que entrasse em equilibrio, para diferentes taxas até essa taxa de serviço crítica, incrementando o número de rodadas e o número de serviços por rodada, e configurando o número de serviços até a fase transiente para 0 nas configurações do simulador.

De maneira geral, observou-se que com 10000 serviços executados(realizando a execução com os parametros `number_of_rounds`=200, `samples_per_round`=50, `services_until_steady_state`=0), o sistema já se encontrava em equilibrio para as taxas de utilização menores do que 0.5:

[rho = 0.2](./images/wait_time_10000_services_lambda_02.png)

[rho = 0.4](./images/wait_time_10000_services_lambda_04.png)

Com relação ao número ótimo de amostras por rodada, após algumas simulações com diferentes valores, foi observado que com k = 50 amostras por rodada fornecia um resultado razoável em relação à variancia e oferecendo um tempo de simulação mais rápido do que com quantidades maiores. Não foi observado diferença considerável na co-variância para valores de k acima deste. Abaixo estão alguns resultados com diferentes valores de k(observar as colunas terminadas por '_cov_var', em especial 'N2_cov_var' e 'NQ2_cov_var', que apresentam os maiores valores).

[k = 50](./files/metric_per_round_k_50.csv)

[k = 100](./files/metric_per_round_k_100.csv)

[k = 200](./files/metric_per_round_k_200.csv)

[k = 1000](./files/metric_per_round_k_1000.csv)

## Análise dos resultados

//TODO:
### Chegando ao fator mínimo

## Otimizações
//TODO:
## Conclusão

Ao executar a simulação para os diferentes valores da taxa de utilização, fica claro a relação entre essa taxa e a convergência da fila para um estado de equilibrio; Ao executar com taxas maiores do que 0.5, o número de clientes na fila 2 e o tempo de espera médio aumentam indefinidamente!

[Número médio de clientes na fila, lambda=0.49](./images/q_size_lambda_049.png)

[Atraso médio, lambda=0.49](./images/wait_time_lambda_049.png)

[Número médio de clientes na fila, lambda=0.51](./images/q_size_lambda_051.png)

[Atraso médio, lambda=0.51](./images/wait_time_lambda_051.png)

### Dificuldades
- Amostragem de métricas

    Não pude utilizar um sistema de cores a cada **chegada**, como indicado nos materiais de aula. O motivo foi que, na minha implemenmtação, caso considerasse somente as chegadas, as métricas da segunda fila(W2 e X2) poderiam não ser calculadas para o número desejado de clientes. Com isso, determinei que a rodada avançaria sempre que k clientes tivessem a sua **partida** do sistema.

- Cálculo do intervalo de confiança

    Como calculo o número de rodadas previamente, tendo uma precisão alvo para o intervalo de confiança?

## Instruções para execução do simulador

//TODO:

## Integrantes do grupo
- Guilherme Avelino do Nascimento - DRE 117078497