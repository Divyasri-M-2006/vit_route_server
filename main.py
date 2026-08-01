from flask import Flask, request, jsonify
import osmnx as ox
import networkx as nx
import os

app = Flask(__name__)

# Load road network (Only once when server starts)
print("🚀 Loading VIT Vellore road network... This might take 2 minutes on first boot.")

# We load the road network for Vellore
try:
    G = ox.graph_from_place('Vellore, Tamil Nadu, India', network_type='drive')
    print("✅ Road network loaded successfully!")
except Exception as e:
    print(f"❌ Error loading network: {e}")
    G = None

@app.route('/')
def home():
    return "VIT Route Server is running!"

@app.route('/get_route', methods=['POST'])
def get_route():
    if G is None:
        return jsonify({"error": "Network not loaded"}), 500

    data = request.json
    start_lat = data.get('start_lat')
    start_lon = data.get('start_lon')
    end_lat = data.get('end_lat')
    end_lon = data.get('end_lon')

    if None in [start_lat, start_lon, end_lat, end_lon]:
        return jsonify({"error": "Missing coordinates"}), 400

    try:
        # Find nearest road nodes
        start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
        end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)

        # Find shortest path
        route = nx.shortest_path(G, start_node, end_node, weight='length')

        # Convert to Lat/Lng list [lat, lon]
        route_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in route]

        return jsonify({"route": route_coords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
