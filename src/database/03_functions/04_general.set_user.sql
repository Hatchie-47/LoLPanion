CREATE OR REPLACE FUNCTION general.set_user(
    _name                   CHARACTER VARYING,
    _tagline                CHARACTER VARYING,
    _riot_puu_id            CHARACTER VARYING,
    _id_server              SMALLINT
) RETURNS BOOLEAN
AS $$
DECLARE
    _summoner_id           INTEGER;
    _user_id               SMALLINT;
BEGIN

    SELECT data.upsert_summoner(_name, _tagline, _riot_puu_id, _id_server, NULL, NULL, NULL)
    INTO _summoner_id;

    INSERT INTO general.users(id_server, id_summoner)
    VALUES (_id_server, _summoner_id)
    ON CONFLICT (id_summoner)
    DO UPDATE
    SET id_server = EXCLUDED.id_server
    RETURNING id INTO _user_id;

    INSERT INTO general.current_settings (setting, setting_value)
    VALUES ('id_user', _user_id::CHARACTER VARYING)
    ON CONFLICT (setting)
    DO UPDATE
    SET setting_value           = EXCLUDED.setting_value;

    RETURN TRUE;

END;
$$ LANGUAGE plpgsql;