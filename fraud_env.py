import matplotlib.pyplot as plt
import networkx as nx

class FraudEnv():
    def __init__(self):
        # init graph
        self.G = nx.DiGraph()

        self.NODE_TEMPLATES = {
            "individual": {
                "role": None,
            },
            "fraudster": {
                "role": None,
                "status": "active",
                "description": None,
            },
            "bank": {
            },
            "account": {
                "owner": None,
                "bank": None,
                "balance": 0.0,
                "status": "active",  # could be 'active', 'flagged', 'frozen', etc.
                "compromised": False
            }
        }
    
    def add_node_with_attribute(self, node_id, node_type, custom_attrs=None):
        if node_type not in self.NODE_TEMPLATES:
            raise ValueError(f"Unknown node type: '{node_type}'")
        attr = self.NODE_TEMPLATES[node_type].copy()
        if custom_attrs:
            invalid_attr = [i for i in custom_attrs if i not in attr]
            if invalid_attr:
                raise ValueError(f"Invalid keys: {invalid_attr}")
            attr.update(custom_attrs)
        self.G.add_node(node_id, **attr)
        print(f"Successfully added node {node_id} as a {node_type} node.")

    def add_ownership_edge(self, node_id1, node_id2):
        self.G.add_edge(node_id1, node_id2, rel="owns")
        print(f"Added ownership relationship between {node_id1} -> {node_id2}")

    def get_nodes(self):
        return list(self.G.nodes(data=True))

    def get_edges(self):
        return list(self.G.edges(data=True))

    def get_graph(self):
        return self.G

    def reset(self):
        self.G.clear()
        print("Graph has been reset.")

    def __str__(self):
        return f"FraudEnv with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges."
    
    def draw_graph(self):
        pos = nx.spring_layout(self.G, k = 0.5)
        plt.figure(figsize=(8, 6))
        nx.draw_networkx_nodes(self.G, pos, node_color='lightblue', node_size=800)
        nx.draw_networkx_labels(self.G, pos, font_size=9)
        nx.draw_networkx_edges(self.G, pos, arrows=True, arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels={(u, v): d.get('rel', '') for u, v, d in self.G.edges(data=True)}, font_size = 9)
        plt.axis('off')
        plt.show()


# Testing
if __name__ == "__main__":
    env1 = FraudEnv()

    # Add banks
    env1.add_node_with_attribute("BankOfAmerica", "bank")
    env1.add_node_with_attribute("Chase", "bank")
    env1.add_node_with_attribute("FirstFinancial", "bank")

    # Add individuals
    env1.add_node_with_attribute("Olivia", "individual", {"role": "victim"})
    env1.add_node_with_attribute("Betty", "individual", {"role": "victim"})

    # Add fraudsters
    env1.add_node_with_attribute("ScamGov", "fraudster", {"role": "fraudco", "status": "active", "description": "Impersonates gov for SID"})
    env1.add_node_with_attribute("ScamCo", "fraudster", {"role": "fraudco", "status": "active", "description": "Impersonates gov for SID"})

    # Add accounts (using valid banks)
    env1.add_node_with_attribute("acc_olivia", "account", {"owner": "Olivia", "bank": "BankOfAmerica", "balance": 60000.00})
    env1.add_node_with_attribute("acc_betty", "account", {"owner": "Betty", "bank": "Chase", "balance": 4000.00})
    env1.add_node_with_attribute("acc_scamgov", "account", {"owner": "ScamGov", "bank": "FirstFinancial", "balance": 0.00})

    # Add ownership edges
    env1.add_ownership_edge("Olivia", "acc_olivia")
    env1.add_ownership_edge("Betty", "acc_betty")
    env1.add_ownership_edge("ScamGov", "acc_scamgov")

    # Show result
    print(env1.get_nodes())
    print(env1.get_edges())
    print(env1)
    env1.draw_graph()