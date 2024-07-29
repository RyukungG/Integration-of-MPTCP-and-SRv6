import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from os3e import OS3E

os3e = OS3E()
router = os3e.get_router()
link = os3e.get_link()
graph = os3e.get_graph()

# Display the DataFrames
print("Router DataFrame:")
print(router)
print("\nLink DataFrame:")
print(link)
print("\nGraph:")
print(graph)

m = Basemap(
         projection='merc',
         llcrnrlon=-128,
         llcrnrlat=23,
         urcrnrlon=-70,
         urcrnrlat=50,
         lat_ts=0,
         resolution='l',
         suppress_ticks=True)

mx, my = m(router['Longitude'].values, router['Latitude'].values)
pos = {}
for count, elem in enumerate (router['node']):
    pos[elem] = (mx[count], my[count])
edge_labels = nx.get_edge_attributes(graph, 'ipv6')

plt.figure(figsize=(45, 15))

nx.draw(graph, pos, with_labels=True, 
        node_size=150, node_color='red', font_size=22, font_weight='bold', font_color='black', 
        edge_color='green', linewidths=1, alpha=0.7)
nx.draw_networkx_nodes(graph, pos, nodelist=['Seattle', 'Chicago'], node_color='Blue', node_size=300, alpha=0.8, node_shape="H")
nx.draw_networkx_edges(graph, pos, edgelist=[('Seattle', 'Missoula'), ('Missoula', 'Minneapolis'), ('Minneapolis', 'Chicago')], edge_color='Red', width=1)
nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=12)

m.drawcountries(linewidth=1)
m.drawstates(linewidth=0.5)
m.drawcoastlines(linewidth=1)

# plt.tight_layout()
plt.savefig('os3e_map.eps', format='eps', dpi=600)
plt.show()