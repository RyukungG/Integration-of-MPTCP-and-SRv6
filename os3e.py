import pandas as pd
import numpy as np
import networkx as nx

class OS3E:
    def __init__(self):
        PREFIX = 'fd00:0:'

        with open('OS3E.txt', 'r') as file:
            lines = file.readlines()

        router_data = []
        link_data = []

        lines = [line.strip() for line in lines if line.strip()]

        current_section = None
        for line in lines:
            if line == "router":
                current_section = "router"
            elif line == "link":
                current_section = "link"
            elif current_section == "router" and line and not line.startswith("node"):
                router_data.append(line.split())
            elif current_section == "link" and line and not line.startswith("source"):
                link_data.append(line.split())
        
        for i in range(1, len(link_data)+1):
            link_data[i-1].insert(4,f'{PREFIX}{i}::')

        print(link_data)
        # Convert the lists into pandas DataFrames
        self.router_df = pd.DataFrame(router_data, columns=["node", "Longitude", "Latitude"])
        self.link_df = pd.DataFrame(link_data, columns=["source", "dest", "bandwidth", "delay", "ipv6"])

        self.router_df = self.router_df.astype({"Longitude": np.float64, "Latitude": np.float64})
        self.link_df = self.link_df.astype({"bandwidth": np.float64, "delay": np.float64})

        # Create a graph from the link DataFrame
        self.graph = nx.from_pandas_edgelist(self.link_df, 'source', 'dest', ['bandwidth', 'delay', 'ipv6'])

    def get_router(self):
        return self.router_df

    def get_link(self):
        return self.link_df
    
    def get_graph(self):
        return self.graph
    
