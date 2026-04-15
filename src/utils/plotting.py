import matplotlib.pyplot as plt
import numpy as np

def plot_fitness(history, title="Evolución del fitness", filename=None):
    generations = list(range(len(history)))

    plt.figure()
    plt.plot(generations, history)
    plt.xlabel("Generaciones")
    plt.ylabel("Fitness")
    plt.title(title)

    if filename:
        plt.savefig(filename)

    plt.show()


def plot_comparison(history1, history2, label1="F1", label2="F2", filename=None):
    generations = list(range(len(history1)))
    plt.figure()
    plt.plot(generations, history1)
    plt.plot(generations, history2)

    plt.xlabel("Generaciones")
    plt.ylabel("Fitness")
    plt.title("Comparación de configuraciones")

    plt.legend([label1, label2])

    if filename:
        plt.savefig(filename)

    plt.show()

def plot_average(history, title="Promedio"):
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(history)
    plt.xlabel("Generaciones")
    plt.ylabel("Fitness")
    plt.title(title)
    plt.show()

def plot_function_frequency(counter):
    import matplotlib.pyplot as plt

    names = list(counter.keys())
    values = list(counter.values())

    plt.figure()
    plt.bar(names, values)
    plt.xlabel("Funciones")
    plt.ylabel("Frecuencia")
    plt.title("Uso de funciones")
    plt.show()

def plot_tree_sizes(size1, size2):
    import matplotlib.pyplot as plt

    plt.figure()
    plt.bar(["F1", "F2"], [size1, size2])
    plt.title("Tamaño de árboles")
    plt.ylabel("Nodos")
    plt.show()

def plot_regression(tree, data, title="Regresión", filename=None):
    x_real = [row["x"] for row in data]
    y_real = [row["y"] for row in data]

    # ordenar datos reales
    sorted_pairs = sorted(zip(x_real, y_real), key=lambda x: x[0])
    x_real, y_real = zip(*sorted_pairs)

    x_model = np.linspace(min(x_real), max(x_real), 100)
    y_model = []

    for x in x_model:
        try:
            y_pred = tree.evaluate({"x": float(x)})

            # asegurar que sea número
            if isinstance(y_pred, (int, float)):
                y_model.append(y_pred)
            else:
                y_model.append(np.nan)

        except:
            y_model.append(np.nan)

    # asegurar mismo tamaño
    if len(y_model) != len(x_model):
        print("Error: tamaños diferentes en modelo")
        return

    plt.figure()
    plt.scatter(x_real, y_real)
    plt.plot(x_model, y_model)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(title)

    if filename:
        plt.savefig(filename)

    plt.show()





