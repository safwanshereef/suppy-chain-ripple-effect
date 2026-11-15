# Graph Schema

The AtmoGraph supply chain is stored in Neo4j (database: atmograph) as five node types connected by five relationship types.

## Node types

| Label | Key property | Other properties |
|---|---|---|
| Port | port_code | risk_score |
| Plant | plant_code | risk_score, capacity, cost_per_unit |
| Customer | customer_id | vmi |
| Carrier | carrier_name | carrier_type |
| Product | product_id | none |

Every key property has a uniqueness constraint, so the same entity is never created twice.

## Relationship types

| Relationship | From | To | Properties |
|---|---|---|---|
| HOSTED_AT | Plant | Port | none |
| ROUTE | Port | Port | carrier, rate, mode, tpt_days, min_weight, max_weight |
| MAKES | Plant | Product | none |
| ORDERED_BY | Plant | Customer | order_id, quantity, weight, late_days, service_level, order_date |
| OPERATED_BY | Port | Carrier | none |

## Loaded data

- Nodes: 11 ports, 20 plants, 46 customers, 10 carriers, 1,540 products
- Relationships: 9,215 ORDERED_BY, 2,036 MAKES, 1,258 ROUTE, 33 OPERATED_BY, 22 HOSTED_AT

## Why this design

The risk_score on Port and Plant nodes will be updated by the NLP engine in Week 2. A disruption at one port can then be followed along ROUTE, HOSTED_AT and ORDERED_BY edges to find the plants and customers it affects. The late_days property on orders is the target for delay prediction in Week 3.
