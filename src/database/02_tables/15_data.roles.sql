DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.roles
    (
        id smallint NOT NULL DEFAULT nextval('data.positions_id_seq'::regclass),
        name character varying COLLATE pg_catalog."default",
        CONSTRAINT positions_pkey PRIMARY KEY (id)
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.roles OWNER TO loladmin;

    INSERT INTO data.roles(id, name)
    VALUES  (1, 'TOP'),
            (2, 'JUNGLE'),
            (3, 'MID'),
            (4, 'BOT'),
            (5, 'SUPPORT'),
            (6, 'UNKNOWN')
    ON CONFLICT (id)
    DO UPDATE
    SET name = EXCLUDED.name;

    PERFORM setval((SELECT pg_get_serial_sequence('data.roles', 'id'))::regclass, (SELECT MAX(id) FROM data.roles));

END
$$;