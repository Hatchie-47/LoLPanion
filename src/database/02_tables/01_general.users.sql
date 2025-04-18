DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS general.users
	(
	    id integer NOT NULL DEFAULT nextval('general.users_id_seq'::regclass),
	    id_server integer,
	    id_summoner integer NOT NULL,
	    CONSTRAINT pk_users PRIMARY KEY (id),
	    CONSTRAINT users_id_summoner UNIQUE (id_summoner),
	    CONSTRAINT users_id_server_fkey FOREIGN KEY (id_server)
	        REFERENCES data.servers (id) MATCH SIMPLE
	        ON UPDATE NO ACTION
	        ON DELETE NO ACTION,
	    CONSTRAINT users_id_summoner_fkey FOREIGN KEY (id_summoner)
	        REFERENCES data.summoners (id) MATCH SIMPLE
	        ON UPDATE NO ACTION
	        ON DELETE NO ACTION
	)

	TABLESPACE pg_default;

	ALTER TABLE IF EXISTS general.users OWNER TO loladmin;

END
$$;