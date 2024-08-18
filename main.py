import dotenv
import instaloader
from instaloader import Profile
import json
import os
from utils import *
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dotenv.load_dotenv(".env")
USER = os.getenv("user")
PASSWORD = os.getenv("password")
USERS = getUsernames()

def setup():
    logging.info("Starting setup process")
    L = instaloader.Instaloader()
    
    logging.info(f"Attempting to log in as {USER}")
    try:
        L.login(USER, PASSWORD)
        logging.info("Login successful")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return
    
    os.makedirs("./users", exist_ok=True)
    data_file = "./users/data.json"
    
    # Load existing data if file exists
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            user_data = json.load(f)
        logging.info(f"Loaded existing data for {len(user_data)} users")
    else:
        user_data = {}
    
    total_users = len(USERS)
    for index, username in enumerate(USERS, 1):
        if username in user_data:
            logging.info(f"Skipping already processed user {index}/{total_users}: {username}")
            continue
        
        logging.info(f"Processing user {index}/{total_users}: {username}")
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
                "last_post_date": None
            }
            
            posts = profile.get_posts()
            for post in posts:
                user_data[username]["last_post_date"] = post.date.strftime("%Y-%m-%d")
                logging.info(f"Found last post date for {username}: {user_data[username]['last_post_date']}")
                break
            
            # Save data after each user is processed
            with open(data_file, "w") as f:
                json.dump(user_data, f)
            logging.info(f"Successfully processed and saved data for {username}")
            
        except Exception as e:
            logging.error(f"Error processing {username}: {str(e)}")
    
    logging.info("All users processed.")

if __name__ == "__main__":
    logging.info("Script started")
    setup()
    logging.info("Script completed")