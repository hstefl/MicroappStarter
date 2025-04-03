<span style="color:red">**WIP**</span>

Microservice Example: Mini E-Commerce System
3 microservices that work together to simulate a basic online order process.

Service	Purpose	    Endpoints	                                                Communicates with
-------------------------------------------------------------------------------------------------------------
User Service	    Manages users/customers	/users, /users/{id}	                Order Service
Product Service	    Handles product catalog	/products, /products/{id}	        Order Service
Order Service	    Creates orders, ties user + product	/orders, /orders/{id}	Calls User + Product Services

Business Case: Place an Order
-----------------------------
Scenario:
Client hits /orders to place an order.
Order Service:
 1. Verifies user exists via User Service
 2. Verifies product exists via Product Service
 3. Saves the order (in-memory for now)
 4. Returns an order confirmation

How
---
Test execution in each module
```
cd services/{service_name}
poetry run pytest
```

Run all tests in all modules and provide combined coverage report
```
poetry run python scripts/run_all_tests_and_coverage.py
```