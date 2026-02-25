import sys
sys.path.insert(0, '.')
from server import fetch_odata

# Fetch more records and check status distribution
orders = fetch_odata(
    'SalesOrderHeadersV2',
    select='SalesOrderNumber,SalesOrderStatus',
    top=1000
)

print(f"Total returned: {len(orders)}")

counts = {}
for o in orders:
    s = o.get('SalesOrderStatus', 'Unknown')
    counts[s] = counts.get(s, 0) + 1

print("Status breakdown:")
for status, count in counts.items():
    print(f"  {status}: {count}")

# Show backorders specifically
backorders = [o for o in orders if o.get('SalesOrderStatus') == 'Backorder']
print(f"\nBackorders found: {len(backorders)}")
for o in backorders[:5]:
    print(f"  {o.get('SalesOrderNumber')} | {o.get('SalesOrderStatus')}")
