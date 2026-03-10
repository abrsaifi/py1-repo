from app import create_app

app = create_app()

# Get all routes
print("\n=== ALL ROUTES ===\n")
routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        routes.append((rule.rule, methods, rule.endpoint))

# Sort by rule
for rule, methods, endpoint in sorted(routes, key=lambda x: x[0]):
    print(f"{methods:10} {rule:50} -> {endpoint}")

print(f"\n=== TOTALS ===")
print(f"Total routes: {len(routes)}")

# Check for frontend routes
frontend_routes = [r for r in routes if r[2] in ('serve_frontend', 'serve_assets', 'catch_all')]
print(f"\nFrontend routes: {len(frontend_routes)}")
for rule, methods, endpoint in frontend_routes:
    print(f"  {endpoint}: {rule}")
