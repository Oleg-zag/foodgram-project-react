import csv

path = 'D:/Dev/foodgram-project-react/data/ingredients.csv'

with open(path, encoding="UTF8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
