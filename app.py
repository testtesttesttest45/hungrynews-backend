from flask import Flask, jsonify
import pymysql
import pymysql.cursors
import os
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta

app = Flask(__name__)
load_dotenv()
CORS(app)

def get_week_table_name(today=None):
    """
    get table name for current week (monday to sunday)
    If today variable is not provided, use the current date.
    """
    # debugging custom date
    # today = today or datetime(2024, 10, 10)  # Hardcoded date for debugging
    print(f"Debugging: Using date {today.strftime('%d %B %Y')}")
    
    # Find the start and end of the week
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday
    return f"{start_of_week.strftime('%d%m%y')}-{end_of_week.strftime('%d%m%y')}"


@app.route('/news')
def get_news():
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    table_name = get_week_table_name()
    print(f"Checking table: {table_name}")
    
    conn = pymysql.connect(**config)
    try:
        with conn.cursor() as cursor:
            # check if the table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}';")
            if not cursor.fetchone():
                return jsonify({"error": "Please wait while I generate this week's database"}), 503
            
            # see current week's table
            cursor.execute(f"SELECT title, url, datetime, is_read FROM `{table_name}` WHERE impact_level = 3")
            results = cursor.fetchall()
    except pymysql.MySQLError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # default to 5000
    app.run(host='0.0.0.0', port=port)