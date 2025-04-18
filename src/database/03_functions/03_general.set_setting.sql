CREATE OR REPLACE FUNCTION general.set_setting(
    _setting                CHARACTER VARYING,
    _value                  CHARACTER VARYING
) RETURNS BOOLEAN
AS $$
BEGIN

    INSERT INTO general.current_settings (setting, setting_value)
    VALUES (_setting, _value)
    ON CONFLICT (setting)
    DO UPDATE
    SET setting_value           = EXCLUDED.setting_value;

    RETURN TRUE;

END;
$$ LANGUAGE plpgsql;