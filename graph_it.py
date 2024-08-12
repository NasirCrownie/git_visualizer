import sys
import os
from git import Repo, NoSuchPathError, InvalidGitRepositoryError
from graphviz import Digraph
from jinja2 import Template
from datetime import datetime

def get_repo():
  try:
    repo = Repo(sys.argv[1])
    return repo
  except IndexError:
    print(f"ERROR: Please pass a path to the local repository!")
    return
  except NoSuchPathError:
    print(f"ERROR: No directory named '{sys.argv[1]}'! Is the repository cloned locally?")
    return
  except InvalidGitRepositoryError:
    print(f"ERROR: '{sys.argv[1]}' is not a valid Git repository.")
    return
  
def create_graph():
  graph = Digraph(comment='Initializing Graph')
  name = f"{os.path.basename(sys.argv[1])} Graphical Repository"
  graph.attr(label=f"{name}", labelloc='t', bgcolor='', fontsize='50')
  return graph
   
def get_branches(repo):
  branches = [branch.name for branch in repo.remote().refs]
  #Removing HEAD "branch"
  branches.remove('origin/HEAD')
  return branches

def get_branch_commits(repo, branch):
  return list(repo.iter_commits(branch))

def make_color_map(branches):
  x11_colors = ["red", "orange", "yellow", "green", "blue", "purple", "gold", "pink", "grey", "cornflowerblue",
                "darkorchid", "darkolivegreen", "khaki", "maroon", "navy", "palegreen", "saddlebrown", "royalblue",
                "violet", "plum", "tomato", "lime", "indigo", "chocolate", "bisque", "olive" 
                ]
  color_map = dict()

  for i in range(len(branches)):
    color_map[branches[i]] = x11_colors[i % len(x11_colors)]
  
  return color_map

def node_in_graph(graph, node_message):
  for node in graph:
    if (node == node_message):
      return True
  return False

def add_branches(repo, graph, branches, color_map):
  for branch in branches:
    commits = get_branch_commits(repo, branch)
    prev_node = None
    for commit in commits[::-1]:
      node_message = f"{commit.author}\n{commit.message}"
      if (node_in_graph(graph, node_message) and prev_node != None): #If node in graph and no prev node
        graph.edge(prev_node, node_message, color=color_map[branch])
        prev_node = node_message
      elif (node_in_graph(graph, node_message) and prev_node == None): #If node in graph and is prev node
        prev_node = node_message
      elif (not node_in_graph(graph, node_message) and prev_node != None): #If node not in graph and no prev node
        graph.node(node_message, style="filled", id=f"{commit}", shape="circle", width='5.0', height='5.0', fixedsize='true')
        graph.edge(prev_node, node_message, color=color_map[branch])
        prev_node = node_message
      elif (not node_in_graph(graph, node_message) and prev_node == None): #If node not in graph and is prev node
        graph.node(node_message, style="filled", id=f"{commit}", shape="circle", width='5.0', height='5.0', fixedsize='true')
        prev_node = node_message

    #Add branch ender 
    graph.node(branch, fontcolor=color_map[branch], id=f"{commit}", shape="box", fontsize="28.0")
    graph.edge(branch, prev_node, color=color_map[branch])

def show_graph(graph):
  now = datetime.now()
  png_name = now.strftime("%Y-%m-%d %H:%M:%S")
  graph.render(f'{png_name}', format='png', view=True)

def main():
  repo = get_repo()
  graph = create_graph()
  branches = get_branches(repo)
  color_map = make_color_map(branches)
  add_branches(repo, graph, branches, color_map)
  show_graph(graph)

if (__name__ == "__main__"):
  main()

