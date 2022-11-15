import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

event_list_raw = pd.read_csv('event_list_raw.csv')

#enqueue_dequeue_events = event_list_raw[(event_list_raw['reference'] == 'enqueue' | event_list_raw['reference'] == 'dequeue') & event_list_raw['queue_number'] == 1]

metrics = {
    'q_1_size': [0],
    'q_1_timestamp': [0],
    'q_2_size': [0],
    'q_2_timestamp': [0]
}

for index, row in event_list_raw.iterrows():
    tt = float(row['timestamp'])

    if(int(row['queue_number']) == 1 and str(row['reference']) == 'enqueue'):
        metrics['q_1_timestamp'].append(tt)
        metrics['q_1_size'].append(metrics['q_1_size'][len(metrics['q_1_size'])-1] + 1)
    elif(int(row['queue_number']) == 1 and str(row['reference']) == 'dequeue'):
        metrics['q_1_timestamp'].append(tt)
        metrics['q_1_size'].append(metrics['q_1_size'][len(metrics['q_1_size'])-1] - 1)
    elif(int(row['queue_number']) == 2 and str(row['reference']) == 'enqueue'):
        metrics['q_2_timestamp'].append(tt)
        metrics['q_2_size'].append(metrics['q_2_size'][len(metrics['q_2_size'])-1] + 1)
    elif(int(row['queue_number']) == 2 and str(row['reference']) == 'dequeue'):
        metrics['q_2_timestamp'].append(tt)
        metrics['q_2_size'].append(metrics['q_2_size'][len(metrics['q_2_size'])-1] - 1)

plt.plot(metrics['q_1_timestamp'], metrics['q_1_size'], color='blue')
plt.plot(metrics['q_2_timestamp'], metrics['q_2_size'], color='red')

plt.xlabel('Time(seconds)')
plt.ylabel('Queue size')

plt.savefig('./queue_sizes.png')
