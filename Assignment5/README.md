# 1) Check if the API is running (root route)
curl http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/

# 2) Get ALL trucking companies (GET all)
curl http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/companies

# 3) Get ONE specific company (example: UPS)
curl http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/companies/UPS

# 4) ADD a new company (POST)
curl -X POST http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/companies \
  -H "Content-Type: application/json" \
  -d '{
        "Company": "New Truck Co",
        "Services": "Regional Freight",
        "Hubs": ["Seattle, WA", "Short haul on West Coast"],
        "Revenue": "$1,000",
        "HomePage": "https://example.com",
        "Logo": "newtruck.png"
      }'

# 5) UPDATE an existing company (example: UPS revenue) (PUT)
curl -X PUT http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/companies/UPS \
  -H "Content-Type: application/json" \
  -d '{"Revenue":"$26,000"}'

# 6) DELETE a specific company (example: Con-way)
curl -X DELETE http://ec2-18-221-220-107.us-east-2.compute.amazonaws.com:8000/companies/Con-way
