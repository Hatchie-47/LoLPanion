CREATE OR REPLACE FUNCTION general.get_setting(
    _setting                CHARACTER VARYING
) RETURNS CHARACTER VARYING
AS $$
DECLARE
    _value                  CHARACTER VARYING;
BEGIN

    SELECT  setting_value
    INTO _value
    FROM general.current_settings
    WHERE setting = _setting;

    RETURN _value;

END;
$$ LANGUAGE plpgsql;