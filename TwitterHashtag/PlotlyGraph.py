import plotly.offline as plotly
import plotly.graph_objs as go
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('dfCommunity.csv')

# Give nodes their Usernames
dfLookup = df[['userFromName', 'userFromId']].drop_duplicates()
# dfLookup.head(10)

G = nx.DiGraph()
#G = nx.Graph()
G.add_nodes_from(df['userFromId'])
# G.add_edges_from(zip(df['userFromId'],df['userToId']))

temp = zip(df['userFromId'], df['userToId'])
G.add_edges_from(temp)

# nx.draw(G, pos=nx.spring_layout(G,k=.12),node_color='c',edge_color='k')

pos = nx.spring_layout(G, k=.12)

centralScore = nx.betweenness_centrality(G)
inScore = G.in_degree()
outScore = G.out_degree()

# Get a list of all nodeID in ascending order
nodeID = G.node.keys()


def scatter_nodes(pos, labels=None, color='rgb(152, 0, 0)', size=8, opacity=1):
    trace = go.Scatter(x=[],
                       y=[],
                       mode='markers',
                       marker=dict(
        showscale=True,
        # colorscale options
        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='Greens',
        reversescale=False,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))
    x = []
    y = []
    color = []
    for nd in nodeID:

        x.append(pos[nd][0])
        y.append(pos[nd][1])
        color.append(centralScore[nd])

    trace['marker']['size'] = size
    trace['text'] = labels
    trace['name'] = ""
    trace['x'] = x
    trace['y'] = y
    trace['marker']['color'] = color

    return trace


def scatter_edges(G, pos, line_color='#a3a3c2', line_width=1, opacity=.2):
    trace = go.Scatter(x=[],
                       y=[],
                       mode='lines',
                       hoverinfo='none'
                       )

    x = []
    y = []
    for edge in G.edges():
        x += [pos[edge[0]][0], pos[edge[1]][0], None]
        y += [pos[edge[0]][1], pos[edge[1]][1], None]

        trace['line']['width'] = line_width
        if line_color is not None:  # when it is None a default Plotly color is used
            trace['line']['color'] = line_color
    trace['x'] = x
    trace['y'] = y

    return trace


labels = []
for nd in nodeID:
    temp = dfLookup['userFromName'][df['userFromId'] == nd]
    user = nd
    if not temp.empty:
        user = temp.values[0]
    labels.append(str(user) + "<br>" + "Followers: " + str(inScore[nd]) + "<br>" + "Following: " + str(
        outScore[nd]) + "<br>" + "Centrality: " + str("%0.3f" % centralScore[nd]))

trace1 = scatter_edges(G, pos)
trace2 = scatter_nodes(pos, labels=labels)

axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
            )
layout = go.Layout(title='Twitter Netwotk Graph',

                   titlefont_size=16,
                   showlegend=False,
                   hovermode='closest',
                   margin=dict(b=20, l=5, r=5, t=40),
                   xaxis=dict(
                       title='',
                       titlefont=dict(
                           size=14,
                           color='#7f7f7f'),
                       showline=False,
                       showticklabels=False,
                       zeroline=False
                   ),

                   yaxis=dict(showgrid=False, zeroline=False,
                              showticklabels=False),

                   )


data = [trace1, trace2]

fig = go.Figure(data=data, layout=layout)


def make_annotations(pos, text, font_size=14, font_color='rgb(25,25,25)'):
    L = len(pos)
    if len(text) != L:
        raise ValueError('The lists pos and text must have the same len')
    annotations = []
    for nd in nodeID:

        annotations.append(
            dict(
                text="",
                x=pos[nd][0], y=pos[nd][1],
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations


fig['layout'].update(annotations=make_annotations(pos, labels))
filename = "NetworkX.html"
plotly.plot(fig, show_link=False, filename=filename)
