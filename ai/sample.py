import api.prototype as api


def every_tick(api: api.API):
    print(f"I am {api.get_team_id()}, score is {api.get_score()}")
