DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.tags
    (
        id smallint NOT NULL DEFAULT nextval('data.tags_id_seq'::regclass),
        name character varying COLLATE pg_catalog."default",
        CONSTRAINT tags_pkey PRIMARY KEY (id)
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.tags OWNER TO loladmin;

    INSERT INTO data.severity(id, name)
    VALUES  (1, 'INTER'),
            (2, 'FLAMER'),
            (3, 'TILTER'),
            (4, 'UNDERPERFORMER'),
            (5, 'OVERPERFORMER'),
            (6, 'ONETRICK')
    ON CONFLICT (id)
    DO UPDATE
    SET name = EXCLUDED.name;

    PERFORM setval((SELECT pg_get_serial_sequence('data.tags', 'id'))::regclass, (SELECT MAX(id) FROM data.tags));

END
$$;