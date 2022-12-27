import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

event_list_raw = pd.read_csv('event_list_raw.csv')

metrics = {
    'q_1_size': [0],
    'q_1_timestamp': [0],
    'q_2_size': [0],
    'q_2_timestamp': [0]
}

rounds = list(event_list_raw['round'].unique())

offset = 0

for round in rounds:
    events_round = event_list_raw[event_list_raw['round'] == round]

    for index, row in events_round.iterrows():
        tt = float(row['timestamp'])

        if(int(row['queue_number']) == 1 and str(row['reference']) == 'enqueue'):
            metrics['q_1_timestamp'].append(tt + offset)
            metrics['q_1_size'].append(metrics['q_1_size'][len(metrics['q_1_size'])-1] + 1)
        elif(int(row['queue_number']) == 1 and str(row['reference']) == 'dequeue'):
            metrics['q_1_timestamp'].append(tt + offset)
            metrics['q_1_size'].append(metrics['q_1_size'][len(metrics['q_1_size'])-1] - 1)
        elif(int(row['queue_number']) == 2 and str(row['reference']) == 'enqueue'):
            metrics['q_2_timestamp'].append(tt + offset)
            metrics['q_2_size'].append(metrics['q_2_size'][len(metrics['q_2_size'])-1] + 1)
        elif(int(row['queue_number']) == 2 and str(row['reference']) == 'dequeue'):
            metrics['q_2_timestamp'].append(tt + offset)
            metrics['q_2_size'].append(metrics['q_2_size'][len(metrics['q_2_size'])-1] - 1)
    
    offset = offset + metrics['q_2_timestamp'][len(metrics['q_2_timestamp']) - 1]

    plt.scatter(metrics['q_1_timestamp'], metrics['q_1_size'], color='blue')
    plt.scatter(metrics['q_2_timestamp'], metrics['q_2_size'], color='red')

plt.xlabel('Time(seconds)')
plt.ylabel('Queue size')

plt.savefig('./queue_sizes.png')
