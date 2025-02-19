import requests
import boto3
import json
import os
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration
#NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Store API Key in AWS Secrets Manager or Env Variables
NEWS_API_KEY = "629e9358bb52438aa0cbab9f611af95f"
DYNAMODB_TABLE = "NewsArticles"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
COUNTRY = "us"  # Fetch news from the US


def fetch_news():
    params = {
        "country": COUNTRY,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        print(f"Error fetching news: {response.status_code}")
        return []


def store_news(articles):
    for article in articles:
        item = {
            "id": article["url"],
            "title": article["title"],
            "description": article.get("description", "No Description"),
            "url": article["url"],
            "published_at": article["publishedAt"],
            "source": article["source"]["name"]
        }
        table.put_item(Item=item)
        print(f"Stored: {item['title']}")


@app.route("/fetch-news", methods=["GET"])
def fetch_and_store_news():
    articles = fetch_news()
    if articles:
        store_news(articles)
        return jsonify({"message": "News stored successfully"}), 200
    else:
        return jsonify({"message": "Failed to fetch news"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
