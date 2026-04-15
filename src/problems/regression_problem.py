import csv

class RegressionProblem:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)

    def load_data(self, file_path):
        data = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)

            header = next(reader)  # saltar encabezado

            for row in reader:
                x = float(row[0])
                y = float(row[1])

                data.append({"x": x, "y": y})

        return data

    def fitness(self, tree):
        errors = []

        for row in self.data:
            context = {"x": row["x"]}
            expected = row["y"]

            try:
                prediction = tree.evaluate(context)
            except:
                prediction = 1e6

            if prediction is None:
                prediction = 1e6

            error = (prediction - expected) ** 2
            errors.append(error)

        return sum(errors) / len(errors)


