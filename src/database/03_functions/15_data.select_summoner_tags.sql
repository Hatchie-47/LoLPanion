CREATE OR REPLACE FUNCTION data.select_summoner_tags(
    _puu_id                 CHARACTER VARYING
) RETURNS TABLE (
    riot_match_id           BIGINT,
    server_id               SMALLINT,
    assigned                TIMESTAMP,
    tag_id                  SMALLINT,
    severity_id             SMALLINT,
    note                    CHARACTER VARYING
)
AS $$
BEGIN

    RETURN QUERY
    SELECT  m.riot_match_id,
            m.id_server,
            m.match_end,
            at.id_tag,
            at.id_severity,
            at.note
    FROM data.summoners s
    JOIN data.participants p ON s.id = p.id_summoner
    JOIN data.matches m ON p.id_match = m.id
    JOIN data.assigned_tags at ON m.id = at.id_match AND at.id_summoner = s.id
    WHERE s.riot_puu_id = _puu_id
    ORDER BY m.match_end DESC;

END;
$$ LANGUAGE plpgsql;