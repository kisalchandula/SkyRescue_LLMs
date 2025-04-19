from atproto import Client
from dotenv import load_dotenv
import os


def search_bluesky_posts(query: str, limit: int = 100):
    load_dotenv()
    username = os.getenv('BLUESKY_USERNAME')
    password = os.getenv('BLUESKY_PASSWORD')

    if not username or not password:
        raise ValueError("Username or password not found in .env file.")

    client = Client()
    client.login(username, password)

    results = client.app.bsky.feed.search_posts({'q': query, 'limit': limit})

    posts_data = []

    for post in results.data.posts:
        post_info = {
            "handle": post.author.handle,
            "display_name": post.author.display_name,
            "text": post.record.text,
            "post_uri": post.uri,
            "indexed_at": post.indexed_at,
        }
        posts_data.append(post_info)

    return posts_data


# Example usage
if __name__ == "__main__":
    posts = search_bluesky_posts("wildfire", 5)
    for idx, post in enumerate(posts, start=1):
        print(f"{idx}. @{post['handle']} ({post['display_name']})")
        print(f"   {post['text']}")
        print(f"   Link: https://bsky.app/profile/{post['handle']}/post/{post['post_uri'].split('/')[-1]}")
        print()
