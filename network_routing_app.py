import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# Set up Streamlit page config
st.set_page_config(page_title="ConnectFlow: Network Routing", layout="wide")
st.title("🌐 ConnectFlow: Animated Network Routing Simulator")

# Function to generate a random connected graph
def generate_connected_graph(num_nodes=10, extra_edges=5):
    G = nx.Graph()

    # Add nodes
    for i in range(num_nodes):
        G.add_node(i)

    # Create a minimum spanning tree to ensure connectivity
    nodes = list(G.nodes())
    random.shuffle(nodes)
    for i in range(1, len(nodes)):
        u = nodes[i]
        v = nodes[random.randint(0, i - 1)]
        weight = random.randint(1, 10)
        G.add_edge(u, v, weight=weight)

    # Add some extra edges
    edges_added = 0
    while edges_added < extra_edges:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            weight = random.randint(1, 10)
            G.add_edge(u, v, weight=weight)
            edges_added += 1

    return G

# Draw the graph with optional highlight path
def draw_graph(G, path=[], animate=False):
    pos = nx.spring_layout(G, seed=42)
    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw all nodes and edges
    nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightgray', edge_color='gray', node_size=700)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Animate path
    if path and not animate:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='blue', width=3)

    st.pyplot(fig)
    
    if animate:
        for i in range(1, len(path)):
            fig, ax = plt.subplots(figsize=(8, 6))
            nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightgray', edge_color='gray', node_size=700)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
            nx.draw_networkx_edges(G, pos, edgelist=list(zip(path[:i], path[1:i+1])), edge_color='blue', width=3)
            st.pyplot(fig)
            time.sleep(0.5)

# Run Dijkstra and return path + cost
def run_dijkstra(G, source, target):
    path = nx.dijkstra_path(G, source=source, target=target, weight='weight')
    cost = nx.dijkstra_path_length(G, source=source, target=target, weight='weight')
    return path, cost

# UI - Sidebar
st.sidebar.header("⚙ Configuration")

# Generate the graph
num_routers = st.sidebar.slider("Number of Routers", 5, 20, 10)
extra_edges = st.sidebar.slider("Extra Random Connections", 0, 10, 4)

if "graph" not in st.session_state or st.sidebar.button("🔁 Generate New Topology"):
    st.session_state.graph = generate_connected_graph(num_routers, extra_edges)

G = st.session_state.graph
routers = list(G.nodes())
router_names = [f"Router{i}" for i in routers]
router_mapping = dict(zip(router_names, routers))

source = st.sidebar.selectbox("Choose Source Router", router_names)
destination = st.sidebar.selectbox("Choose Destination Router", router_names)

# Avoid source = destination
if source == destination:
    st.warning("Source and Destination should be different.")
    draw_graph(G)
else:
    # Main UI
    st.subheader("🖼 Network Topology")
    draw_graph(G)

    if st.button("🚀 Start Routing"):
        with st.spinner("Finding path using Dijkstra’s Algorithm..."):
            path, cost = run_dijkstra(G, router_mapping[source], router_mapping[destination])
            readable_path = " → ".join([f"Router{n}" for n in path])
            st.success(f"✅ Best Path: {readable_path}")
            st.info(f"📍 Total Cost: {cost} ms")
            st.subheader("🔵 Routing Animation")
            draw_graph(G, path, animate=True)
