DO LANGUAGE plpgsql $$
BEGIN

    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname = 'general') THEN
        CREATE SCHEMA general;
	END IF;

END
$$;