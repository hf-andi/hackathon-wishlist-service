MOCK_DB_ENTRIES = [
    {
        "uuid": "d626d7d9-adc3-4c06-b24e-8a9ee04b8187",
        "s3_file_key": "cheeseburger.jpeg",
        "labels": [{"Name": "burger", "Confidence": 1}],
        "week":  "2023-W23",
        "index": 2
    }
]


def compare_labels(user_labels):
    """
    user_labels format: [{'Name': 'Food', 'Confidence': 94.69338989257812}]
    :return:
    """

    # get labels from dictionary where the labels contains the user labels
    db_recipes = MOCK_DB_ENTRIES

    best_match_score = 0
    best_match_id = ""
    for recipe in db_recipes:
        score = 0
        for label in user_labels:
            for recipe_label in recipe["labels"]:
                if recipe_label["Name"] == label["Name"]:
                    score += 1 * label["Confidence"] * recipe_label["Confidence"]
        if score > best_match_score and score > 50:
            best_match_score = score
            best_match_id = recipe["uuid"]

    print(f"the final score is {best_match_score}")
    return best_match_id

recipe_id = compare_labels([{'Name': 'burger', 'Confidence': 94.69338989257812}])
print(f"{recipe_id} is the id of the final recipe")


