import pandas as pd
import random 
import numpy as np

def isNaN(string):
    return string != string

df = pd.read_csv('codechef.csv')
useless = []
for index, row in df.iterrows():
	if isNaN(row['Country']) or isNaN(row['Institute']):
		useless.append(index)

df = df.drop(useless)
new_df = pd.DataFrame()
userIds = [i for i in range(df.shape[0])]
userRatings = [0 for i in range(df.shape[0])]
userQuizzes = [0 for i in range(df.shape[0])]
new_df['UserId'] = userIds
new_df['UserName'] = df['Username'].tolist()
new_df['Password'] = df['Username'].tolist()
new_df['Country'] = df['Country'].tolist()
new_df['Institute'] = df['Institute'].tolist()
new_df['UserRating'] = userRatings
new_df['UserNumQuiz'] = userQuizzes
new_df.to_csv('Processed Users.csv', index = False) 