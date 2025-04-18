DO LANGUAGE plpgsql $$
BEGIN

    CREATE TABLE IF NOT EXISTS general.current_settings
    (
        setting character varying COLLATE pg_catalog."default" NOT NULL,
        setting_value character varying COLLATE pg_catalog."default",
        CONSTRAINT current_settings_setting UNIQUE (setting)
    )

    TABLESPACE pg_default;

    ALTER TABLE general.current_settings OWNER TO loladmin;

    INSERT INTO general.current_settings(setting)
    VALUES  ('id_user'),
            ('riot_api_key'),
            ('ddragon_version')
    ON CONFLICT (setting)
    DO NOTHING;

END
$$;