DO LANGUAGE plpgsql $$
BEGIN

    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname = 'data') THEN
        CREATE SCHEMA data;
	END IF;

END
$$;