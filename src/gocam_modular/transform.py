from koza.cli_utils import transform_source


def process_activity(activity, model_id):
    # Process each activity to generate edges
    edges = []
    for key, assoc in associations.items():
        if assoc and "term" in assoc:
            edge = {
                "subject": activity["id"],
                "predicate": key,
                "object": assoc["term"],
                "relation": key,
                "provided_by": model_id
            }
            edges.append(edge)
    return edges


# Main transformation function
def transform_gocam():
    data = transform_source()
    nodes = []
    edges = []

    # Iterate over each model in data
    for model in data:
        model_id = model["id"]
        taxon = model.get("taxon", "")

        # Process objects as nodes
        for obj in model.get("objects", []):
            node = {
                "id": obj["id"],
                "name": obj.get("label", ""),
                "category": obj.get("type", "gocam:Object"),
                "taxon": taxon
            }
            nodes.append(node)

        # Process activities as nodes and edges
        for activity in model.get("activities", []):
            nodes.append({
                "id": activity["id"],
                "name": "",
                "category": "gocam:Activity",
                "taxon": taxon
            })
            edges.extend(process_activity(activity, model_id))

    # Return nodes and edges
    return nodes, edges
