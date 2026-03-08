from app.main import app

routes = sorted([f"{r.rule} -> {','.join(sorted(r.methods))}" for r in app.url_map.iter_rules()])
for r in routes:
    print(r)
