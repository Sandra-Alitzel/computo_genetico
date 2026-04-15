import csv

class BooleanProblem:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)

    def load_data(self, file_path):
        data = []
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convertir a enteros
                parsed_row = {k: int(v) for k, v in row.items()}
                data.append(parsed_row)
               
        return data


    def fitness(self, tree):
        """
        Calcula número de errores
        """
        errors = 0


        for row in self.data:
            # separar entradas y salida
            context = {k: row[k] for k in row if k != "S"}
            expected = row["S"]


            prediction = tree.evaluate(context)


            if prediction != expected:
                errors += 1


        return errors



