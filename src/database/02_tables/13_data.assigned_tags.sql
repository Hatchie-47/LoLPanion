DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.assigned_tags
    (
        id_tag smallint NOT NULL,
        id_severity smallint,
        note character varying COLLATE pg_catalog."default",
        id_match integer NOT NULL,
        id_summoner integer NOT NULL,
        CONSTRAINT assigned_tags_id_match_id_summoner_fkey FOREIGN KEY (id_match, id_summoner)
            REFERENCES data.participants (id_match, id_summoner) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION,
        CONSTRAINT assigned_tags_id_severity_fkey FOREIGN KEY (id_severity)
            REFERENCES data.severity (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION,
        CONSTRAINT assigned_tags_id_tag_fkey FOREIGN KEY (id_tag)
            REFERENCES data.tags (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.assigned_tags OWNER TO loladmin;

    CREATE UNIQUE INDEX IF NOT EXISTS uq_assignedtags_id_match_id_summoner_id_tag
        ON data.assigned_tags USING btree
        (id_match ASC NULLS LAST, id_summoner ASC NULLS LAST, id_tag ASC NULLS LAST)
        TABLESPACE pg_default;

END
$$;