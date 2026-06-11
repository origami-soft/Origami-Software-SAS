-- Cambiar configuraciones de producción a homologación
UPDATE wsaa_configuration SET type = 'homologation' WHERE type = 'production';

-- Limpiar claves privadas y certificados
UPDATE wsaa_configuration SET private_key = NULL, certificate = NULL, certificate_request = NULL;

-- Limpiar tokens de acceso
UPDATE wsaa_token SET token = NULL, sign = NULL, expiration_time = NULL;
