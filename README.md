# AtmoGraph: Supply Chain Ripple Effect Predictor

AtmoGraph models a global supply chain as a graph, so that a disruption at one place, such as a port strike, can be traced across connected ports, plants and customers. A React dashboard shows the graph and highlights nodes at risk.

Built as part of an internship project at Infotact Solutions.

## Tech stack

- Neo4j for the graph database
- Python, pandas and Jupyter Notebook for data cleaning and ingestion
- React, Vite and React Flow for the dashboard

## Dataset

Kaggle dataset "Supply chain logistics in terms of shipping" with seven sheets, including 9,215 orders.

## Graph design

Nodes: Port, Plant, Customer, Carrier, Product.

Relationships: HOSTED_AT, ROUTE, MAKES, ORDERED_BY, OPERATED_BY.

Port and Plant nodes have a risk_score property for later risk updates.

## Week 1 progress

- Set up Neo4j database
- Designed the graph schema
- Cleaned the dataset and loaded it into Neo4j with a Python script
- Built a React dashboard that shows a static graph with React Flow

## Author

Muhammad Safwan Shereef
