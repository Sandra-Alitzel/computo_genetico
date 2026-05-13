import os
import sys
import random
import copy
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go

from core.population import Population
from core.tree import Tree
from operators.crossover import subtree_crossover
from operators.mutation import subtree_mutation, node_mutation
from operators.selection import select
from utils.functions_sum import FUNCTIONS_EXP1, FUNCTIONS_EXP2
from problems.sum_problem import SumProblem


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def count_nodes(node):
    if node is None:
        return 0
    return 1 + sum(count_nodes(c) for c in node.children)


def tree_depth(node):
    if node is None or node.is_leaf():
        return 0
    return 1 + max((tree_depth(c) for c in node.children), default=0)


def tree_to_str(node):
    if node.is_leaf():
        return str(node.value)
    if len(node.children) == 2:
        return f"({tree_to_str(node.children[0])} {node.value} {tree_to_str(node.children[1])})"
    return f"{node.value}({tree_to_str(node.children[0])})"


def count_terminals_pop(individuals, terminal_set):
    counts = {t: 0 for t in terminal_set}
    for ind in individuals:
        for node in ind.tree.root.get_all_nodes():
            if node.is_leaf() and node.value in counts:
                counts[node.value] += 1
    return counts


# ─────────────────────────────────────────────
# GP RUNNER
# ─────────────────────────────────────────────

class GPRunner:
    def __init__(self, config):
        self.config = config
        self.generation = 0
        self.history = []
        self.done = False
        self.best_overall = None

        functions = FUNCTIONS_EXP1 if config["experiment"] == 1 else FUNCTIONS_EXP2
        self.functions = functions
        self.function_set = list(functions.keys())
        self.terminal_set = config["terminals"]
        self.problem = SumProblem(config["target"])

        self.population = Population(
            config["pop_size"],
            self.function_set,
            self.terminal_set,
            functions,
            config["max_depth"],
        )
        # Enforce max_nodes on initial population
        max_n = config["max_nodes"]
        for ind in self.population.individuals:
            attempts = 0
            while count_nodes(ind.tree.root) > max_n and attempts < 10:
                ind.tree = Tree(
                    self.function_set, self.terminal_set, functions, config["max_depth"]
                )
                attempts += 1

    def step(self):
        if self.done:
            return None

        self.population.evaluate(self.problem)
        self.population.individuals.sort(key=lambda ind: ind.fitness)

        best = self.population.individuals[0]
        if self.best_overall is None or best.fitness < self.best_overall.fitness:
            self.best_overall = copy.deepcopy(best)

        fitnesses = [ind.fitness for ind in self.population.individuals]
        avg_f = sum(fitnesses) / len(fitnesses)
        std_f = math.sqrt(sum((f - avg_f) ** 2 for f in fitnesses) / len(fitnesses))
        depths = [tree_depth(ind.tree.root) for ind in self.population.individuals]
        nodes_list = [count_nodes(ind.tree.root) for ind in self.population.individuals]
        term_counts = count_terminals_pop(self.population.individuals, self.terminal_set)

        stats = {
            "gen": self.generation,
            "best_fitness": best.fitness,
            "avg_fitness": avg_f,
            "std_fitness": std_f,
            "best_depth": tree_depth(best.tree.root),
            "avg_depth": sum(depths) / len(depths),
            "max_depth_pop": max(depths),
            "best_nodes": count_nodes(best.tree.root),
            "avg_nodes": sum(nodes_list) / len(nodes_list),
            "expression": tree_to_str(best.tree.root),
            "terminals": term_counts.copy(),
        }
        self.history.append(stats)

        if self.generation >= self.config["generations"] - 1:
            self.done = True
            return stats

        self._evolve()
        self.generation += 1
        return stats

    def _evolve(self):
        cfg = self.config
        elites = [copy.deepcopy(ind) for ind in self.population.individuals[: cfg["elitism"]]]
        new_pop = list(elites)

        while len(new_pop) < cfg["pop_size"]:
            p1 = select(self.population.individuals, cfg["selection"], cfg["temperature"], cfg["tournament_k"])
            p2 = select(self.population.individuals, cfg["selection"], cfg["temperature"], cfg["tournament_k"])

            if random.random() < cfg["crossover_rate"]:
                c1, c2 = subtree_crossover(p1, p2)
                if count_nodes(c1.tree.root) > cfg["max_nodes"]:
                    c1 = copy.deepcopy(p1)
                if count_nodes(c2.tree.root) > cfg["max_nodes"]:
                    c2 = copy.deepcopy(p2)
            else:
                c1, c2 = copy.deepcopy(p1), copy.deepcopy(p2)

            if random.random() < cfg["mutation_rate"]:
                c1m = self._mutate(c1)
                if count_nodes(c1m.tree.root) <= cfg["max_nodes"]:
                    c1 = c1m

            if random.random() < cfg["mutation_rate"]:
                c2m = self._mutate(c2)
                if count_nodes(c2m.tree.root) <= cfg["max_nodes"]:
                    c2 = c2m

            new_pop.append(c1)
            if len(new_pop) < cfg["pop_size"]:
                new_pop.append(c2)

        self.population.individuals = new_pop[: cfg["pop_size"]]

    def _mutate(self, individual):
        mt = self.config["mutation_type"]
        if mt == "Nodo":
            return node_mutation(individual, self.terminal_set, self.functions)
        if mt == "Subárbol":
            return subtree_mutation(
                individual, self.function_set, self.terminal_set, self.functions, self.config["max_depth"]
            )
        # Mixta: 50/50
        if random.random() < 0.5:
            return node_mutation(individual, self.terminal_set, self.functions)
        return subtree_mutation(
            individual, self.function_set, self.terminal_set, self.functions, self.config["max_depth"]
        )


# ─────────────────────────────────────────────
# CHART FACTORIES
# ─────────────────────────────────────────────

_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]


def _fig_base(title, x_label, y_label, height=310):
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
        margin=dict(t=40, b=30, l=50, r=20),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#fafafa"),
        xaxis=dict(gridcolor="#e5e5e5"),
        yaxis=dict(gridcolor="#e5e5e5"),
    )
    return fig


def fig_fitness(history, title="Evolución del Fitness"):
    gens = [h["gen"] for h in history]
    fig = _fig_base(title, "Generación", "|resultado − objetivo|")
    fig.add_trace(go.Scatter(x=gens, y=[h["best_fitness"] for h in history],
                             name="Mejor", line=dict(color="#2ecc71", width=2)))
    fig.add_trace(go.Scatter(x=gens, y=[h["avg_fitness"] for h in history],
                             name="Promedio", line=dict(color="#3498db", width=1.5, dash="dash")))
    return fig


def fig_terminals(history, terminal_set, title="Conteo de Terminales (Intrones)"):
    gens = [h["gen"] for h in history]
    fig = _fig_base(title, "Generación", "Conteo total en población")
    for i, t in enumerate(terminal_set):
        counts = [h["terminals"].get(t, 0) for h in history]
        fig.add_trace(go.Scatter(x=gens, y=counts, name=f"'{t}'",
                                 line=dict(color=_COLORS[i % len(_COLORS)], width=2)))
    return fig


def fig_depth(history, title="Profundidad de Árboles"):
    gens = [h["gen"] for h in history]
    fig = _fig_base(title, "Generación", "Profundidad")
    fig.add_trace(go.Scatter(x=gens, y=[h["best_depth"] for h in history],
                             name="Mejor árbol", line=dict(color="#9b59b6", width=2)))
    fig.add_trace(go.Scatter(x=gens, y=[h["avg_depth"] for h in history],
                             name="Promedio", line=dict(color="#e67e22", width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=gens, y=[h["max_depth_pop"] for h in history],
                             name="Máx. población", line=dict(color="#e74c3c", width=1, dash="dot")))
    return fig


def fig_diversity(history, title="Diversidad (Convergencia)"):
    gens = [h["gen"] for h in history]
    fig = _fig_base(title, "Generación", "Desv. Est. Fitness")
    fig.add_trace(go.Scatter(x=gens, y=[h["std_fitness"] for h in history],
                             name="σ Fitness", line=dict(color="#1abc9c", width=2),
                             fill="tozeroy", fillcolor="rgba(26,188,156,0.15)"))
    return fig


def fig_nodes(history, title="Tamaño de Árboles (Nodos)"):
    gens = [h["gen"] for h in history]
    fig = _fig_base(title, "Generación", "Nodos")
    fig.add_trace(go.Scatter(x=gens, y=[h["best_nodes"] for h in history],
                             name="Mejor árbol", line=dict(color="#f39c12", width=2)))
    fig.add_trace(go.Scatter(x=gens, y=[h["avg_nodes"] for h in history],
                             name="Promedio", line=dict(color="#95a5a6", width=1.5, dash="dash")))
    return fig


def fig_compare(hist_a, hist_b, la, lb, metric, y_label, title):
    fig = _fig_base(title, "Generación", y_label)
    if hist_a:
        gens = [h["gen"] for h in hist_a]
        fig.add_trace(go.Scatter(x=gens, y=[h[metric] for h in hist_a],
                                 name=la, line=dict(color="#3498db", width=2)))
    if hist_b:
        gens = [h["gen"] for h in hist_b]
        fig.add_trace(go.Scatter(x=gens, y=[h[metric] for h in hist_b],
                                 name=lb, line=dict(color="#e74c3c", width=2)))
    return fig


# ─────────────────────────────────────────────
# STREAMLIT APP
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="GP Simbólico — Suma",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Regresión Simbólica · Programación Genética")
st.caption("Experimentos de suma simbólica con análisis de intrones y comparación de métodos de selección.")

# ── SIDEBAR ──────────────────────────────────
with st.sidebar:
    st.header("Configuración")

    st.subheader("Experimento")
    exp_label = st.radio(
        "Conjunto de funciones F",
        ["Exp 1: F = {+}", "Exp 2: F = {+, ×}"],
        help="Exp 1 solo suma; Exp 2 agrega multiplicación.",
    )
    exp_num = 1 if "Exp 1" in exp_label else 2

    target = st.number_input("Objetivo (suma =)", value=10, min_value=0, max_value=10_000)

    st.subheader("Terminales")
    st.caption("Marca los terminales a incluir (0 actúa como intrón)")
    tcols = st.columns(4)
    t_flags = {}
    for i, tv in enumerate([0, 1, 2, 4]):
        t_flags[tv] = tcols[i].checkbox(str(tv), value=True, key=f"t{tv}")
    terminal_set = [tv for tv, on in t_flags.items() if on]
    if not terminal_set:
        terminal_set = [1, 2, 4]
        st.warning("Al menos un terminal requerido.")

    st.subheader("Parámetros del GP")
    pop_size     = st.slider("Tamaño de población",   50, 1000, 500, step=50)
    max_gens     = st.slider("Generaciones máximas",  10, 2000, 1000, step=10)
    max_depth    = st.slider("Profundidad máxima",     2,   12,   7)
    max_nodes    = st.slider("Nodos máximos",         16,  256, 128, step=16)
    cx_rate      = st.slider("Prob. cruzamiento",    0.0,  1.0, 0.9, step=0.05)
    mut_rate     = st.slider("Prob. mutación",        0.0,  1.0, 0.1, step=0.05)
    elitism_k    = st.number_input("Elitismo (top k)", 0, 20, 2)

    st.subheader("Operadores")
    mut_label = st.selectbox(
        "Tipo de mutación",
        ["Mixta (Nodo + Subárbol)", "Nodo", "Subárbol"],
    )
    mut_map = {"Mixta (Nodo + Subárbol)": "Mixta", "Nodo": "Nodo", "Subárbol": "Subárbol"}

    st.subheader("Selección (experimento individual)")
    sel_single = st.selectbox(
        "Método",
        ["Torneo", "Boltzmann", "Vasconcelos"],
        help="Torneo: presión selectiva alta | Boltzmann: temperatura | Vasconcelos: rango lineal",
    )
    k_single   = st.slider("k (Torneo)", 2, 20, 7) if sel_single == "Torneo"    else 7
    temp_single = st.slider("Temperatura (Boltzmann)", 0.01, 10.0, 1.0, step=0.01) \
                  if sel_single == "Boltzmann" else 1.0

    st.subheader("Visualización")
    update_freq = st.slider("Actualizar gráficas cada N gens", 1, 50, 10)

# ── CONFIG DICT ──────────────────────────────
base_config = dict(
    experiment   = exp_num,
    target       = int(target),
    terminals    = terminal_set,
    pop_size     = pop_size,
    generations  = max_gens,
    max_depth    = max_depth,
    max_nodes    = max_nodes,
    crossover_rate = cx_rate,
    mutation_rate  = mut_rate,
    elitism        = elitism_k,
    mutation_type  = mut_map[mut_label],
    update_freq    = update_freq,
    # selection fields filled per-tab below
    selection    = sel_single,
    temperature  = temp_single,
    tournament_k = k_single,
)

# ── TABS ─────────────────────────────────────
tab_single, tab_compare = st.tabs(
    ["Experimento Individual", "Comparación de Métodos"]
)

# ═════════════════════════════════════════════
# TAB 1 — SINGLE EXPERIMENT
# ═════════════════════════════════════════════
with tab_single:
    f_label = "{+}" if exp_num == 1 else "{+, ×}"
    st.subheader(f"Experimento {exp_num}  ·  F = {f_label}  ·  Objetivo = {target}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Población",    pop_size)
    m2.metric("Generaciones", max_gens)
    m3.metric("Terminales",   str(terminal_set))
    m4.metric("Selección",    sel_single)
    m5.metric("Mutación",     mut_map[mut_label])

    st.divider()

    run_btn = st.button("▶  Ejecutar", key="btn_single", type="primary", use_container_width=False)

    ph_prog     = st.empty()
    ph_status   = st.empty()
    ph_expr     = st.empty()

    col1, col2 = st.columns(2)
    ph_fit  = col1.empty()
    ph_term = col2.empty()
    ph_dep  = col1.empty()
    ph_div  = col2.empty()
    ph_node = col1.empty()

    def _refresh_single(hist, terminals):
        if not hist:
            return
        last = hist[-1]
        ph_status.info(
            f"**Gen {last['gen']}**  |  Fitness: `{last['best_fitness']:.4f}`  |  "
            f"Nodos: {last['best_nodes']}  |  Profundidad: {last['best_depth']}"
        )
        ph_expr.code(last["expression"], language=None)
        ph_fit.plotly_chart(fig_fitness(hist),                    use_container_width=True)
        ph_term.plotly_chart(fig_terminals(hist, terminals),       use_container_width=True)
        ph_dep.plotly_chart(fig_depth(hist),                      use_container_width=True)
        ph_div.plotly_chart(fig_diversity(hist),                  use_container_width=True)
        ph_node.plotly_chart(fig_nodes(hist),                     use_container_width=True)

    if run_btn:
        runner = GPRunner(base_config)
        bar = ph_prog.progress(0.0, text="Iniciando…")

        while not runner.done:
            stats = runner.step()
            if stats is None:
                break
            gen   = stats["gen"]
            total = base_config["generations"]

            if gen % update_freq == 0 or runner.done:
                bar = ph_prog.progress(min((gen + 1) / total, 1.0),
                                       text=f"Generación {gen + 1} / {total}")
                _refresh_single(runner.history, terminal_set)

        ph_prog.progress(1.0, text="Completado")
        st.session_state["hist_single"]  = runner.history
        st.session_state["best_single"]  = runner.best_overall

        if runner.best_overall and runner.best_overall.fitness == 0:
            st.success(f"Solución exacta encontrada en generación {runner.history[-1]['gen']}!")
        else:
            bf = runner.best_overall.fitness if runner.best_overall else float("inf")
            st.info(f"Finalizado · Mejor fitness: {bf:.4f}")

    elif "hist_single" in st.session_state:
        ph_prog.progress(1.0, text="Resultado anterior")
        _refresh_single(st.session_state["hist_single"], terminal_set)


# ═════════════════════════════════════════════
# TAB 2 — COMPARISON
# ═════════════════════════════════════════════
with tab_compare:
    st.subheader("Comparación de Métodos de Selección")
    st.caption(
        "Mismo experimento, mismos parámetros, dos métodos de selección distintos. "
        "Los experimentos corren en paralelo generación a generación."
    )

    ca, cb = st.columns(2)
    with ca:
        st.markdown("**Método A**")
        sel_a   = st.selectbox("Selección A", ["Torneo", "Boltzmann", "Vasconcelos"], key="sel_a")
        k_a     = st.slider("k A", 2, 20, 7, key="ka")    if sel_a == "Torneo"     else 7
        temp_a  = st.slider("Temp A", 0.01, 10.0, 1.0, step=0.01, key="ta") if sel_a == "Boltzmann" else 1.0

    with cb:
        st.markdown("**Método B**")
        sel_b   = st.selectbox("Selección B", ["Boltzmann", "Vasconcelos", "Torneo"], key="sel_b")
        k_b     = st.slider("k B", 2, 20, 7, key="kb")    if sel_b == "Torneo"     else 7
        temp_b  = st.slider("Temp B", 0.01, 10.0, 1.0, step=0.01, key="tb") if sel_b == "Boltzmann" else 1.0

    cmp_btn = st.button("Comparar métodos", key="btn_cmp", type="primary")

    ph_cprog   = st.empty()
    ph_cstatus = st.empty()

    st.markdown("---")
    st.markdown("#### Vista individual por método")
    cla, clb = st.columns(2)
    ph_fa   = cla.empty();  ph_fb   = clb.empty()
    ph_ta   = cla.empty();  ph_tb   = clb.empty()
    ph_da   = cla.empty();  ph_db   = clb.empty()

    st.markdown("#### Comparación directa")
    ph_cfit  = st.empty()
    ph_cdep  = st.empty()
    ph_cdiv  = st.empty()
    ph_cnode = st.empty()

    def _refresh_compare(ha, hb, la, lb, terminals):
        if ha:
            ph_fa.plotly_chart(fig_fitness(ha,   f"Fitness — {la}"),    use_container_width=True)
            ph_ta.plotly_chart(fig_terminals(ha, terminals, f"Terminales — {la}"), use_container_width=True)
            ph_da.plotly_chart(fig_depth(ha,     f"Profundidad — {la}"), use_container_width=True)
        if hb:
            ph_fb.plotly_chart(fig_fitness(hb,   f"Fitness — {lb}"),    use_container_width=True)
            ph_tb.plotly_chart(fig_terminals(hb, terminals, f"Terminales — {lb}"), use_container_width=True)
            ph_db.plotly_chart(fig_depth(hb,     f"Profundidad — {lb}"), use_container_width=True)
        if ha and hb:
            ph_cfit.plotly_chart(
                fig_compare(ha, hb, la, lb, "best_fitness",  "|resultado − objetivo|", "Mejor Fitness"),
                use_container_width=True)
            ph_cdep.plotly_chart(
                fig_compare(ha, hb, la, lb, "avg_depth",     "Profundidad promedio",   "Profundidad de Árbol"),
                use_container_width=True)
            ph_cdiv.plotly_chart(
                fig_compare(ha, hb, la, lb, "std_fitness",   "Desv. Est. Fitness",     "Diversidad"),
                use_container_width=True)
            ph_cnode.plotly_chart(
                fig_compare(ha, hb, la, lb, "avg_nodes",     "Nodos promedio",         "Tamaño de Árboles"),
                use_container_width=True)

    if cmp_btn:
        cfg_a = {**base_config, "selection": sel_a, "temperature": temp_a, "tournament_k": k_a}
        cfg_b = {**base_config, "selection": sel_b, "temperature": temp_b, "tournament_k": k_b}

        runner_a = GPRunner(cfg_a)
        runner_b = GPRunner(cfg_b)

        bar_c = ph_cprog.progress(0.0, text="Comparando…")
        total  = base_config["generations"]

        for step_i in range(total):
            if not runner_a.done:
                runner_a.step()
            if not runner_b.done:
                runner_b.step()

            if runner_a.done and runner_b.done:
                break

            if step_i % update_freq == 0:
                fa = runner_a.history[-1]["best_fitness"] if runner_a.history else float("inf")
                fb = runner_b.history[-1]["best_fitness"] if runner_b.history else float("inf")
                bar_c = ph_cprog.progress(
                    min((step_i + 1) / total, 1.0),
                    text=f"Gen {step_i + 1} / {total}",
                )
                ph_cstatus.info(
                    f"**{sel_a}**: fitness = `{fa:.4f}`  |  "
                    f"**{sel_b}**: fitness = `{fb:.4f}`"
                )
                _refresh_compare(runner_a.history, runner_b.history, sel_a, sel_b, terminal_set)

        ph_cprog.progress(1.0, text="Comparación completada")
        _refresh_compare(runner_a.history, runner_b.history, sel_a, sel_b, terminal_set)

        st.session_state["hist_cmp_a"]  = runner_a.history
        st.session_state["hist_cmp_b"]  = runner_b.history
        st.session_state["best_cmp_a"]  = runner_a.best_overall
        st.session_state["best_cmp_b"]  = runner_b.best_overall
        st.session_state["cmp_labels"]  = (sel_a, sel_b)

        # Summary
        st.divider()
        st.subheader("Resumen final")
        sa, sb = st.columns(2)
        ba = runner_a.best_overall
        bb = runner_b.best_overall

        def _conv_gen(hist):
            for h in hist:
                if h["best_fitness"] == 0:
                    return h["gen"]
            return hist[-1]["gen"] if hist else "-"

        with sa:
            st.markdown(f"**{sel_a}**")
            st.metric("Mejor fitness", f"{ba.fitness:.4f}" if ba else "—")
            st.metric("Generaciones ejecutadas", len(runner_a.history))
            st.metric("Gen. de convergencia (fitness=0)", _conv_gen(runner_a.history))
            st.metric("Profundidad final", runner_a.history[-1]["best_depth"] if runner_a.history else "—")
            if ba:
                st.code(tree_to_str(ba.tree.root), language=None)

        with sb:
            st.markdown(f"**{sel_b}**")
            st.metric("Mejor fitness", f"{bb.fitness:.4f}" if bb else "—")
            st.metric("Generaciones ejecutadas", len(runner_b.history))
            st.metric("Gen. de convergencia (fitness=0)", _conv_gen(runner_b.history))
            st.metric("Profundidad final", runner_b.history[-1]["best_depth"] if runner_b.history else "—")
            if bb:
                st.code(tree_to_str(bb.tree.root), language=None)

    elif "hist_cmp_a" in st.session_state:
        ha = st.session_state["hist_cmp_a"]
        hb = st.session_state["hist_cmp_b"]
        la, lb = st.session_state.get("cmp_labels", (sel_a, sel_b))
        ph_cprog.progress(1.0, text="Resultado anterior")
        _refresh_compare(ha, hb, la, lb, terminal_set)
