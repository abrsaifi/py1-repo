from . import create_app

app = create_app()


if __name__ == '__main__':
    # Run development server for the new package layout
    app.run(host='0.0.0.0', port=5000, debug=True)
