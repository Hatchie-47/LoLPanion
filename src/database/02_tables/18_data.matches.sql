DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.matches
    (
        id integer NOT NULL DEFAULT nextval('data.games_id_seq'::regclass),
        riot_match_id bigint,
        id_server smallint,
        match_start timestamp without time zone,
        match_end timestamp without time zone,
        winning_team_red boolean,
        match_creation timestamp without time zone,
        game_version character varying COLLATE pg_catalog."default",
        CONSTRAINT pk_games PRIMARY KEY (id),
        CONSTRAINT matches_id_server_match_id UNIQUE (id_server, riot_match_id),
        CONSTRAINT games_id_region_cluster_fkey FOREIGN KEY (id_server)
            REFERENCES data.servers (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.matches OWNER TO loladmin;

END
$$;