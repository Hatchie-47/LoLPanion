CREATE OR REPLACE FUNCTION data.upsert_match(
    _riot_match_id          BIGINT,
    _id_server              INTEGER,
    _match_start            TIMESTAMP,
    _match_end              TIMESTAMP,
    _winning_team_red       BOOLEAN,
    _match_creation         TIMESTAMP,
    _game_version           CHARACTER VARYING
) RETURNS INTEGER
AS $$
DECLARE
    _id_match               INTEGER;
BEGIN

    INSERT INTO data.matches(riot_match_id, id_server, match_start, match_end, winning_team_red, match_creation, game_version)
    VALUES (_riot_match_id, _id_server, _match_start, _match_end, _winning_team_red, _match_creation, _game_version)
    ON CONFLICT (id_server, riot_match_id)
    DO UPDATE
    SET match_start         = COALESCE(EXCLUDED.match_start, matches.match_start),
        match_end           = COALESCE(EXCLUDED.match_end, matches.match_end),
        winning_team_red    = COALESCE(EXCLUDED.winning_team_red, matches.winning_team_red),
        match_creation      = COALESCE(EXCLUDED.match_creation, matches.match_creation),
        game_version        = COALESCE(EXCLUDED.game_version, matches.game_version)
    RETURNING id INTO _id_match;

    RETURN _id_match;

END;
$$ LANGUAGE plpgsql;