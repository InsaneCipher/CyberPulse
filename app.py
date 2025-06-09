from flask import Flask, render_template, request
import threading
import webview

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", results=None)


def run_flask():
    app.run()


@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword")
    sources = request.form.getlist("sources")

    # Placeholder results, replace with real scraping logic
    dummy_results = [
        {"title": f"{source} headline about {keyword}", "snippet": f"Short summary of {keyword} from {source}.",
         "url": "https://example.com"}
        for source in sources
    ]

    return render_template("index.html", results=dummy_results)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    webview.create_window("Flask App", "http://127.0.0.1:5000/")
    webview.start()
