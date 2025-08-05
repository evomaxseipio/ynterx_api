-- Verificar si existe el stored procedure sp_create_referrer
SELECT 
    p.proname as function_name,
    pg_get_function_arguments(p.oid) as arguments,
    pg_get_function_result(p.oid) as return_type,
    p.oid as function_oid
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname = 'sp_create_referrer'
ORDER BY p.oid;

-- Ver la definición completa del stored procedure
SELECT 
    pg_get_functiondef(p.oid) as function_definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname = 'sp_create_referrer'
LIMIT 1; 