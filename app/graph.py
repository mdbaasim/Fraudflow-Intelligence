"""
NetworkX Graph Processing Engine
Constructs directed transaction graphs, tracks money flow hops,
calculates network centrality, fan-in/fan-out, and identifies terminal nodes.
"""

import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger("fraudflow.graph")

class TransactionGraphEngine:
    def __init__(self, transactions: List[Dict[str, Any]], victim_account: Optional[str] = None):
        self.raw_transactions = transactions
        self.victim_account = victim_account
        self.G = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Build directed graph from raw transaction records."""
        # Sort chronologically by timestamp
        sorted_txs = sorted(self.raw_transactions, key=lambda x: x.get("timestamp", ""))

        for tx in sorted_txs:
            src = tx["source_account"]
            dst = tx["dest_account"]
            amount = float(tx["amount"])
            ts = tx.get("timestamp", "")
            channel = tx.get("channel", "IMPS")
            src_city = tx.get("source_city") or "Unknown"
            dst_city = tx.get("dest_city") or "Unknown"
            tx_id = str(tx.get("id") or tx.get("external_event_id", ""))

            # Initialize source node
            if not self.G.has_node(src):
                self.G.add_node(
                    src,
                    label=src,
                    city=src_city,
                    received_total=0.0,
                    sent_total=0.0,
                    entity_type="VICTIM" if src == self.victim_account else "MULE"
                )
            
            # Initialize destination node
            if not self.G.has_node(dst):
                self.G.add_node(
                    dst,
                    label=dst,
                    city=dst_city,
                    received_total=0.0,
                    sent_total=0.0,
                    entity_type="MULE"
                )

            # Update totals
            self.G.nodes[src]["sent_total"] += amount
            self.G.nodes[dst]["received_total"] += amount
            if dst_city != "Unknown" and self.G.nodes[dst]["city"] == "Unknown":
                self.G.nodes[dst]["city"] = dst_city

            # Add directed edge
            self.G.add_edge(
                src,
                dst,
                id=tx_id,
                amount=amount,
                channel=channel,
                timestamp=ts,
                is_latest=False
            )

        # Mark latest transaction edge
        if sorted_txs:
            last_tx = sorted_txs[-1]
            last_src = last_tx["source_account"]
            last_dst = last_tx["dest_account"]
            if self.G.has_edge(last_src, last_dst):
                self.G[last_src][last_dst]["is_latest"] = True

    def get_terminal_nodes(self) -> List[str]:
        """
        Terminal nodes are accounts that have received funds but have not forwarded
        them (out_degree == 0 and in_degree > 0), or hold remaining dissipated balance.
        """
        terminals = [
            node for node in self.G.nodes
            if self.G.out_degree(node) == 0 and self.G.in_degree(node) > 0
        ]
        if not terminals and self.G.nodes:
            # Fallback to node with lowest out/in ratio or destination of latest tx
            if self.raw_transactions:
                terminals = [self.raw_transactions[-1]["dest_account"]]
            else:
                terminals = list(self.G.nodes)
        return terminals

    def compute_graph_metrics(self) -> Dict[str, Any]:
        """Compute structural network features using NetworkX."""
        num_nodes = self.G.number_of_nodes()
        num_edges = self.G.number_of_edges()

        if num_nodes == 0 or num_edges == 0:
            return {
                "num_nodes": 0,
                "num_edges": 0,
                "max_hops": 0,
                "avg_hops": 0.0,
                "max_fan_out": 0,
                "max_fan_in": 0,
                "density": 0.0,
                "clustering_coeff": 0.0,
                "terminal_in_degree": 0,
                "terminal_out_degree": 0,
                "longest_path_nodes": []
            }

        # Calculate out-degrees and in-degrees
        out_degrees = dict(self.G.out_degree())
        in_degrees = dict(self.G.in_degree())
        max_fan_out = max(out_degrees.values()) if out_degrees else 0
        max_fan_in = max(in_degrees.values()) if in_degrees else 0

        # Density
        density = nx.density(self.G)

        # Average clustering coefficient (converted to undirected for clustering)
        try:
            undirected_g = self.G.to_undirected()
            clustering = nx.average_clustering(undirected_g)
        except Exception:
            clustering = 0.0

        # Hop depth analysis from root/victim
        max_hops = 0
        longest_path = []
        terminal_nodes = self.get_terminal_nodes()

        # Trace paths from victim (or in_degree == 0 nodes)
        root_nodes = [n for n in self.G.nodes if self.G.in_degree(n) == 0]
        if self.victim_account and self.victim_account in self.G:
            root_nodes = [self.victim_account]

        for root in root_nodes:
            for term in terminal_nodes:
                if nx.has_path(self.G, root, term):
                    all_paths = list(nx.all_simple_paths(self.G, root, term))
                    for path in all_paths:
                        hops = len(path) - 1
                        if hops > max_hops:
                            max_hops = hops
                            longest_path = path

        # Terminal node metrics
        primary_terminal = terminal_nodes[-1] if terminal_nodes else None
        term_in = in_degrees.get(primary_terminal, 0) if primary_terminal else 0
        term_out = out_degrees.get(primary_terminal, 0) if primary_terminal else 0

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "max_hops": max_hops,
            "avg_hops": float(max_hops),
            "max_fan_out": max_fan_out,
            "max_fan_in": max_fan_in,
            "density": round(float(density), 4),
            "clustering_coeff": round(float(clustering), 4),
            "terminal_in_degree": term_in,
            "terminal_out_degree": term_out,
            "longest_path_nodes": longest_path,
            "primary_terminal": primary_terminal
        }

    def serialize_for_ui(self) -> Dict[str, Any]:
        """Serialize nodes and edges for frontend D3/SVG visualization."""
        nodes = []
        edges = []
        latest_edge_id = None

        terminals = set(self.get_terminal_nodes())

        for node_id, data in self.G.nodes(data=True):
            is_term = node_id in terminals
            entity_type = data.get("entity_type", "MULE")
            if is_term and entity_type != "VICTIM":
                entity_type = "TERMINAL_MULE"

            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "entity_type": entity_type,
                "city": data.get("city", "Unknown"),
                "balance_received": data.get("received_total", 0.0),
                "balance_forwarded": data.get("sent_total", 0.0),
                "is_terminal": is_term
            })

        for u, v, data in self.G.edges(data=True):
            is_latest = data.get("is_latest", False)
            edge_id = data.get("id", f"{u}->{v}")
            if is_latest:
                latest_edge_id = edge_id

            edges.append({
                "id": edge_id,
                "source": u,
                "target": v,
                "amount": data.get("amount", 0.0),
                "channel": data.get("channel", "IMPS"),
                "timestamp": data.get("timestamp", ""),
                "is_latest": is_latest
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "latest_edge_id": latest_edge_id
        }
