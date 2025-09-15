import requests
import pandas as pd
import os
from datetime import datetime
from .celery_config import celery_app


@celery_app.task(bind=True, name="src.tasks.tasks.fetch_users_from_api")
def fetch_users_from_api(self):
    try:
        api_url = "https://jsonplaceholder.typicode.com/users"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        users_data = response.json()
        
        users_list = []
        for user in users_data:
            users_list.append({
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email")
            })
        
        if not os.path.exists("data"):
            os.makedirs("data")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"data/users_{timestamp}.csv"
        
        df = pd.DataFrame(users_list)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Successfully saved {len(users_list)} users to {csv_filename}",
            "filename": csv_filename,
            "users_count": len(users_list)
        }
        
    except requests.exceptions.RequestException as e:
        self.retry(countdown=60, max_retries=3)
        return {
            "status": "error",
            "message": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Task failed: {str(e)}"
        }