def get_battle_max(user_info, battles_data):
    current_rank = user_info["rank"]
    max_count = -1
    battle = None
    for battle in battles_data["battles"]:
        if current_rank < battle["minRank"] or current_rank > battle["maxRank"]:
            continue
        count = battle["redPeople"] + battle["bluePeople"] + battle["countPeople"]
        if count > max_count and battle["maxPeople"] < count:
            count = max_count
            battle = battle
    return battle

def battles_to_count(user_info, battles_data):
    current_rank = user_info["rank"]
    battles = {}
    for battle in battles_data["battles"]:
        if current_rank < battle["minRank"] or current_rank > battle["maxRank"]:
            continue
        count = battle["redPeople"] + battle["bluePeople"] + battle["countPeople"]
        battle_count = {
            battle,
            count,
        }
        battles.append(battle_count)