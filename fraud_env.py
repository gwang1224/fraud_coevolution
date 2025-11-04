import matplotlib.pyplot as plt
import networkx as nx

class FraudEnv():
    def __init__(self):
        self.G = nx.DiGraph()

        self.NODE_TEMPLATES = {
            "participant": {
                "role": None, # Either individual or fraudster
                "isFraudster": None, #True or False
            },
            "bank": {
                "role": "bank",
            },
            "account": {
                "role": "account",
                "owner": None,
                "bank": None,
                "balance": 0.0,
                "status": "active",  # could be 'active', 'flagged', 'frozen', etc.
                "compromised": False
            }
        }
    
    def add_node_with_attribute(self, node_id, node_type, custom_attrs=None):
        """
        Adds a node to the fraud environment graph using predefined templates.

        Args:
        node_id (str): 
            Unique identifier for the node (e.g., "Alice", "acc_alice", "Chase").
        node_type (str): 
            Type of node to add (must exist in `NODE_TEMPLATES`, e.g., "participant", "bank", "account").
        custom_attrs (dict, optional): 
            Dictionary of custom attributes to update the default template values 

        Raises:
            ValueError: 
                If the specified `node_type` is not found in `NODE_TEMPLATES`, 
                or if any key in `custom_attrs` does not exist in the template.

        Returns:
            None  
        """
        # Must add node with template
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

        try:
            if node_type == "account":
                owner = custom_attrs["owner"]
                bank = custom_attrs["bank"]
                self.G.add_edge(owner, node_id, rel="owns")
                self.G.add_edge(bank, node_id, rel="hosts")
                print(f"   ↳ Added edges: {owner} → {node_id} and {bank} → {node_id}")
        except Exception as e:
            Exception("Add ownership and bank node.")

    def add_ownership_edge(self, node_id1, node_id2):
            self.G.add_edge(node_id1, node_id2, rel="owns")
            print(f"Added ownership relationship between {node_id1} -> {node_id2}")

    def get_nodes(self):
        return list(self.G.nodes)

    def get_edges(self):
        return list(self.G.edges(data=True))

    def get_graph(self):
        return self.G
    
    def get_individuals(self):
        return [node for node, data in self.G.nodes(data=True) if data.get('role') == 'individual']
    
    def get_fraudsters(self):
        return [node for node, data in self.G.nodes(data=True) if data.get('role') == "fraudster"]
    
    def get_banks(self):
        return [node for node, data in self.G.nodes(data=True) if data.get('role') == "bank"]
    
    def get_acc(self):
        return [node for node, data in self.G.nodes(data=True) if data.get('role') == "account"]

    
    def update_balance(self, acc_from, acc_to, amount):
        self.G.nodes[acc_from]["balance"] -= amount
        self.G.nodes[acc_to]["balance"] += amount

    
    # MAYBE IMPLEMENT LATER
    # def get_acc_balances(self):
    
    def reset(self):
        self.G.clear()
        print("Graph has been reset.")

    def __str__(self):
        return f"FraudEnv with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges."
    
    def draw_graph(self):
        pos = nx.spring_layout(self.G, k = 0.5)
        plt.figure(figsize=(9, 7))
        nx.draw_networkx_nodes(self.G, pos, node_color='lightblue', node_size=1000)
        nx.draw_networkx_labels(self.G, pos, font_size=5)
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
    env1.add_node_with_attribute("Olivia", "participant", {"role": "individual"})
    env1.add_node_with_attribute("Betty", "participant", {"role": "individual"})

    # Add fraudsters
    env1.add_node_with_attribute("ScamGov", "participant", {"role": "fraudster"})
    env1.add_node_with_attribute("ScamCo", "participant", {"role": "fraudster"})

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