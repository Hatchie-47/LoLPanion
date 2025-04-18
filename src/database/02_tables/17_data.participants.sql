DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.participants
    (
        id_match integer NOT NULL,
        id_summoner integer NOT NULL,
        team_red boolean,
        id_role smallint,
        id_champion integer,
        runes_primary integer,
        runes_secondary integer,
        runes integer[],
        items integer[],
        kills smallint,
        deaths smallint,
        assists smallint,
        champion_mastery_points integer,
        summ_spell_1 smallint,
        summ_spell_2 smallint,
        total_gold smallint,
        cs smallint,
        small_runes smallint[],
        bot boolean,
        mastery_points integer,
        CONSTRAINT pk_participants PRIMARY KEY (id_match, id_summoner),
        CONSTRAINT participants_id_game_fkey FOREIGN KEY (id_match)
            REFERENCES data.matches (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION,
        CONSTRAINT participants_id_player_fkey FOREIGN KEY (id_summoner)
            REFERENCES data.summoners (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION,
        CONSTRAINT participants_id_role_fkey FOREIGN KEY (id_role)
            REFERENCES data.roles (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.participants OWNER TO loladmin;

END
$$;