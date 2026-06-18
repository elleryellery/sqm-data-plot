from tkinter.filedialog import askopenfilename
import parse
import graph

filename = askopenfilename(filetypes=[("DAT File", "*.dat")])

parse.parse_file(filename)
#graph.graph_quality()

#parse.max_quality_over_time()
graph.graph_max_quality()