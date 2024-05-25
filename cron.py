import pandas as pd
import datetime
import os

df = pd.read_csv('test.csv')
sampleData = df.sample(n=100)
dir1 = "stats"
curr_time = datetime.datetime.now()
newFile = os.path.join(dir1, f"{curr_time}.csv")
sampleData.to_csv(newFile, index=False)
