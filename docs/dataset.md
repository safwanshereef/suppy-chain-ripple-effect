# Dataset Notes

## Source

Kaggle dataset "Supply chain logistics in terms of shipping", provided as one Excel file with seven sheets.

## Sheets

| Sheet | Rows | Columns | Used for |
|---|---|---|---|
| OrderList | 9,215 | 14 | Orders between plants and customers |
| FreightRates | 1,540 | 11 | Carrier routes between ports |
| PlantPorts | 22 | 2 | Which plant ships through which port |
| ProductsPerPlant | 2,036 | 2 | Which products each plant makes |
| VmiCustomers | 14 | 2 | Vendor managed inventory customers |
| WhCapacities | 19 | 2 | Daily capacity of each plant warehouse |
| WhCosts | 19 | 2 | Cost per unit of each warehouse |

## OrderList columns

Order ID, Order Date, Origin Port, Carrier, TPT, Service Level, Ship ahead day count, Ship Late Day count, Customer, Product ID, Plant Code, Destination Port, Unit quantity, Weight.

## FreightRates columns

Carrier, orig_port_cd, dest_port_cd, minm_wgh_qty, max_wgh_qty, svc_cd, minimum cost, rate, mode_dsc, tpt_day_cnt, Carrier type.

## Cleaning steps

- Checked every sheet for missing values: none found.
- Found 3 duplicate rows in FreightRates and removed them, leaving 1,537 rows.
- Removed stray spaces from column names.
- Renamed columns that differed between sheets, for example WH and Plant ID became Plant Code, and Customers became Customer.
- Converted Order ID from a float to a clean text value.

## Notes

The Ship Late Day count column in OrderList is the delay measure. It will be the target for delay prediction in Week 3.
