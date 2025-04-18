DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS data.servers
    (
        id integer NOT NULL DEFAULT nextval('data.servers_id_seq'::regclass),
        server character varying COLLATE pg_catalog."default",
        region_cluster character varying COLLATE pg_catalog."default",
        CONSTRAINT pk_servers PRIMARY KEY (id)
    )

    TABLESPACE pg_default;

    ALTER TABLE IF EXISTS data.servers OWNER TO loladmin;

    INSERT INTO data.servers(id, server, region_cluster)
    VALUES  (1, 'euw1', 'europe')
    ON CONFLICT (id)
    DO UPDATE
    SET server          = EXCLUDED.server,
        region_cluster  = EXCLUDED.region_cluster;

    PERFORM setval((SELECT pg_get_serial_sequence('data.servers', 'id'))::regclass, (SELECT MAX(id) FROM data.servers));

END
$$;