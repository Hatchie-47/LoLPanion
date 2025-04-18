import common.data_models as data_models
import common.db as db

TAG = {
    data_models.Tag.INTER: 1,
    data_models.Tag.FLAMER: 2,
    data_models.Tag.TILTER: 3,
    data_models.Tag.UNDERPERFORMER: 4,
    data_models.Tag.OVERPERFORMER: 5,
    data_models.Tag.ONETRICK: 6
}

SEVERITY = {
    data_models.Severity.HIGH: 1,
    data_models.Severity.MEDIUM: 2,
    data_models.Severity.LOW: 3
}


def enhance_summoner(summoner: data_models.Summoner) -> data_models.Summoner:
    """
    Adds tags to summoner object.
    :param summoner: Summoner object to add tags to.
    :return: Summoner object with tags added.
    """
    tags = []

    for tag in db.get_tags(riot_puu_id=summoner.puu_id):
        tags.append(data_models.AssignedTag(
            tag=[key for key, value in TAG.items() if value == int(tag[0][3])][0],
            added=tag[0][2],
            severity=[key for key, value in SEVERITY.items() if value == int(tag[0][4])][0],
            note=tag[0][5]
        ))

    summoner.tags = tags

    return summoner


def enhance_participant(participant: data_models.Participant, riot_match_id: int | None) -> data_models.Participant:
    """
    Adds tags from to participant object.
    :param participant: Participant object to add tags to.
    :param riot_match_id: If provided, add tags only from a specific match. If None, add tags from all matches.
    :return: Participant object with tags added.
    """
    tags = []
    participant_tags = []

    for tag in db.get_tags(riot_puu_id=participant.summoner.puu_id):
        prepared = data_models.AssignedTag(
            tag=[key for key, value in TAG.items() if value == int(tag[0][3])][0],
            added=tag[0][2],
            severity=[key for key, value in SEVERITY.items() if value == int(tag[0][4])][0],
            note=tag[0][5]
        )

        if riot_match_id is None or tag[0][0] == riot_match_id:
            participant_tags.append(prepared)
        tags.append(prepared)

    participant.tags = participant_tags
    participant.summoner.tags = tags

    return participant
