#!usr/bin/env python3
import json
import sys
import os
import math
import numpy as np

INPUT_FILE = "testdata.json"  # Constant variables are usually in ALL CAPS


class User:
    def __init__(self, name, gender, preferences, grad_year, responses):
        self.name = name
        self.gender = gender
        self.preferences = preferences
        self.grad_year = grad_year
        self.responses = responses


def cosine_similarity(v1, v2):
    """
    Cosine similarity, just took it off of stackoverflow. idk if this is
    correct lmao
    """
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]
        y = v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    return sumxy / math.sqrt(sumxx * sumyy)


def compare_responses(response1, response2, question_distribution):
    """
    This is a stupid 5 min attempt at trying to impelment the weighted
    question distribution as described in the google doc.

    Loops through responses of 2 users, for each time they
    answer the same thing, the score is weighted by
    1 / (1 + p), where p is the proportion of users that answered
    that question. Therefore, if p is high, the weight is lower.

    Then we divide that by the total number of equivalent answers,
    as ideally if the proportion is low for the same answers for every
    question the weighted proportion score should be close to 1
    """
    total_same = 0
    score = 0.0
    for i in range(len(response1)):
        if response1[i] == response2[i]:
            total_same += 1
            score += 1.0 / (1.0 + question_distribution[i][response1[i]])

    return score / total_same


def grad_year_comparison(year1, year2, gender1, gender2):
    """
    In this case different grad years could have different scores
    based off of the gender of the two.

    i.e. Grade difference of 3 might contribute less if the younger
    was a guy vs. a girl

    Actually this is probably the case with all relationships in
    hs/college - younger guy is usually less appealing

    I'm not assuming same sex couples here for ease as everyone on board
    is heterosexual based off of the data. Ooops.

    The max value is if both genders are opposite and year is the same,
    which is what we achieve here
    """
    if gender1 == gender2:
        return 0.3  # because what if...? not quite 0 because there's opportunities to ~explore~ ;)

    gender_constant = 0.3  # we add this constant if the male is younger
    year_constant = 0.1  # general year constant for each singular difference in year

    score = (
        1.0
        / (
            1.0
            + year_constant * abs(year1 - year2)
            + gender_constant * abs(year1 - year2)
        )
        if year1 < year2 and gender1 == "M" or year2 < year1 and gender2 == "M"
        else 1.0 / (1.0 + year_constant * abs(year1 - year2))
    )

    return score


# Takes in two user objects and outputs a float denoting compatibility
def compute_score(user1, user2, question_distribution):
    score = 0.0
    if user1.gender in user2.preferences and user2.gender in user1.preferences:
        score += 0.1

    answer_similarity = cosine_similarity(user1.responses, user2.responses)
    answer_similarity_weighted = compare_responses(
        user1.responses, user2.responses, question_distribution
    )
    grad_year = grad_year_comparison(
        user1.grad_year, user2.grad_year, user1.gender, user2.gender
    )
    score += answer_similarity * 0.6
    score += answer_similarity_weighted * 0.2
    score += grad_year * 0.1

    return score


if __name__ == "__main__":
    # Make sure input file is valid
    if not os.path.exists(INPUT_FILE):
        print("Input file not found")
        sys.exit(0)

    users = []
    with open(INPUT_FILE) as json_file:
        data = json.load(json_file)
        for user_obj in data["users"]:
            new_user = User(
                user_obj["name"],
                user_obj["gender"],
                user_obj["preferences"],
                user_obj["gradYear"],
                user_obj["responses"],
            )
            users.append(new_user)

    question_counts = np.zeros((len(users[0].responses), 6))
    question_distribution = np.zeros((len(users[0].responses), 6))

    for i in range(len(users)):
        user = users[i]
        responses = user.responses
        for j in range(len(responses)):
            question_counts[j][responses[j]] += 1

    for j in range(len(question_distribution)):
        total = np.sum(question_counts[j])
        for z in range(len(question_distribution[j])):
            if total != 0.0:
                question_distribution[j][z] = round(question_counts[j][z] / total, 3)

    for i in range(len(users) - 1):
        for j in range(i + 1, len(users)):
            user1 = users[i]
            user2 = users[j]
            score = compute_score(user1, user2, question_distribution)
            print(
                "Compatibility between {} and {}: {}".format(
                    user1.name, user2.name, score
                )
            )
