CREATE OR REPLACE FUNCTION data.insert_tag(
    _riot_match_id          BIGINT,
    _id_server              INTEGER,
    _puu_id                 CHARACTER VARYING,
    _tag_id                 SMALLINT,
    _severity_id            SMALLINT,
    _note                   CHARACTER VARYING
) RETURNS BOOLEAN
AS $$
BEGIN

    INSERT INTO data.assigned_tags(id_tag, id_severity, note, id_match, id_summoner)
    SELECT _tag_id, _severity_id, _note, id, (SELECT id FROM data.summoners WHERE riot_puu_id = _puu_id)
    FROM data.matches
    WHERE riot_match_id = _riot_match_id
      AND id_server = _id_server;

    RETURN TRUE;

END;
$$ LANGUAGE plpgsql;