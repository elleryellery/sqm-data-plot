from tkinter.filedialog import askopenfilename
import parse
import graph

filename = askopenfilename(filetypes=[("DAT File", "*.dat")])

parse.parse_file(filename)
#graph.graph_quality()

graph.graph_max_quality()