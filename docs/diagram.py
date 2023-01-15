from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MongoDB
from diagrams.onprem.queue import Kafka


with Diagram("", show=False):
    with Cluster("Ads System"):
        with Cluster("Storage"):
            mongo_db = MongoDB("MongoDB")

        with Cluster("Display"):
            client = Client("Client")
            api_server = Server("API Server")

            client << Edge(label="response: [ad list]") << api_server
            client >> Edge(label="GET /ads") >> api_server
            api_server >> Edge(label="check balance") >> mongo_db

        with Cluster("Event [impression | click] & Charge"):
            client = Client("Client")
            faust_worker = Server("Faust Worker")
            kafka = Kafka("Stream")

            client >> Edge(label="POST /events") >> kafka

            kafka << Edge(label="consume") << faust_worker
            faust_worker >> Edge(label="charge credit") >> mongo_db