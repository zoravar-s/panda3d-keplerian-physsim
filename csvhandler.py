import csv
def read_data(filename, cutoff):
    with open(filename, newline='', encoding="utf-8") as file:
        i=0
        data = []
        reader = csv.DictReader(file)
        for row in reader:
            i += 1
            if row["spect"] and float(row["mag"]) < cutoff:
                data.append([row["proper"], row["id"], row["ra"], row["dec"],row["mag"], row["spect"][0]])
    return(data)
