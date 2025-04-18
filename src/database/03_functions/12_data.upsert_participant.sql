CREATE OR REPLACE FUNCTION data.upsert_participant(
    _riot_puu_id                CHARACTER VARYING,
    _match_id                   INTEGER,
    _team_red                   BOOLEAN,
    _id_role                    SMALLINT,
    _summspell1                 SMALLINT,
    _summspell2                 SMALLINT,
    _champion                   SMALLINT,
    _mastery_points             INTEGER,
    _bot                        BOOLEAN,
    _runes_primary              SMALLINT,
    _runes_secondary            SMALLINT,
    _runes                      SMALLINT[],
    _small_runes                SMALLINT[],
    _kills                      SMALLINT,
    _deaths                     SMALLINT,
    _assists                    SMALLINT,
    _items                      SMALLINT[],
    _total_gold                 SMALLINT,
    _cs                         SMALLINT,
    OUT _id_match               INTEGER,
    OUT _id_summoner            INTEGER
)
AS $$
BEGIN

    INSERT INTO data.participants(id_match, id_summoner, team_red, id_role, id_champion, mastery_points, runes_primary, runes_secondary, runes, items, kills, deaths, assists, champion_mastery_points, summ_spell_1, summ_spell_2, total_gold, cs, small_runes, bot)
    SELECT  _match_id,
            id,
            _team_red,
            _id_role,
            _champion,
            _mastery_points,
            _runes_primary,
            _runes_secondary,
            _runes,
            _items,
            _kills,
            _deaths,
            _assists,
            NULL,
            _summspell1,
            _summspell2,
            _total_gold,
            _cs,
            _small_runes,
            _bot
    FROM data.summoners
    WHERE riot_puu_id = _riot_puu_id
    ON CONFLICT (id_match, id_summoner)
    DO UPDATE
    SET team_red                    = COALESCE(EXCLUDED.team_red, participants.team_red),
        id_role                     = COALESCE(EXCLUDED.id_role, participants.id_role),
        id_champion                 = COALESCE(EXCLUDED.id_champion, participants.id_champion),
        mastery_points              = COALESCE(EXCLUDED.mastery_points, participants.mastery_points),
        runes_primary               = COALESCE(EXCLUDED.runes_primary, participants.runes_primary),
        runes_secondary             = COALESCE(EXCLUDED.runes_secondary, participants.runes_secondary),
        runes                       = COALESCE(EXCLUDED.runes, participants.runes),
        items                       = COALESCE(EXCLUDED.items, participants.items),
        kills                       = COALESCE(EXCLUDED.kills, participants.kills),
        deaths                      = COALESCE(EXCLUDED.deaths, participants.deaths),
        assists                     = COALESCE(EXCLUDED.assists, participants.assists),
        champion_mastery_points     = COALESCE(EXCLUDED.champion_mastery_points, participants.champion_mastery_points),
        summ_spell_1                = COALESCE(EXCLUDED.summ_spell_1, participants.summ_spell_1),
        summ_spell_2                = COALESCE(EXCLUDED.summ_spell_2, participants.summ_spell_2),
        total_gold                  = COALESCE(EXCLUDED.total_gold, participants.total_gold),
        cs                          = COALESCE(EXCLUDED.cs, participants.cs),
        small_runes                 = COALESCE(EXCLUDED.small_runes, participants.small_runes),
        bot                         = COALESCE(EXCLUDED.bot, participants.bot)
    RETURNING id_match, id_summoner INTO _id_match, _id_summoner;

    RETURN;

END;
$$ LANGUAGE plpgsql;

