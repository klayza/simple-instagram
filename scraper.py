import dotenv
import instaloader
from instaloader import Profile
import json
import os
from utils import *
import logging
import time
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dotenv.load_dotenv(".env")
USER = os.getenv("user")
PASSWORD = os.getenv("password")
PROCESS_INTERVAL = 240 * 60  # 240 minutes in seconds
USER_UPDATE_INTERVAL = 240 * 60

def create_following_json(L):
    following_file = "following.json"
    if not os.path.exists(following_file) or os.path.getsize(following_file) == 0:
        logging.info("Creating following.json file")
        profile = Profile.from_username(L.context, USER)
        followees = [followee.username for followee in profile.get_followees()]
        with open(following_file, "w") as f:
            json.dump(followees, f, indent=2)
        logging.info(f"Created following.json with {len(followees)} users")
    else:
        logging.info("following.json already exists and is not empty")

def setup():
    logging.info("Starting setup process")
    L = instaloader.Instaloader()
   
    logging.info(f"Attempting to log in as {USER}")
    try:
        L.login(USER, PASSWORD)
        logging.info("Login successful")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return None
    
    create_following_json(L)
    
    return L

def update_user_data(L):
    os.makedirs("./users", exist_ok=True)
    data_file = "./users/data.json"
    USERS = getUsernames()

    # Load existing data if file exists
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            user_data = json.load(f)
        logging.info(f"Loaded existing data for {len(user_data)} users")
    else:
        user_data = {}

    total_users = len(USERS)
    for index, username in enumerate(USERS, 1):
        logging.info(f"Processing user {index}/{total_users}: {username}")

        # Skip users updated within the last UPDATE_INTERVAL_MINS
        last_updated_str = user_data.get(username, {}).get("last_updated")
        if last_updated_str:
            last_updated = datetime.fromisoformat(last_updated_str)
            if datetime.now() - last_updated < timedelta(seconds=USER_UPDATE_INTERVAL):
                logging.info(f"Skipping {username}: last updated {last_updated_str}")
                continue

        try:
            profile = Profile.from_username(L.context, username)
            user_data[username] = {
                "profile_pic_url": profile.profile_pic_url,
                "follower_count": profile.followers,
                "following_count": profile.followees,
                "follows_me": profile.follows_viewer,
                "bio": profile.biography,
                "name": profile.full_name,
                "website": profile.external_url,
                "has_story": profile.has_viewable_story,
                "last_post_date": None,
                "last_updated": datetime.now().isoformat()  # Add this line
            }

            posts = profile.get_posts()
            for post in posts:
                user_data[username]["last_post_date"] = post.date.strftime("%Y-%m-%d")
                logging.info(f"Found last post date for {username}: {user_data[username]['last_post_date']}")
                break

            # Save data after each user is processed
            with open(data_file, "w") as f:
                json.dump(user_data, f, indent=2)
            logging.info(f"Successfully processed and saved data for {username}")

        except Exception as e:
            logging.error(f"Error processing {username}: {str(e)}")

    logging.info("All users processed.")
        
def main():
    logging.info("Script started")
    L = setup()
    if L is None:
        return

    while True:
        update_user_data(L)
        logging.info(f"Waiting for {PROCESS_INTERVAL // 60} minutes before next update")
        time.sleep(PROCESS_INTERVAL)

if __name__ == "__main__":
    main()