import requests
import random
import re
import json

# public api


def cf_public_api(method, **kwargs):
    url = f'https://codeforces.com/api/{method}'
    response = requests.get(url, params=kwargs)
    data = response.json()
    return data


def get_problems():
    print('Loading problems')
    data = cf_public_api('problemset.problems')
    problems = data['result']['problems']
    return problems


def get_submissions(handle):
    data = cf_public_api('user.status', handle=handle)
    submissions = data['result']
    return submissions


def get_solved_problems(handles):
    submissions = []
    for handle in handles:
        submissions += get_submissions(handle)

    solved_problems = set([submission['problem']['name']
                          for submission in submissions if submission['verdict'] == 'OK'])
    return list(solved_problems)


def problem_url(problem):
    return f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"


# authorized api

session = requests.Session()


def get_csrf_token(path):
    url = 'https://codeforces.com/' + path
    response = session.get(url)
    text = response.text
    csrf_token = re.findall(r"data-csrf='(.+)'", text)[0]
    return csrf_token


def get_handle():
    response = session.get('https://codeforces.com/')
    text = response.text
    handle = re.findall(r'handle = "(.+)"', text)[0]
    return handle


def gen_ftaa():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(18))


def gen_bfaa():
    return 'f1b3f18c715565b589b7823cda7448ce'


def login(username, password):
    csrf = get_csrf_token('enter')
    ftaa = gen_ftaa()
    bfaa = gen_bfaa()

    response = session.post('https://codeforces.com/enter', data={
        'csrf_token': csrf,
        'ftaa': ftaa,
        'bfaa': bfaa,
        'action': 'enter',
        'handleOrEmail': username,
        'password': password,
        '_tta': 176,
        'remember': 'off'
    })


def create_mashup(name, duration, problems):
    csrf = get_csrf_token('mashup/new')
    problemJson = []
    i = 0
    for problem in problems:
        queryRes = session.post(
            'https://codeforces.com/data/mashup', data={
                'action': 'problemQuery',
                'problemQuery': f"{problem['contestId']}{problem['index']}",
                'previouslyAddedProblemCount': i,
                'csrf_token': csrf
            },
            headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
            }
        )
        problemId = queryRes.json()['problems'][0]['id']
        problemJson.append({
            'id': problemId,
            'index': chr(ord('A') + i),
        })
        i += 1

    response = session.post('https://codeforces.com/data/mashup', data={
        'action': 'saveMashup',
        'isCloneContest': 'false',
        'parentContestId': '',
        'parentContestIdAndName': '',
        'contestName': name,
        'contestDuration': duration,
        'problemsJson': json.dumps(problemJson),
        'csrf_token': csrf
    })

    res = response.json()

    if 'success' in res and res['success'] == 'true':
        return res['newMashupContestId']
    else:
        print(res)
        return None
