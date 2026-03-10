import server

app = server.app
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    methods = ','.join(sorted(r.methods))
    print(f"{r.rule} -> {methods}")
