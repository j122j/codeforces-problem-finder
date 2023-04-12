import os
import random
from dotenv import load_dotenv
from codeforces import *

load_dotenv()
logged_in = False

if os.getenv('username') and os.getenv('password'):
    login(os.getenv('username'), os.getenv('password'))
    print(f"Logged in as {get_handle()}")
    logged_in = True

handles = []
problems = get_problems()
solved_problems = []
unsolved_problems = problems


def find_problems(ratings, tags):
    result = []
    filtered_problems = [
        problem for problem in unsolved_problems if 'rating' in problem]

    if len(tags) > 0:
        filtered_problems = [
            problem for problem in filtered_problems if any(tag in problem['tags'] for tag in tags)]

    for rating in ratings:
        ratted_problems = [
            problem for problem in filtered_problems if problem['rating'] == rating]
        if len(ratted_problems) > 0:
            result.append(random.choice(ratted_problems))
    return result


while True:
    print("""

Codeforces Problem Finder
1. Set handles
2. Get problems
3. Create mashup
4. Exit

""")
    try:
        choice = int(input('Enter your choice: '))
    except:
        print('Invalid choice')
        continue
    if choice == 1:
        handles = input('Enter handles: ').split()
        solved_problems = get_solved_problems(handles)
        unsolved_problems = [problem for problem in problems if problem['name']
                             not in solved_problems]
    elif choice == 2:
        ratings = list(map(int, input(
            'Enter ratings: ').split()))
        tags = input('Enter tags (comma separated): ').split(',')
        if tags == ['']:
            tags = []
        print()
        problems = find_problems(ratings, tags)
        for problem in problems:
            print(
                f"Rating: {problem['rating']} | Name: {problem['name']} | URL: {problem_url(problem)} | Tags: {','.join(problem['tags'])}")
    elif choice == 3:
        if not logged_in:
            print('Not logged in')
            continue
        name = input('Enter mashup name: ')
        duration = int(input('Enter duration (in minutes): '))
        ratings = list(map(int, input(
            'Enter ratings: ').split()))
        tags = input('Enter tags (comma separated): ').split(',')
        if tags == ['']:
            tags = []

        problems = find_problems(ratings, tags)
        if len(problems) == 0:
            print('No problems found')
            continue

        mashup_id = create_mashup(name, duration, problems)

        print(f"Mashup created: https://codeforces.com/gym/{mashup_id}")

    else:
        print('Exiting')
        break
