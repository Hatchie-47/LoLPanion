DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.summoners
    (
        id integer NOT NULL DEFAULT nextval('data.players_id_seq'::regclass),
        gamename character varying COLLATE pg_catalog."default",
        riot_puu_id character varying COLLATE pg_catalog."default",
        id_server smallint NOT NULL,
        summoner_level smallint,
        profile_icon smallint,
        revision_date timestamp without time zone,
        tagline character varying COLLATE pg_catalog."default",
        CONSTRAINT pk_players PRIMARY KEY (id),
        CONSTRAINT summoners_riot_puu_id UNIQUE (riot_puu_id),
        CONSTRAINT summoners_id_server_fkey FOREIGN KEY (id_server)
            REFERENCES data.servers (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.summoners OWNER TO loladmin;

END
$$;