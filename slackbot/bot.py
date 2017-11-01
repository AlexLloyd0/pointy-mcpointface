from flask import Flask, request, Response, jsonify
import re
import json
import logging

from typing import Tuple, Dict, Optional
from collections import namedtuple

logger = logging.getLogger(__name__)


class Slackbot:
    def __init__(self, api_token: str, scores: Dict[str, int]):
        self.api_token = api_token
        self.change_score = re.compile('^([^+\-=])+ ((\+\+|--)|((\+=|-=) [0-9]+))( .*)?$')
        self.scored_user = namedtuple('ScoredUser', ['user', 'score'])
        self.scores = scores
        self.max_assignment = 50

        self.app = Flask(__name__)
        self.app.run(host='0.0.0.0')

        self.users = self._get_users()

    def main(self):

        @self.app.route('/add-points', methods=['POST'])
        def add_points():
            text = request.form.get('text', '')
            if self.change_score.match(text):
                self._parse_and_update(event)
            elif text.startswith('score '):
                self._post_score(event)
            elif text == 'scoreboard':
                self._print_scoreboard(event)
            if 'that would be great' in text.lower() and link not in text:
                return jsonify(text=link)
            return Response(), 200

        second = 0
        try:
            if self.slack_client.rtm_connect():
                print('Running rtm client')
                while True:
                    if second == 0:
                        self.users = self._get_users()
                    events = self.slack_client.rtm_read()
                    for event in events:
                        logger.debug(f"Event logged: {event}")
                        if (
                            'channel' in event and
                            'text' in event and
                            event.get('type') == 'message' and
                            event.get('user') != 'U7QNFJKEH'  # Don't do anything if it's pointy doing the pointing
                        ):
                            text = event['text']
                            if self.change_score.match(text):
                                self._parse_and_update(event)
                            elif text.startswith('score '):
                                self._post_score(event)
                            elif text == 'scoreboard':
                                self._print_scoreboard(event)
                    time.sleep(1)
                    second = second + 1 % 600
            else:
                print('Connection failed, invalid token?')
        except Exception as e:
            print(e)
            self.main()

    def _parse_and_update(self, event: dict):
        subject, points, reason = parse_message(event['text'])
        if subject not in self.users:
            return
        elif subject[2:-1] == event.get('user'):
            self.slack_client.api_call(
                'chat.postMessage',
                channel=event['channel'],
                text="Naughty! You can't assign yourself points! -1 for you",
                as_user='true:'
            )
            self._update_score(subject, -1, event['channel'], 'for trying to give himself points')
        elif abs(points) > self.max_assignment:
            self.slack_client.api_call(
                'chat.postMessage',
                channel=event['channel'],
                text="Don't be silly now.",
                as_user='true:'
            )
        else:
            self._update_score(subject, points, reason, event['channel'])

    def _update_score(self, subject: str, points: int, reason: str, channel: str):
        print(f"Adding {points} to {subject}'s score")
        if subject not in self.scores:
            self.scores[subject] = 0
        old_score = self.scores[subject]
        self.scores[subject] += points
        if self.scores[subject] == 0:
            del self.scores[subject]
        with open('scores.json', 'w+') as file:
            json.dump(self.scores, file)
        response = f'{subject}: {old_score} -> {self.scores.get(subject, 0)} {reason}'
        self.slack_client.api_call(
            'chat.postMessage',
            channel='C7Q8H378C',
            text=response,
            as_user='true:'
        )

    def _post_score(self, event: dict):
        subject = 'score '.join(event['text'].split('score ')[1:])
        print(f"Posting {subject}'s score to channel {event['channel']}")
        score = self.scores.get(subject, 0)
        response = f'Points make prizes!\n{subject} has {score} point{"s" if score != 1 else " "}'
        self.slack_client.api_call(
            'chat.postMessage',
            channel=event['channel'],
            text=response,
            as_user='true:'
        )

    def _print_scoreboard(self, event: dict):
        print(f"Posting scoreboard to channel {event['channel']}")
        scored_tuples = [self.scored_user(subject, self.scores[subject]) for subject in self.scores]
        ordered_tuples = sorted(scored_tuples, key=lambda x: x.score, reverse=True)
        response = f'Here\'s a list of my favourite people:'
        for i in range(len(ordered_tuples)):
            subject, score = ordered_tuples[i]
            response += f'\n{i+1}. {subject} [{score} point{"s" if score != 1 else ""}]'
            if i == 0:
                response += ' :crown:'
            elif i + 1 == len(ordered_tuples):
                response += ' :hankey:'
        self.slack_client.api_call(
            'chat.postMessage',
            channel=event['channel'],
            text=response,
            as_user='true:'
        )

    def _get_users(self):
        users_dict = {}
        raw_users = self.slack_client.api_call('users.list')
        for user in raw_users['members']:
            users_dict[user['id']] = user
        return users_dict

    # def _add_zero_users(self):
    #     for user in self._get_users():
    #         if '<@' + user + '>' not in self.scores:
    #             self.scores['<@' + user + '>'] = 0


def parse_message(message: str) -> Tuple[str, int, str]:
    logger.debug(f"Parsing {message}")
    if '++' in message:
        split = message.split('+')
        subject = split[0][:-1]
        reason = '+'.join(split[2:])
        logger.debug(f"Message parsed: {subject} needs 1 point {reason}")
        return subject, 1, reason
    elif '--' in message:
        split = message.split('-')
        subject = split[0][:-1]
        reason = '-'.join(split[2:])
        logger.debug(f"Message parsed: {subject} needs -1 point {reason}")
        return subject, -1, reason
    else:
        equal_split = message.split('=')
        subject = equal_split[0][:-2]
        sign = equal_split[0][-1]
        space_split = equal_split[1].split(' ')
        str_score = space_split[1]
        score = int(sign + str_score)

        reason = ' '.join(space_split[2:]) if len(space_split) > 2 else ''
        logger.debug(f'Message parsed: {subject} needs {score} point{"s" if score != 1 else " "} {reason}')
        return subject, score, reason
