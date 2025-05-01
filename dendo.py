import pandas as pd
import plotly.express as px
from collections import defaultdict

def human_readable_size(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} PB"

def generate_treemap_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]
    df['Path Parts'] = df['Filepath'].apply(lambda x: x.split('/'))

    size_map = defaultdict(int)
    label_map = {}
    parent_map = {}

    for _, row in df.iterrows():
        path_parts = row['Path Parts']
        file_size = row['Bytes']

        for i in range(1, len(path_parts) + 1):
            subpath = "/".join(path_parts[:i])
            parent = "/".join(path_parts[:i-1]) if i > 1 else ""
            size_map[subpath] += file_size
            label_map[subpath] = path_parts[i - 1]
            parent_map[subpath] = parent

    records = []
    for path, size in size_map.items():
        records.append({
            "id": path,
            "parent": parent_map[path],
            "label": label_map[path],
            "size": size,
            "readable_size": human_readable_size(size),
            "full_path": path
        })

    treemap_df = pd.DataFrame(records)

    fig = px.treemap(
        treemap_df,
        names='label',
        ids='id',
        parents='parent',
        values='size',
        custom_data=['readable_size', 'full_path'],
        title="Directory Size Treemap (Aggregated)"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>" +
            "Full Path: %{customdata[1]}<br>" +
            "Size: %{customdata[0]}<extra></extra>"
        )
    )

    fig.show()

if __name__ == "__main__":
    generate_treemap_from_csv("sample_files.csv")
