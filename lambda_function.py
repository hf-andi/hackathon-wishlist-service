import json
import os

import psycopg2


def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=os.environ["HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            port=os.environ["PORT"]
        )
        return conn.cursor()
    except Exception as e:
        print(e)
        print("can't connect to db for some reason")


def compare_labels(user_labels, cur):
    """
    user_labels format: [{'Name': 'Food', 'Confidence': 94.69338989257812}]
    :return:
    """
    # Get data from dictionary
    query = 'select uuid as uuid, labels as labels from recipes;'
    cur.execute(query)
    db_recipes = cur.fetchall()

    best_match_score = 0
    best_match_id = None
    for recipe_uuid, recipe_labels in db_recipes:
        score = 0
        print(recipe_labels)
        for label in user_labels:
            for recipe_label in recipe_labels:
                if recipe_label["Name"].upper() == label["Name"].upper():
                    score += (label["Confidence"] / 100) * (recipe_label["Confidence"] / 100)
                    # score += 1
        if score > best_match_score and score > 0.5:
            best_match_score = score
            best_match_id = recipe_uuid

    print(f"the final score is {best_match_score}")
    print(f"{best_match_id} is the id of the final recipe")
    return best_match_id


def extract_data_from_event(event):
    print("event", event)
    msg = json.loads(event["Records"][0]["body"])
    return msg["user_uuid"], msg["s3_file_key"], msg["labels"]


def lambda_handler(event, context):
    user_uuid, file_key, user_labels = extract_data_from_event(event)
    print(user_uuid)
    print(file_key)
    print(user_labels)

    # save to user db

    cur = connect_to_db()

    recipe_id = compare_labels(user_labels, cur)

    query = f"select * from recipes where uuid = '{recipe_id}';"
    cur.execute(query)
    matching_recipe = cur.fetchone()

    print(f"The final recipe is {matching_recipe}")

    cur.close()

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}


# body = {"user_uuid": "test_uuid", "s3_file_key": "user-uploads/cheeseburger.jpeg", "labels": [{"Name": "PORK", "Confidence": 71.5260009765625}, {"Name": "FRIES", "Confidence": 67.23100280761719}, {"Name": "DHAL", "Confidence": 56.61600112915039}, {"Name": "BURGER", "Confidence": 56.055999755859375}]}