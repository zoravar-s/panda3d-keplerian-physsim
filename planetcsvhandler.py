import csv
def read_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)    
    return(data)
