import networkx as nx
import matplotlib.pyplot as plt
import json
plt.figure(figsize=(50,50))

def draw(classes):
    G = nx.DiGraph()
    for cls in classes:
        G.add_node(cls['signature'])
    
    print('start draw')
    nx.draw(G)
    # print('start savefig')
    # plt.savefig("classes.png")
    
    print('start show')
    plt.show()

if __name__ == '__main__':
    with open('E:\\Workstation\\classes.json') as f:
        classes = json.loads(f.read())
        draw(classes)