CREATE OR REPLACE FUNCTION general.get_user(
) RETURNS TABLE (
    _name                   CHARACTER VARYING,
    _tagline                CHARACTER VARYING,
    _puu_id                 CHARACTER VARYING
)
AS $$
DECLARE
    _summoner_id           INTEGER;
    _user_id               SMALLINT;
BEGIN

    RETURN QUERY
    SELECT  s.gamename,
            s.tagline,
            s.riot_puu_id
    FROM general.current_settings cs
    JOIN general.users u ON cs.setting_value::INTEGER = u.id
    JOIN data.summoners s ON s.id = u.id_summoner AND s.id_server = u.id_server
    WHERE cs.setting = 'id_user';

END;
$$ LANGUAGE plpgsql;