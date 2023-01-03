# Trabalho de simulação - Teoria de Filas

## Introdução

### Visão geral

A implementação foi realizada em Python. 

O ponto inicial é o arquivo `main.py`, onde é criado uma instância do o simulador(classe Simulator), com os parametros apropriados. No construtor da classe, são iniciadas as variáveis de controle e parametrizações do simulador(detalhados mais adiante). Em seguida, inicia-se a execução do simulador, chamando o método `run()`.

A execução do simulador é da seguinte forma:

No laço principal, é gerado o evento inicial de chegada do cliente(evento ARRIVAL). Em seguida o programa trata os eventos da lista de eventos e realiza a coleta das estatísticas apropriadas para cada tipo de evento. O objetivo é que cada cliente servido tenha uma estatística de cada tipo coletada(dentre ). Os eventos podem ser dos seguintes tipos:

- `EventType.ARRIVAL`: é a chegada de um novo cliente ao sistema. Caso o sistema se encontre vazio, o cliente recém chegado inicia imediatamente o serviço. Se o serviço corrente for um cliente oriudo da fila de menor prioridade, o serviço é interrompido e o cliente recém chegado inicia a sua execução. Nos demais casos, o cliente é enfileirado na fila de maior prioridade. É neste momento que novas chegadas ao sistema são agendadas. Ao término do método, a estatística `NQ1` é amostrada.
- `EventType.START_SERVICE_1`: início do primeiro serviço do cliente, oriundo da fila de maior prioridade. É agendada um evento de término do primeiro serviço. `NQ1`, `N1` e `W1` são amostradas.
- `EventType.END_SERVICE_1`: término do primeiro serviço do cliente. Se não houverem serviços em execução, o cliente inicia o segundo serviço imediatamente. Caso contrário, é direcionado para a fila de menor prioridade. `X1` e `T1` são amostradas.
- `EventType.START_SERVICE_2`: início do segundo serviço do cliente, oriundo da fila de menor prioridade. É agendado o evento de partida do cliente do sistema para o momento do término do serviço. `NQ2` e `N2` são amostradas.
- `EventType.HALT_SERVICE_2`: interrupção do segundo serviço do cliente. Conforme dito no enunciado do trabalho, acontece sempre que um novo cliente chega ao sistema durante um serviço corrente que é oriundo da fila de menor prioridade. Quando esse evento ocorre, é necessário remover a partida do cliente que havia sido criada pelo evento do tipo `EventType.START_SERVICE_2`. `NQ2` é amostrada.
- `EventType.DEPARTURE`: o término do segundo serviço do cliente, e a subsequente partida desse do sistema. Se houverem novos cliente para serem servidos, tem-se o serviço iniciado, de acordo com a prioridade da fila em que se encontram. `W2`, `X2` e `T2` são amostradas.

Ao final de cada rodada, a média e a variância amostral são obtidas a partir das amostras obtidas durante o tratamento dos eventos.

### Estruturas e variáveis internas

Ao longo do código, são utilizadas diversas variáveis e estruturas de controle. Dentre elas, as mais relevantes são:

- `self.__utilization_pct`, `self.__service_rate`, `self.__arrival_rate`: São as indicações das taxas de utilização, de serviço e de chegada ao sistema. As duas primeiras são informadas no momento de instânciação da classe do simulador, e a última é derivada dessas, pela relação $$\rho = {\lambda \over \mu}$$

- `self.__number_of_rounds`, `self.__round_size`, `self.__current_round`: O número de rodadas da simulação, o tamanho de cada rodada, e o contador da rodada corrente.

- `self.__metric_samples_current_round`, `self.__events_current_round`, `self.__metrics_per_round`: Os dois primeiros representam as métricas e os eventos da rodada atual. São utilizados para a geração das médias e variâncias amostrais das métricas, que acontece ao final de cada rodada no método `self.__generate_round_metrics`, e o resultado é armazenado como um registro na lista `self.__metrics_per_round`. Esses registros são utilizados ao final das rodadas para determinar o intervalo de confiança para as métricas.

- `self.__event_log_raw`, `self.__event_log_raw_file`: Log de todos os eventos de todas as rodadas de simulação. Ao final, há a opção de salvar esse log no arquivo indicado pela varíavel `self.__event_log_raw_file`. Não interferem nas funções essenciais do simulador, mas foram utilizadas na depuração do simulador nas etapas iniciais de implementação.

- `self.__current_timestamp`, `self.__current_service`: usadas para armazenar o tempo corrente de simulação e o serviço corrente em execução. O tempo é avançado à medida em que os eventos são tratados. Quando há o início ou término de um serviço, o valor do serviço corrente é modificado.

- `self.__event_q`: É a lista principal de eventos do simulador. De maneira geral, os eventos são inseridos na lista de maneira que permaneça sempre de maneira crescente pelo `timestamp` dos eventos. A inserção ordenada é feita utilizando o [`insort`](https://docs.python.org/3/library/bisect.html#bisect.insort).

- `self.__waiting_qs`: representação das filas de espera do sistema(como uma lista de listas). É gerida utilizando a estratégia FIFO, suportada pelas APIs padrão de listas do Python.

- `self.__served_clients_current_round`: O número de clientes servidos na rodada atual.Tem o seu valor incrementado sempre que um novo cliente chega ao sistema. Ao final de cada rodada, o valor é resetado.

A representação dos eventos e das métricas também merecem ser destacados. Foram criadas as classes `Event` e `Metric` para facilitar a representação e o entendimento ao longo do código.

- `Event`
    - example

- `Metric`
    - example

## Teste de correção dos resultados
## Determinando a fase transiente
## Análise dos resultados
## Otimizações
## Conclusão
### Integrantes do grupo
- Guilherme Avelino do Nascimento - DRE 117078497

## Instruções para execução dos programas
