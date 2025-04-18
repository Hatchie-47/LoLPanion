DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.severity
    (
        id smallint NOT NULL,
        name character varying COLLATE pg_catalog."default" NOT NULL,
        CONSTRAINT severity_id PRIMARY KEY (id)
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.severity OWNER TO loladmin;

    INSERT INTO data.severity(id, name)
    VALUES  (1, 'HIGH'),
            (2, 'MEDIUM'),
            (3, 'LOW')
    ON CONFLICT (id)
    DO UPDATE
    SET name = EXCLUDED.name;

    PERFORM setval((SELECT pg_get_serial_sequence('data.severity', 'id'))::regclass, (SELECT MAX(id) FROM data.severity));

END
$$;