from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MongoDB
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Kafka

with Diagram("", show=False):
    with Cluster("Ads System[Async]"):
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
            redis = Redis("Rolling Bloom Filter(e: 0.01, window: last 24h)")

            client >> Edge(label="POST /events") >> kafka

            kafka << Edge(label="1. consume") << faust_worker

            redis << Edge(label="2. membership query") << faust_worker
            mongo_db << Edge(label="2-a. query again when possibly duplicate") << faust_worker

            faust_worker >> Edge(label="3. charge credit") >> mongo_db
