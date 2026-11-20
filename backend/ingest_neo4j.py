import pandas as pd
from getpass import getpass
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
DATABASE = "atmograph"
EXCEL_FILE = "Supply chain logisitcs problem.xlsx"

driver = GraphDatabase.driver(URI, auth=("neo4j", getpass("Neo4j password: ")))
driver.verify_connectivity()


def run_batch(query, rows, batch_size=1000):
    with driver.session(database=DATABASE) as session:
        for i in range(0, len(rows), batch_size):
            session.run(query, rows=rows[i:i + batch_size])
    print("Loaded", len(rows), "rows")


# 1. Read and clean the data
sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)
orders = sheets["OrderList"].copy()
freight = sheets["FreightRates"].copy()
plant_ports = sheets["PlantPorts"].copy()
products = sheets["ProductsPerPlant"].copy()
capacities = sheets["WhCapacities"].copy()
costs = sheets["WhCosts"].copy()
vmi = sheets["VmiCustomers"].copy()

for df in [orders, freight, plant_ports, products, capacities, costs, vmi]:
    df.columns = [c.strip() for c in df.columns]

freight = freight.drop_duplicates().reset_index(drop=True)
capacities = capacities.rename(columns={"Plant ID": "Plant Code", "Daily Capacity": "capacity"})
costs = costs.rename(columns={"WH": "Plant Code", "Cost/unit": "cost_per_unit"})
vmi = vmi.rename(columns={"Customers": "Customer"})
orders["Order ID"] = orders["Order ID"].astype("int64").astype(str)
orders["Product ID"] = orders["Product ID"].astype(str)
products["Product ID"] = products["Product ID"].astype(str)

# 2. Uniqueness constraints and a clean start
with driver.session(database=DATABASE) as session:
    for label, prop in [("Port", "port_code"), ("Plant", "plant_code"),
                        ("Customer", "customer_id"), ("Carrier", "carrier_name"),
                        ("Product", "product_id")]:
        session.run(f"CREATE CONSTRAINT {prop} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")
    session.run("MATCH (n) DETACH DELETE n")

# 3. Nodes
ports = (set(orders["Origin Port"]) | set(orders["Destination Port"])
         | set(freight["orig_port_cd"]) | set(freight["dest_port_cd"])
         | set(plant_ports["Port"]))
run_batch("UNWIND $rows AS row MERGE (p:Port {port_code: row.id}) SET p.risk_score = 0.0",
          [{"id": p} for p in ports])

plants = set(plant_ports["Plant Code"]) | set(products["Plant Code"]) | set(orders["Plant Code"])
cap_map = dict(zip(capacities["Plant Code"], capacities["capacity"]))
cost_map = dict(zip(costs["Plant Code"], costs["cost_per_unit"]))
run_batch("""UNWIND $rows AS row MERGE (p:Plant {plant_code: row.id})
             SET p.risk_score = 0.0, p.capacity = row.capacity, p.cost_per_unit = row.cost""",
          [{"id": p,
            "capacity": float(cap_map[p]) if p in cap_map else None,
            "cost": float(cost_map[p]) if p in cost_map else None} for p in plants])

vmi_set = set(vmi["Customer"])
run_batch("UNWIND $rows AS row MERGE (c:Customer {customer_id: row.id}) SET c.vmi = row.vmi",
          [{"id": c, "vmi": c in vmi_set} for c in set(orders["Customer"])])

carrier_types = freight.drop_duplicates("Carrier").set_index("Carrier")["Carrier type"].to_dict()
carriers = set(freight["Carrier"]) | set(orders["Carrier"])
run_batch("UNWIND $rows AS row MERGE (c:Carrier {carrier_name: row.id}) SET c.carrier_type = row.type",
          [{"id": c, "type": carrier_types.get(c)} for c in carriers])

product_ids = set(products["Product ID"]) | set(orders["Product ID"])
run_batch("UNWIND $rows AS row MERGE (p:Product {product_id: row.id})",
          [{"id": p} for p in product_ids])

# 4. Relationships
run_batch("""UNWIND $rows AS row
             MATCH (pl:Plant {plant_code: row.plant}) MATCH (po:Port {port_code: row.port})
             MERGE (pl)-[:HOSTED_AT]->(po)""",
          [{"plant": r["Plant Code"], "port": r["Port"]} for _, r in plant_ports.iterrows()])

run_batch("""UNWIND $rows AS row
             MATCH (pl:Plant {plant_code: row.plant}) MATCH (pr:Product {product_id: row.product})
             MERGE (pl)-[:MAKES]->(pr)""",
          [{"plant": r["Plant Code"], "product": r["Product ID"]} for _, r in products.iterrows()])

run_batch("""UNWIND $rows AS row
             MATCH (a:Port {port_code: row.orig}) MATCH (b:Port {port_code: row.dest})
             MERGE (a)-[r:ROUTE {carrier: row.carrier, service_code: row.svc, min_weight: row.min_w}]->(b)
             SET r.rate = row.rate, r.mode = row.mode, r.tpt_days = row.tpt, r.max_weight = row.max_w""",
          [{"orig": r["orig_port_cd"], "dest": r["dest_port_cd"], "carrier": r["Carrier"],
            "svc": r["svc_cd"], "min_w": float(r["minm_wgh_qty"]), "max_w": float(r["max_wgh_qty"]),
            "rate": float(r["rate"]), "mode": r["mode_dsc"], "tpt": int(r["tpt_day_cnt"])}
           for _, r in freight.iterrows()])

ops = freight[["orig_port_cd", "Carrier"]].drop_duplicates()
run_batch("""UNWIND $rows AS row
             MATCH (p:Port {port_code: row.port}) MATCH (c:Carrier {carrier_name: row.carrier})
             MERGE (p)-[:OPERATED_BY]->(c)""",
          [{"port": r["orig_port_cd"], "carrier": r["Carrier"]} for _, r in ops.iterrows()])

run_batch("""UNWIND $rows AS row
             MATCH (pl:Plant {plant_code: row.plant}) MATCH (c:Customer {customer_id: row.customer})
             MERGE (pl)-[r:ORDERED_BY {order_id: row.order_id}]->(c)
             SET r.quantity = row.qty, r.weight = row.weight, r.late_days = row.late,
                 r.service_level = row.service, r.order_date = row.date""",
          [{"plant": r["Plant Code"], "customer": r["Customer"], "order_id": r["Order ID"],
            "qty": int(r["Unit quantity"]), "weight": float(r["Weight"]),
            "late": int(r["Ship Late Day count"]), "service": r["Service Level"],
            "date": str(r["Order Date"])[:10]} for _, r in orders.iterrows()])

# 5. Check the result
with driver.session(database=DATABASE) as session:
    for r in session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS total"):
        print(r["label"], r["total"])
    for r in session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS total"):
        print(r["type"], r["total"])
