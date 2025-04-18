CREATE OR REPLACE FUNCTION data.upsert_summoner(
    _name                   CHARACTER VARYING,
    _tagline                CHARACTER VARYING,
    _riot_puu_id            CHARACTER VARYING,
    _id_server              SMALLINT,
    _summoner_level         SMALLINT,
    _profile_icon           SMALLINT,
    _revision_date          TIMESTAMP
) RETURNS INTEGER
AS $$
DECLARE
    _id_summoner            INTEGER;
BEGIN

    INSERT INTO data.summoners(gamename, tagline, riot_puu_id, id_server, summoner_level, profile_icon, revision_date)
    VALUES (_name, _tagline, _riot_puu_id, _id_server, _summoner_level, _profile_icon, _revision_date)
    ON CONFLICT (riot_puu_id)
    DO UPDATE
    SET gamename            = EXCLUDED.gamename,
        tagline             = EXCLUDED.tagline,
        id_server           = EXCLUDED.id_server,
        summoner_level      = COALESCE(EXCLUDED.summoner_level, summoners.summoner_level),
        profile_icon        = COALESCE(EXCLUDED.profile_icon, summoners.profile_icon),
        revision_date       = COALESCE(EXCLUDED.revision_date, summoners.revision_date)
    RETURNING id INTO _id_summoner;

    RETURN _id_summoner;

END;
$$ LANGUAGE plpgsql;