import pandas as pd
import numpy as np
import plotly.graph_objects as go

class AutoSankey:

  def __init__(self, agg_table, metric_col, mother_node='all'):
    """
    Automatically generate a sankey diagram from a aggregated table (results from "groupby")

    ---Parameters
    agg_table: a pandas dataframe with at least one layer column and one metric column
    metric: a string indicating the name of the metric column 
    mother_node: a string indicating the name of the mother node
    """
    self.agg = agg_table
    self.metric_col = metric_col
    self.mother_node = mother_node

    self.layers = [x for x in agg_table.columns]
    self.layers.remove(self.metric_col)

  def plot(self):
    nodes = []
    # Create table that replace all values in the table with the actual name of the node
    agg_nodes = self.agg.copy()
    for col in self.layers:
      agg_nodes[col] = agg_nodes[col].map(lambda x: col+'-'+str(x))
      nodes += [col+'-'+str(x) for x in self.agg[col].unique()]
      # reserve index 0 for the mother node
      nodes_dict = {nodes[i]:(i+1) for i in range(len(nodes))}

    # Add the mother node insto the nodes dictionary
    nodes_dict[self.mother_node] = 0

    # Add the mode node into the list of nodes
    nodes = [self.mother_node] + nodes

    # Translate the agg_nodes table to the index
    agg_nodes_idx = agg_nodes.copy()
    for col in self.layers:
      agg_nodes_idx[col] = agg_nodes_idx[col].map(nodes_dict)

    # Add the mother node index to the agg_nodes_idx table
    agg_nodes_idx[self.mother_node] = 0

    # get all columns we need to group by to create mappings (e.g. the edges and its values)
    all_cols_for_group_by = [self.mother_node]+self.layers
    agg_nodes_idx = agg_nodes_idx[all_cols_for_group_by+[self.metric_col]]

    # create nested column sets and loop over them to create the mapping table
    nested_list = [all_cols_for_group_by[i:i+2] for i in range(len(self.layers))]
    mapping_table = pd.DataFrame()
    for col_set in nested_list:
      temp = agg_nodes_idx[col_set+[self.metric_col]].groupby(col_set).sum().reset_index()
      temp.columns = ['source','target','value']
      mapping_table = pd.concat([mapping_table,temp])

    # Calculate the step-wise CVR
    source_agg = mapping_table[['source','value']].groupby('source').sum().reset_index()
    source_agg.columns = ['source','source_total']
    mapping_table = pd.merge(
        mapping_table,
        source_agg,
        how='left',
        left_on='source',
        right_on='source'
    )

    mapping_table['step_cvr'] = mapping_table['value']/mapping_table['source_total']
    self.mapping_table = mapping_table
    # Make the final plot
    fig = go.Figure(data=[go.Sankey(
            arrangement = "snap",
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = nodes,
              color = "blue",
              hovertemplate='Raw %{value}<extra></extra>'
            ),
            link = dict(
              source = mapping_table.source,
              target = mapping_table.target,
              value = mapping_table.value,
              label = [str(round(x,1))+'%' for x in mapping_table.step_cvr*100],
              customdata = [str(round(x,1))+'%' for x in mapping_table.step_cvr*100],
              hovertemplate='Raw %{value}; CVR %{customdata}<extra></extra>',  
          ))])
    
    return fig