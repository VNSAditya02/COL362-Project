import pandas as pd
import random 

df = pd.read_csv('JEOPARDY1.csv')
# df = df[:1000]
grouped_question = df.groupby('Category')

new_df = pd.DataFrame()
options = ["" for i in range(df.shape[0])]
new_df['Category'] = df['Category']
new_df['Question'] = df['Question']
new_df['Answer'] = df['Answer']
new_df['Option1'] = options
new_df['Option2'] = options
new_df['Option3'] = options
new_df['Option4'] = options

useless = []
for index, row in new_df.iterrows():
	print(index)
	temp = grouped_question.get_group(row['Category'])['Answer'].tolist()
	if len(temp) < 10 or 'href' in row['Question']:
		useless.append(index)
		continue
	all_options = random.sample(temp, 3)
	while(row['Answer'] in all_options):
		all_options = random.sample(temp, 3)
	all_options = all_options + [row['Answer']]

	random.shuffle(all_options)
	new_df.at[index, 'Option1'] = all_options[0]
	new_df.at[index, 'Option2'] = all_options[1]
	new_df.at[index, 'Option3'] = all_options[2]
	new_df.at[index, 'Option4'] = all_options[3]

new_df = new_df.drop(useless)

CategoryNames = (new_df['Category'].drop_duplicates()).tolist()
CategoryIds = [i for i in range(len(CategoryNames))]
new_df2 = pd.DataFrame()
new_df2['CategoryId'] = CategoryIds
new_df2['CategoryName'] = CategoryNames
new_df2.to_csv('Categories.csv', index = False)

Indices = []
for index, row in new_df.iterrows():
	Indices.append(CategoryIds[CategoryNames.index(row['Category'])])

final_df = pd.DataFrame()
qids = [i for i in range(new_df.shape[0])]
final_df['QuestionId'] = qids
final_df['CategoryId'] = Indices
final_df['Question'] = new_df['Question'].tolist()
final_df['Answer'] = new_df['Answer'].tolist()
final_df['Option1'] = new_df['Option1'].tolist()
final_df['Option2'] = new_df['Option2'].tolist()
final_df['Option3'] = new_df['Option3'].tolist()
final_df['Option4'] = new_df['Option4'].tolist()

final_df.to_csv('Processed Questions.csv', index = False)

# new_df2 = pd.DataFrame()
# new_df2['Category'] = df['Category']
# new_df2 = new_df2.drop_duplicates()
# print(new_df2.iloc[13]['Category'])
# new_df2.to_csv('Categories.csv', index = False)