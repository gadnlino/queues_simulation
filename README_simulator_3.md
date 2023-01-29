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

Para as métricas referentes ao número de clientes no sistema e em cada fila espera, a coleta é realizada a cada tratamento de evento da simulação. Isso permitiu uma maior precisão para as estimativas relacionados à fila 2, que tem seus eventos associados tratados somente após os eventos da fila 1 devido à precedência de prioridade.

Para a média dos tempos em fila espera, tempo de serviço e tempo total, é calculado o valor absoluto para cada um dos clientes, e, ao final da rodada, ou seja, após a partida de k clientes, calcula-se o valor médio e a variância para a rodada. Nesse momento, é incrementa-se o estimador global para a média e variância do valor médio das rodadas. No gráfico gerado ao final das rodadas, esse valor é representado por uma linha tracejada, por ex:

[Médias da simulação (linhas azuis e vermelhas tracejadas)](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png)([link](https://github.com/gadnlino/queues_simulation/raw/main/images/example_mean_values.png))

### Arquivos da simulação

Ao final da execução, o simulador salva os arquivos para análise das métricas na pasta `results_{timestamp}_simulator3`. Estes são:

- Arquivos .png(ex: `W1_est_mean_X_round.png`) com os valores médios de cada uma das métricas, a cada rodada;
- `simulation_metrics.csv`: onde são armazenados os resultados finais(média, variância, intervalos de confiança) de cada uma das métricas.
- `execution_parameters.json`: os parâmetros utilizados para a simulação.
- `metric_per_round_evolution.csv`: evolução das métricas, rodada a rodada. É a representação tabular dos dados apresentados nos arquivos .png .
- `event_log_raw.csv`: Lista com todos os eventos tratados na simulação.

## Corretude do simulador e análise dos resultados

### Cenários determinísticos

1) Chegadas a cada 2 segundos, serviço constante = 1 segundo:

    Nesse cenário não há tempo de espera; o cliente chega ao sistema pela fila 1 e tem os seus 2 serviços realizados antes que um novo cliente chegue(e o interrompa). A variância deve ser nula para esse cenário.

    Parametros alvo: $E[W_1] = 0$, $E[W_2] = 0$, $E[T_1] = $1, $E[T_2] = 1$

## Obtenção dos melhores parâmetros de simulação

### Número de amostras por rodada

Utilizando como base $n = 3300$ rodadas de simulação(precisão de 5% para intervalos de confiança com a distribuição $\chi^2$), e iniciando com $k = 50$ amostras por rodada, foi aumentando-se o valor de $k$, com o objetivo de:

- A covariância entre a média das amostras a cada rodada fossem relativamente baixos;
- O valor analítico estivesse contido no intervalo de confiança de 95%, para todos os valores de $\rho$
- Pudesse ser utilizado um único valor $k$ para para os valores de $\rho$ especificados

$k=50$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 50                	| 0                           	| 100000 	|

Resultados(métricas com ** obtiveram valores fora do intervalo de confiança):

| metric       	| mean                 	| variance              	| lower_t              	| mean_analytical      	| upper_t              	| precision_t          	|
|--------------	|----------------------	|-----------------------	|----------------------	|----------------------	|----------------------	|----------------------	|
| N1_est_mean**  	| 0.11368963292894962  	| 0.0007445696936522023 	| 0.1127584450292298   	| 0.11111111111111112  	| 0.11462082082866945  	| 0.00819061400525211  	|
| N2_est_mean**  	| 0.15790366323142624  	| 0.0027319218647871226 	| 0.15611997567156302  	| 0.1388888888888889   	| 0.15968735079128946  	| 0.011296049270554422 	|
| NQ1_est_mean** 	| 0.011703390557228426 	| 9.602324782843738e-05 	| 0.011368985495924954 	| 0.011111111111111113 	| 0.012037795618531898 	| 0.028573348865720986 	|
| NQ2_est_mean** 	| 0.05558886545534271  	| 0.001465882590347345  	| 0.05428229076909933  	| 0.03888888888888889  	| 0.05689544014158609  	| 0.023504251715534986 	|
| T1_est_mean**  	| 1.0826203512712955   	| 0.035802829243693435  	| 1.076163164921904    	| 1.1111111111111112   	| 1.0890775376206872   	| 0.005964405104531062 	|
| T2_est_mean**  	| 1.4831604762862005   	| 0.13088812795903018   	| 1.4708142345954975   	| 1.3888888888888888   	| 1.4955067179769035   	| 0.008324279056854029 	|
| W1_est_mean  	| 0.10882740585855674  	| 0.007119788287703195  	| 0.10594789854272718  	| 0.11111111111111112  	| 0.1117069131743863   	| 0.026459394976041852 	|
| W1_est_var   	| 0.22467617077143     	| 0.11585231829200168   	| 0.21306069479919237  	| 0.2345679012345679   	| 0.23629164674366765  	| 0.051698744608098327 	|
| W2_est_mean**  	| 0.5064230743468859   	| 0.09132621845491772   	| 0.49611013688976857  	| 0.38888888888888884  	| 0.5167360118040033   	| 0.020364272442399148 	|

$k=200$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 200               	| 0                           	| 100000 	|


| metric       	| mean                 	| variance               	| lower_t              	| mean_analytical      	| upper_t             	| precision_t           	|
|--------------	|----------------------	|------------------------	|----------------------	|----------------------	|---------------------	|-----------------------	|
| N1_est_mean  	| 0.11147252566523072  	| 0.00017701016353712984 	| 0.11101849650340385  	| 0.11111111111111112  	| 0.11192655482705759 	| 0.004073014037471282  	|
| N2_est_mean**  	| 0.15398473991760248  	| 0.0006438593991865104  	| 0.15311881514071804  	| 0.1388888888888889   	| 0.1548506646944869  	| 0.00562344539691262   	|
| NQ1_est_mean 	| 0.011160091623576543 	| 2.1045041147974665e-05 	| 0.011003539293466737 	| 0.011111111111111113 	| 0.01131664395368635 	| 0.014027871400184376  	|
| NQ2_est_mean** 	| 0.05342503638610618  	| 0.00033202189927047704 	| 0.052803211625765574 	| 0.03888888888888889  	| 0.05404686114644678 	| 0.011639201438191511  	|
| T1_est_mean**  	| 1.1022894528378555   	| 0.009424833162462632   	| 1.0989764524865453   	| 1.1111111111111112   	| 1.1056024531891657  	| 0.003005562960600723  	|
| T2_est_mean** 	| 1.5174499594890396   	| 0.038137826838367556   	| 1.5107855355205027   	| 1.3888888888888888   	| 1.5241143834575765  	| 0.0043918574888499075 	|
| W1_est_mean  	| 0.10980648963759988  	| 0.0018207277649888776  	| 0.10835033615282791  	| 0.11111111111111112  	| 0.11126264312237186 	| 0.013261087660463411  	|
| W1_est_var   	| 0.2300473309656477   	| 0.02760527064474922    	| 0.22437736240135847  	| 0.2345679012345679   	| 0.23571729952993692 	| 0.02464696521576209   	|
| W2_est_mean**  	| 0.5227298925676994   	| 0.02591708214765869    	| 0.5172360311645425   	| 0.38888888888888884  	| 0.5282237539708563  	| 0.010509943053324321  	|

Aqui algumas das métricas da fila 1 começaram a convergir para dentro do intervalo de confiança(somente $E[T1]$ restante).

$k=500$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 500               	| 0                           	| 100000 	|


| metric       	| mean                 	| variance               	| lower_t              	| mean_analytical      	| upper_t              	| precision_t           	|
|--------------	|----------------------	|------------------------	|----------------------	|----------------------	|----------------------	|-----------------------	|
| N1_est_mean  	| 0.11108743772126242  	| 7.211490548663311e-05  	| 0.11079763853229778  	| 0.11111111111111112  	| 0.11137723691022706  	| 0.00260874852196873   	|
| N2_est_mean ** 	| 0.15304378469483787  	| 0.00023762005893810095 	| 0.15251773569888954  	| 0.1388888888888889   	| 0.1535698336907862   	| 0.0034372450798784925 	|
| NQ1_est_mean 	| 0.011046258925839447 	| 8.293393911935587e-06  	| 0.010947982174211031 	| 0.011111111111111113 	| 0.011144535677467862 	| 0.008896835778357988  	|
| NQ2_est_mean 	| 0.05291046040156728  	| 0.00011907268499860969 	| 0.052538076652698856 	| 0.03888888888888889  	| 0.0532828441504357   	| 0.007037998649835838  	|
| T1_est_mean  	| 1.1065560546118292   	| 0.004043236316851741   	| 1.1043861071991399   	| 1.1111111111111112   	| 1.1087260020245184   	| 0.0019609918572543886 	|
| T2_est_mean  	| 1.52274487616348     	| 0.014705407732070935   	| 1.5186065646274867   	| 1.3888888888888888   	| 1.5268831876994735   	| 0.0027176657106341593 	|
| W1_est_mean**  	| 0.1098028924752204   	| 0.0007372061627926137  	| 0.10887632057595893  	| 0.11111111111111112  	| 0.11072946437448188  	| 0.008438501740476216  	|
| W1_est_var**  	| 0.22962129221912964  	| 0.011289191697147857   	| 0.22599539014975287  	| 0.2345679012345679   	| 0.2332471942885064   	| 0.015790792022529632  	|
| W2_est_mean**  	| 0.5251302589328872   	| 0.009774836789320172   	| 0.5217563030174971   	| 0.38888888888888884  	| 0.5285042148482774   	| 0.006424988577588865  	|

$k=1000$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 1000              	| 0                           	| 100000 	|

| metric       	| mean                 	| variance               	| lower_t              	| mean_analytical      	| upper_t              	| precision_t           	|
|--------------	|----------------------	|------------------------	|----------------------	|----------------------	|----------------------	|-----------------------	|
| N1_est_mean  	| 0.111083889511161    	| 3.8162968758901215e-05 	| 0.11087307246581625  	| 0.11111111111111112  	| 0.11129470655650574  	| 0.0018978183629729552 	|
| N2_est_mean**  	| 0.1530121616932754   	| 0.00012543631600515616 	| 0.1526299567571128   	| 0.1388888888888889   	| 0.15339436662943798  	| 0.0024978729267857466 	|
| NQ1_est_mean 	| 0.011087656510165626 	| 4.1979818659273605e-06 	| 0.011017735945730064 	| 0.011111111111111113 	| 0.011157577074601188 	| 0.006306162566585225  	|
| NQ2_est_mean 	| 0.05287569201018222  	| 6.181431361768647e-05  	| 0.05260738675938784  	| 0.03888888888888889  	| 0.05314399726097659  	| 0.005074264574025943  	|
| T1_est_mean**  	| 1.1083229688833964   	| 0.0022300753710851494  	| 1.1067114165360463   	| 1.1111111111111112   	| 1.1099345212307465   	| 0.0014540457904375318 	|
| T2_est_mean** 	| 1.5256530744199008   	| 0.007832829867254325   	| 1.5226328167689192   	| 1.3888888888888888   	| 1.5286733320708825   	| 0.001979649044478883  	|
| W1_est_mean  	| 0.1105023496193425   	| 0.00037493309758278705 	| 0.10984156254931748  	| 0.11111111111111112  	| 0.1111631366893675   	| 0.005979846331786411  	|
| W1_est_var   	| 0.2322322135897731   	| 0.005631227017115324   	| 0.22967135165755992  	| 0.2345679012345679   	| 0.2347930755219863   	| 0.011027160670900012  	|
| W2_est_mean**  	| 0.5264801310487565   	| 0.0050488600764011455  	| 0.5240553009519858   	| 0.38888888888888884  	| 0.5289049611455271   	| 0.004605739046486695  	|

$k=5000$:

| confidence 	| utilization_pct 	| arrival_process 	| service_process 	| service_rate 	| number_of_rounds 	| samples_per_round 	| arrivals_until_steady_state 	| seed   	|
|------------	|-----------------	|-----------------	|-----------------	|--------------	|------------------	|-------------------	|-----------------------------	|--------	|
| 0.95       	| 0.2             	| exponential     	| exponential     	| 1.0          	| 3300             	| 5000              	| 0                           	| 100000 	|

| metric       	| mean                 	| variance               	| lower_t              	| mean_analytical      	| upper_t              	| precision_t           	|
|--------------	|----------------------	|------------------------	|----------------------	|----------------------	|----------------------	|-----------------------	|
| N1_est_mean  	| 0.11105599444159918  	| 1.0513565891406874e-05 	| 0.11094534234000143  	| 0.11111111111111112  	| 0.11116664654319693  	| 0.000996363160350933  	|
| N2_est_mean**  	| 0.15276255616216577  	| 2.9967361592145958e-05 	| 0.15257574238543647  	| 0.1388888888888889   	| 0.15294936993889507  	| 0.001222902924791176  	|
| NQ1_est_mean 	| 0.011116997422791508 	| 8.70071125978831e-07   	| 0.011085165562164594 	| 0.011111111111111113 	| 0.011148829283418423 	| 0.002863350544784147  	|
| NQ2_est_mean**	| 0.05277259437464203  	| 1.2602646818838903e-05 	| 0.052651446575404194 	| 0.03888888888888889  	| 0.05289374217387987  	| 0.0022956574463212595 	|
| T1_est_mean  	| 1.1100906578547818   	| 0.0007499835879656475  	| 1.1091560906730764   	| 1.1111111111111112   	| 1.1110252250364872   	| 0.0008418836561613438 	|
| T2_est_mean**  	| 1.5267897946825624   	| 0.0020879726390604916  	| 1.5252304323187083   	| 1.3888888888888888   	| 1.5283491570464165   	| 0.0010213340233770278 	|
| W1_est_mean  	| 0.1110986544786058   	| 7.878992315583499e-05  	| 0.11079574003295992  	| 0.11111111111111112  	| 0.11140156892425168  	| 0.00272653568188991   	|
| W1_est_var   	| 0.2344546942516595   	| 0.0011662239209602437  	| 0.23328929262758005  	| 0.2345679012345679   	| 0.23562009587573893  	| 0.004970690084918971  	|
| W2_est_mean** 	| 0.5272908391023556   	| 0.0010462876123667822  	| 0.5261869887817505   	| 0.38888888888888884  	| 0.5283946894229608   	| 0.0020934373191163888 	|

Alterando a seed:

### Número de rodadas

Ao final de cada rodada, são determinados os intervalos de confiança para a média e variância de cada métrica, a partir do estimador global(`self.__metric_estimators_simulation`). O calculo é feito iterativamente, e a simulação e encerrada somente quando não há nenhuma métrica em que a precisão está acima do `target_precision` informado para a porcentagem de confiança `confidence`.

Os cálculos usados para determinar os valores máximos e mínimos do intervalo de confiança estão no arquivo `src/utils/estimator.py`.

### Determinando a fase transiente

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

Da fila 2(fórmulas obtidas a partir do slide da aula 17):

$E[T] = {{E[U] + E[X_1] + E[X_2]} \over {1 - \rho}} = {{{\rho {1 \over \mu}} + (1 - \rho)(E[X_1] + E[X_2])} \over {({1-\rho_1})({1- \rho})}}$

$E[T_2] = {E[T] - E[T_1]}$

$E[W_2] = E[T_2] - E[X_2] = E[T_2] - E[X] = E[X_2] - {1 \over \mu}$

$E[N_2] = {\lambda E[T_2]} = {\lambda (E[T] - E[T_1])}$

$E[Nq_2] = \lambda E[W_2] = \lambda (E[T_2] - E[X_2]) = \lambda (E[T_2] - {1 \over \mu})$

Tenho então os valores obtidos analiticamente:

| rho 	| mu 	| E_W1                	| Var_W1             	| E_NQ1                	| E_T1               	| E_N1                	| E_W2                	| E_NQ2               	| E_T2               	| E_N2                	|
|-----	|----	|---------------------	|--------------------	|----------------------	|--------------------	|---------------------	|---------------------	|---------------------	|--------------------	|---------------------	|
| 0.2 	| 1  	| 0.11111111111111112 	| 0.2345679012345679 	| 0.011111111111111113 	| 1.1111111111111112 	| 0.11111111111111112 	| 0.38888888888888884 	| 0.03888888888888889 	| 1.3888888888888888 	| 0.1388888888888889  	|
| 0.4 	| 1  	| 0.25                	| 0.5625             	| 0.05                 	| 1.25               	| 0.25                	| 1.0833333333333335  	| 0.2166666666666667  	| 2.0833333333333335 	| 0.41666666666666674 	|
| 0.6 	| 1  	| 0.4285714285714286  	| 1.0408163265306123 	| 0.1285714285714286   	| 1.4285714285714286 	| 0.42857142857142855 	| 2.571428571428571   	| 0.7714285714285714  	| 3.571428571428571  	| 1.0714285714285714  	|
| 0.8 	| 1  	| 0.6666666666666667  	| 1.7777777777777781 	| 0.2666666666666667   	| 1.6666666666666667 	| 0.6666666666666667  	| 7.333333333333336   	| 2.9333333333333345  	| 8.333333333333336  	| 3.3333333333333344  	|
| 0.9 	| 1  	| 0.8181818181818181  	| 2.3057851239669422 	| 0.36818181818181817  	| 1.8181818181818181 	| 0.8181818181818181  	| 17.181818181818183  	| 7.731818181818182   	| 18.181818181818183 	| 8.181818181818183   	|

O arquivo com as funções para geração dos valores acima é o `utils/analitical_values.py`.

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

- Erro número do Python:
    Ao calcula o tempo de serviço restante do cliente pertencente a fila 2, as operações aritméticas resultavam em um erro numérico, que fazia com o que o tempo de serviço resultante(considerando todas as interrupções) fosse ligeiramente maior do que o obtido inicialmente para o cliente. Por exemplo:

    client 4, service time queue 2: 0.5497878190747206

    client 4, effective service time queue 2: 0.549787819074723

    client 5, service time queue 2: 0.5181251288306629
    
    client 5, effective service time queue 2: 0.5181251288306612

    Solução: Decimal?(https://docs.python.org/3/library/decimal.html#module-decimal)



## Instruções para execução do simulador

Para a execução, é necessário instalar a versão [versão 3.11.1 do Python](https://www.python.org/downloads/release/python-3111/)([link](https://www.python.org/downloads/release/python-3111/)).

Após a instalação, para realizar o download das dependências do projeto, executar o seguinte comando abaixo a partir da pasta raiz:

`pip install -r requirements.txt`

Para executar o simulador, executar o comando a seguir a partir da pasta raiz do projeto:

`python src/main.py`