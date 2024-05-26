import pandas as pd
import random
from datetime import datetime
import os

file = "quarry-82283-wikimedia-incubator-stats-run855927.csv"
df = pd.read_csv(file)
sample = df.sample(n=100)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

dir = "/stats/"
os.makedirs("/stats/",exist_ok=True)
new = os.path.join(dir, f"{timestamp}.csv")
print(df.to_csv(new,index=False))