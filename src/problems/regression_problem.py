import csv
import math

class RegressionProblem:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)

    def load_data(self, file_path):
        data = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # saltar encabezado (X, Y, Z)

            for row in reader:
                if not row: continue
                # En tu CSV: row[0]=X, row[1]=Y, row[2]=Z
                x = float(row[0])
                y = float(row[1])
                z = float(row[2]) 

                data.append({"x": x, "y": y, "z": z})
        return data

    def fitness(self, tree):
        errors = []
        MAX_ERROR = 1e6  # Techo para evitar Overflows

        for row in self.data:
            # Contexto con ambas variables para regresión de superficie
            context = {"x": row["x"], "y": row["y"]}
            expected = row["z"]

            try:
                prediction = tree.evaluate(context)
                
                # LIMITADOR: Si la predicción se sale de control, la cortamos
                prediction = max(min(prediction, 250), -250)
                
                # Verificaciones de seguridad post-evaluación
                if prediction is None or math.isnan(prediction) or math.isinf(prediction):
                    error = MAX_ERROR
                else:
                    # Calculamos el error cuadrático
                    diff = prediction - expected
                    error = diff ** 2
                    
                    # Si el error es más grande de lo que Python maneja cómodamente
                    if error > MAX_ERROR:
                        error = MAX_ERROR

            except OverflowError:
                error = MAX_ERROR
            except ZeroDivisionError:
                error = MAX_ERROR
            except Exception:
                error = MAX_ERROR

            errors.append(error)

        # Retornamos el MSE (Mean Squared Error) limitado
        return sum(errors) / len(errors)