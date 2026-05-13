import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

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


def plot_surface_3d(tree, data, title="Comparación de Superficies", filename=None):
    """
    Grafica superficies 3D: datos reales vs predicción del modelo.
    
    Args:
        tree: Árbol de expresión GP
        data: Lista de diccionarios con 'x', 'y', 'z'
        title: Título de la figura
        filename: Nombre archivo para guardar (opcional)
    """
    # Extraer coordenadas de los datos
    x_data = np.array([row["x"] for row in data])
    y_data = np.array([row["y"] for row in data])
    z_data = np.array([row["z"] for row in data])
    
    # Crear malla regular para interpolación y predicción
    x_min, x_max = x_data.min(), x_data.max()
    y_min, y_max = y_data.min(), y_data.max()
    
    # Crear grid más fino para mejor visualización
    x_grid = np.linspace(x_min, x_max, 50)
    y_grid = np.linspace(y_min, y_max, 50)
    X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
    
    # ===== SUPERFICIE REAL: Interpolar datos =====
    points = np.array([x_data, y_data]).T
    Z_real = griddata(points, z_data, (X_grid, Y_grid), method='cubic', fill_value=np.nan)
    
    # ===== SUPERFICIE PREDICHA: Evaluar árbol en cada punto =====
    Z_pred = np.zeros_like(X_grid)
    MAX_ERROR = 1e10
    
    for i in range(X_grid.shape[0]):
        for j in range(X_grid.shape[1]):
            x_val = X_grid[i, j]
            y_val = Y_grid[i, j]
            try:
                z_pred = tree.evaluate({"x": float(x_val), "y": float(y_val)})
                if isinstance(z_pred, (int, float)) and not np.isnan(z_pred) and not np.isinf(z_pred):
                    Z_pred[i, j] = z_pred
                else:
                    Z_pred[i, j] = np.nan
            except:
                Z_pred[i, j] = np.nan
    
    # ===== PLOTEO DE SUPERFICIES =====
    fig = plt.figure(figsize=(16, 5))
    
    # Subplot 1: Superficie Real
    ax1 = fig.add_subplot(131, projection='3d')
    surf_real = ax1.plot_surface(X_grid, Y_grid, Z_real, cmap='viridis', alpha=0.8)
    ax1.scatter(x_data, y_data, z_data, c='red', s=20, alpha=0.5, label='Puntos datos')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title('Superficie Real')
    fig.colorbar(surf_real, ax=ax1, label='Z')
    
    # Subplot 2: Superficie Predicha
    ax2 = fig.add_subplot(132, projection='3d')
    surf_pred = ax2.plot_surface(X_grid, Y_grid, Z_pred, cmap='plasma', alpha=0.8)
    ax2.scatter(x_data, y_data, z_data, c='red', s=20, alpha=0.5, label='Puntos datos')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.set_title('Superficie Predicha')
    fig.colorbar(surf_pred, ax=ax2, label='Z')
    
    # Subplot 3: Diferencia (Error)
    ax3 = fig.add_subplot(133, projection='3d')
    Z_diff = np.abs(Z_real - Z_pred)
    surf_diff = ax3.plot_surface(X_grid, Y_grid, Z_diff, cmap='coolwarm', alpha=0.8)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_zlabel('Error Absoluto')
    ax3.set_title('Error Absoluto')
    fig.colorbar(surf_diff, ax=ax3, label='|Error|')
    
    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    plt.show()
    
    # Retornar estadísticas de error
    valid_errors = Z_diff[~np.isnan(Z_diff)]
    if len(valid_errors) > 0:
        mse = np.mean((Z_real - Z_pred) ** 2)
        mae = np.mean(valid_errors)
        rmse = np.sqrt(mse)
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'max_error': np.max(valid_errors),
            'min_error': np.min(valid_errors)
        }
    return None


def plot_surface_3d_combined(tree, data, title="Superficies Comparadas", filename=None):
    """
    Alternativa: Grafica ambas superficies en perspectiva similar para comparación directa.
    """
    x_data = np.array([row["x"] for row in data])
    y_data = np.array([row["y"] for row in data])
    z_data = np.array([row["z"] for row in data])
    
    x_min, x_max = x_data.min(), x_data.max()
    y_min, y_max = y_data.min(), y_data.max()
    
    x_grid = np.linspace(x_min, x_max, 40)
    y_grid = np.linspace(y_min, y_max, 40)
    X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
    
    # Superficie Real
    points = np.array([x_data, y_data]).T
    Z_real = griddata(points, z_data, (X_grid, Y_grid), method='cubic', fill_value=np.nan)
    
    # Superficie Predicha
    Z_pred = np.zeros_like(X_grid)
    for i in range(X_grid.shape[0]):
        for j in range(X_grid.shape[1]):
            try:
                z_pred = tree.evaluate({"x": float(X_grid[i, j]), "y": float(Y_grid[i, j])})
                if isinstance(z_pred, (int, float)) and not np.isnan(z_pred) and not np.isinf(z_pred):
                    Z_pred[i, j] = z_pred
                else:
                    Z_pred[i, j] = np.nan
            except:
                Z_pred[i, j] = np.nan
    
    # Normalizar a la misma escala
    z_min = np.nanmin([Z_real.min(), Z_pred.min()])
    z_max = np.nanmax([Z_real.max(), Z_pred.max()])
    
    fig = plt.figure(figsize=(14, 6))
    
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(X_grid, Y_grid, Z_real, cmap='viridis', alpha=0.8)
    ax1.set_zlim(z_min, z_max)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    ax1.set_title('Datos Reales')
    
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot_surface(X_grid, Y_grid, Z_pred, cmap='viridis', alpha=0.8)
    ax2.set_zlim(z_min, z_max)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.set_title('Predicción del Modelo')
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    plt.show()
