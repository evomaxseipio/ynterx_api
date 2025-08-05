-- Query completo para obtener toda la información del contrato
-- Incluye: contrato, participantes, loan, properties, documentos, etc.

WITH contract_info AS (
    SELECT 
        c.contract_id,
        c.contract_number,
        c.contract_type,
        c.description,
        c.status,
        c.folder_path,
        c.version,
        c.is_active,
        c.contract_date,
        c.start_date,
        c.end_date,
        c.created_at as contract_created_at,
        c.updated_at as contract_updated_at
    FROM contract c
    WHERE c.contract_id = $1::uuid
),
participants_info AS (
    SELECT 
        cp.contract_id,
        cp.person_id,
        cp.person_type_id,
        cp.is_primary,
        cp.is_active as participant_active,
        cp.created_at as participant_created_at,
        -- Información de la persona
        p.first_name,
        p.last_name,
        p.middle_name,
        p.date_of_birth,
        p.gender,
        p.nationality_country,
        p.marital_status,
        p.occupation,
        -- Tipo de persona
        pt.name as person_type_name,
        pt.description as person_type_description,
        -- Información específica según el tipo
        CASE 
            WHEN cp.person_type_id = 1 THEN -- Cliente
                jsonb_build_object(
                    'client_id', cl.client_id,
                    'client_type_id', cl.client_type_id,
                    'credit_limit', cl.credit_limit,
                    'client_rating', cl.client_rating,
                    'is_active', cl.is_active,
                    'created_at', cl.created_at
                )
            WHEN cp.person_type_id = 2 THEN -- Inversionista
                jsonb_build_object(
                    'investor_id', inv.investor_id,
                    'investor_type_id', inv.investor_type_id,
                    'investment_limit', inv.investment_limit,
                    'investment_amount', inv.investment_amount,
                    'preferred_interest_rate', inv.preferred_interest_rate,
                    'risk_tolerance_id', inv.risk_tolerance_id,
                    'is_active', inv.is_active,
                    'created_at', inv.created_at,
                    'investor_type_name', it.type_name
                )
            WHEN cp.person_type_id = 3 THEN -- Testigo
                jsonb_build_object(
                    'witness_id', w.witness_id,
                    'document_relation', w.document_relation,
                    'occupation', w.occupation,
                    'relationship_with_client', w.relationship_with_client,
                    'notes', w.notes,
                    'is_active', w.is_active,
                    'created_at', w.created_at
                )
            WHEN cp.person_type_id = 7 THEN -- Notario
                jsonb_build_object(
                    'notary_id', n.notary_id,
                    'license_number', n.license_number,
                    'issuing_entity', n.issuing_entity,
                    'issue_date', n.issue_date,
                    'expiration_date', n.expiration_date,
                    'jurisdiction', n.jurisdiction,
                    'office_name', n.office_name,
                    'professional_email', n.professional_email,
                    'professional_phone', n.professional_phone,
                    'notes', n.notes,
                    'is_active', n.is_active,
                    'created_at', n.created_at
                )
            WHEN cp.person_type_id = 8 THEN -- Referente
                jsonb_build_object(
                    'referrer_id', r.referrer_id,
                    'referral_code', r.referral_code,
                    'referrer_phone_number', r.referrer_phone_number,
                    'bank_name', r.bank_name,
                    'bank_account', r.bank_account,
                    'commission_percentage', r.commission_percentage,
                    'notes', r.notes,
                    'is_active', r.is_active,
                    'created_at', r.created_at
                )
            ELSE NULL
        END as role_specific_data
    FROM contract_participant cp
    INNER JOIN person p ON cp.person_id = p.person_id
    INNER JOIN person_type pt ON cp.person_type_id = pt.person_type_id
    -- Left joins para información específica de cada tipo
    LEFT JOIN client cl ON cp.person_id = cl.person_id AND cp.person_type_id = 1
    LEFT JOIN investor inv ON cp.person_id = inv.person_id AND cp.person_type_id = 2
    LEFT JOIN investor_type it ON inv.investor_type_id = it.investor_type_id
    LEFT JOIN witness w ON cp.person_id = w.person_id AND cp.person_type_id = 3
    LEFT JOIN notary n ON cp.person_id = n.person_id AND cp.person_type_id = 7
    LEFT JOIN referrer r ON cp.person_id = r.person_id AND cp.person_type_id = 8
    WHERE cp.contract_id = $1::uuid
),
loan_info AS (
    SELECT 
        l.loan_id,
        l.contract_id,
        l.loan_amount,
        l.interest_rate,
        l.loan_term_months,
        l.monthly_payment,
        l.total_payment,
        l.loan_status,
        l.loan_type,
        l.start_date,
        l.end_date,
        l.created_at as loan_created_at,
        l.updated_at as loan_updated_at,
        -- Información de la cuenta bancaria
        ba.bank_account_id,
        ba.account_number,
        ba.account_type,
        ba.bank_name,
        ba.routing_number,
        ba.is_active as bank_account_active
    FROM loan l
    LEFT JOIN bank_account ba ON l.bank_account_id = ba.bank_account_id
    WHERE l.contract_id = $1::uuid
),
properties_info AS (
    SELECT 
        p.property_id,
        p.contract_id,
        p.property_type,
        p.address_line1,
        p.address_line2,
        p.city,
        p.state,
        p.postal_code,
        p.country,
        p.property_value,
        p.property_description,
        p.is_active as property_active,
        p.created_at as property_created_at,
        p.updated_at as property_updated_at
    FROM property p
    WHERE p.contract_id = $1::uuid
),
documents_info AS (
    SELECT 
        pd.person_id,
        pd.document_id,
        pd.is_primary,
        pd.document_type,
        pd.document_number,
        pd.issuing_country_id,
        pd.document_issue_date,
        pd.document_expiry_date,
        pd.created_at as document_created_at
    FROM person_document pd
    INNER JOIN contract_participant cp ON pd.person_id = cp.person_id
    WHERE cp.contract_id = $1::uuid
),
addresses_info AS (
    SELECT 
        a.address_id,
        a.person_id,
        a.address_line1,
        a.address_line2,
        a.city_id,
        a.postal_code,
        a.address_type,
        a.is_principal,
        a.created_at as address_created_at
    FROM address a
    INNER JOIN contract_participant cp ON a.person_id = cp.person_id
    WHERE cp.contract_id = $1::uuid
)
SELECT 
    -- Información del contrato
    ci.*,
    
    -- Participantes agrupados por tipo
    jsonb_build_object(
        'clients', COALESCE(
            (SELECT jsonb_agg(
                jsonb_build_object(
                    'person_id', pi.person_id,
                    'first_name', pi.first_name,
                    'last_name', pi.last_name,
                    'middle_name', pi.middle_name,
                    'date_of_birth', pi.date_of_birth,
                    'gender', pi.gender,
                    'nationality_country', pi.nationality_country,
                    'marital_status', pi.marital_status,
                    'occupation', pi.occupation,
                    'is_primary', pi.is_primary,
                    'role_data', pi.role_specific_data,
                    'documents', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'document_id', di.document_id,
                                'is_primary', di.is_primary,
                                'document_type', di.document_type,
                                'document_number', di.document_number,
                                'issuing_country_id', di.issuing_country_id,
                                'document_issue_date', di.document_issue_date,
                                'document_expiry_date', di.document_expiry_date
                            )
                        )
                        FROM documents_info di
                        WHERE di.person_id = pi.person_id
                    ),
                    'addresses', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'address_id', ai.address_id,
                                'address_line1', ai.address_line1,
                                'address_line2', ai.address_line2,
                                'city_id', ai.city_id,
                                'postal_code', ai.postal_code,
                                'address_type', ai.address_type,
                                'is_principal', ai.is_principal
                            )
                        )
                        FROM addresses_info ai
                        WHERE ai.person_id = pi.person_id
                    )
                )
            )
            FROM participants_info pi
            WHERE pi.person_type_id = 1
            ), '[]'::jsonb
        ),
        'investors', COALESCE(
            (SELECT jsonb_agg(
                jsonb_build_object(
                    'person_id', pi.person_id,
                    'first_name', pi.first_name,
                    'last_name', pi.last_name,
                    'middle_name', pi.middle_name,
                    'date_of_birth', pi.date_of_birth,
                    'gender', pi.gender,
                    'nationality_country', pi.nationality_country,
                    'marital_status', pi.marital_status,
                    'occupation', pi.occupation,
                    'is_primary', pi.is_primary,
                    'role_data', pi.role_specific_data,
                    'documents', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'document_id', di.document_id,
                                'is_primary', di.is_primary,
                                'document_type', di.document_type,
                                'document_number', di.document_number,
                                'issuing_country_id', di.issuing_country_id,
                                'document_issue_date', di.document_issue_date,
                                'document_expiry_date', di.document_expiry_date
                            )
                        )
                        FROM documents_info di
                        WHERE di.person_id = pi.person_id
                    ),
                    'addresses', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'address_id', ai.address_id,
                                'address_line1', ai.address_line1,
                                'address_line2', ai.address_line2,
                                'city_id', ai.city_id,
                                'postal_code', ai.postal_code,
                                'address_type', ai.address_type,
                                'is_principal', ai.is_principal
                            )
                        )
                        FROM addresses_info ai
                        WHERE ai.person_id = pi.person_id
                    )
                )
            )
            FROM participants_info pi
            WHERE pi.person_type_id = 2
            ), '[]'::jsonb
        ),
        'witnesses', COALESCE(
            (SELECT jsonb_agg(
                jsonb_build_object(
                    'person_id', pi.person_id,
                    'first_name', pi.first_name,
                    'last_name', pi.last_name,
                    'middle_name', pi.middle_name,
                    'date_of_birth', pi.date_of_birth,
                    'gender', pi.gender,
                    'nationality_country', pi.nationality_country,
                    'marital_status', pi.marital_status,
                    'occupation', pi.occupation,
                    'is_primary', pi.is_primary,
                    'role_data', pi.role_specific_data,
                    'documents', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'document_id', di.document_id,
                                'is_primary', di.is_primary,
                                'document_type', di.document_type,
                                'document_number', di.document_number,
                                'issuing_country_id', di.issuing_country_id,
                                'document_issue_date', di.document_issue_date,
                                'document_expiry_date', di.document_expiry_date
                            )
                        )
                        FROM documents_info di
                        WHERE di.person_id = pi.person_id
                    ),
                    'addresses', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'address_id', ai.address_id,
                                'address_line1', ai.address_line1,
                                'address_line2', ai.address_line2,
                                'city_id', ai.city_id,
                                'postal_code', ai.postal_code,
                                'address_type', ai.address_type,
                                'is_principal', ai.is_principal
                            )
                        )
                        FROM addresses_info ai
                        WHERE ai.person_id = pi.person_id
                    )
                )
            )
            FROM participants_info pi
            WHERE pi.person_type_id = 3
            ), '[]'::jsonb
        ),
        'notaries', COALESCE(
            (SELECT jsonb_agg(
                jsonb_build_object(
                    'person_id', pi.person_id,
                    'first_name', pi.first_name,
                    'last_name', pi.last_name,
                    'middle_name', pi.middle_name,
                    'date_of_birth', pi.date_of_birth,
                    'gender', pi.gender,
                    'nationality_country', pi.nationality_country,
                    'marital_status', pi.marital_status,
                    'occupation', pi.occupation,
                    'is_primary', pi.is_primary,
                    'role_data', pi.role_specific_data,
                    'documents', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'document_id', di.document_id,
                                'is_primary', di.is_primary,
                                'document_type', di.document_type,
                                'document_number', di.document_number,
                                'issuing_country_id', di.issuing_country_id,
                                'document_issue_date', di.document_issue_date,
                                'document_expiry_date', di.document_expiry_date
                            )
                        )
                        FROM documents_info di
                        WHERE di.person_id = pi.person_id
                    ),
                    'addresses', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'address_id', ai.address_id,
                                'address_line1', ai.address_line1,
                                'address_line2', ai.address_line2,
                                'city_id', ai.city_id,
                                'postal_code', ai.postal_code,
                                'address_type', ai.address_type,
                                'is_principal', ai.is_principal
                            )
                        )
                        FROM addresses_info ai
                        WHERE ai.person_id = pi.person_id
                    )
                )
            )
            FROM participants_info pi
            WHERE pi.person_type_id = 7
            ), '[]'::jsonb
        ),
        'referrers', COALESCE(
            (SELECT jsonb_agg(
                jsonb_build_object(
                    'person_id', pi.person_id,
                    'first_name', pi.first_name,
                    'last_name', pi.last_name,
                    'middle_name', pi.middle_name,
                    'date_of_birth', pi.date_of_birth,
                    'gender', pi.gender,
                    'nationality_country', pi.nationality_country,
                    'marital_status', pi.marital_status,
                    'occupation', pi.occupation,
                    'is_primary', pi.is_primary,
                    'role_data', pi.role_specific_data,
                    'documents', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'document_id', di.document_id,
                                'is_primary', di.is_primary,
                                'document_type', di.document_type,
                                'document_number', di.document_number,
                                'issuing_country_id', di.issuing_country_id,
                                'document_issue_date', di.document_issue_date,
                                'document_expiry_date', di.document_expiry_date
                            )
                        )
                        FROM documents_info di
                        WHERE di.person_id = pi.person_id
                    ),
                    'addresses', (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'address_id', ai.address_id,
                                'address_line1', ai.address_line1,
                                'address_line2', ai.address_line2,
                                'city_id', ai.city_id,
                                'postal_code', ai.postal_code,
                                'address_type', ai.address_type,
                                'is_principal', ai.is_principal
                            )
                        )
                        FROM addresses_info ai
                        WHERE ai.person_id = pi.person_id
                    )
                )
            )
            FROM participants_info pi
            WHERE pi.person_type_id = 8
            ), '[]'::jsonb
        )
    ) as participants,
    
    -- Información del loan
    COALESCE(
        (SELECT jsonb_build_object(
            'loan_id', li.loan_id,
            'loan_amount', li.loan_amount,
            'interest_rate', li.interest_rate,
            'loan_term_months', li.loan_term_months,
            'monthly_payment', li.monthly_payment,
            'total_payment', li.total_payment,
            'loan_status', li.loan_status,
            'loan_type', li.loan_type,
            'start_date', li.start_date,
            'end_date', li.end_date,
            'created_at', li.loan_created_at,
            'updated_at', li.loan_updated_at,
            'bank_account', CASE 
                WHEN li.bank_account_id IS NOT NULL THEN
                    jsonb_build_object(
                        'bank_account_id', li.bank_account_id,
                        'account_number', li.account_number,
                        'account_type', li.account_type,
                        'bank_name', li.bank_name,
                        'routing_number', li.routing_number,
                        'is_active', li.bank_account_active
                    )
                ELSE NULL
            END
        )
        FROM loan_info li
        LIMIT 1
        ), '{}'::jsonb
    ) as loan,
    
    -- Información de las propiedades
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'property_id', pri.property_id,
                'property_type', pri.property_type,
                'address_line1', pri.address_line1,
                'address_line2', pri.address_line2,
                'city', pri.city,
                'state', pri.state,
                'postal_code', pri.postal_code,
                'country', pri.country,
                'property_value', pri.property_value,
                'property_description', pri.property_description,
                'is_active', pri.property_active,
                'created_at', pri.property_created_at,
                'updated_at', pri.property_updated_at
            )
        )
        FROM properties_info pri
        ), '[]'::jsonb
    ) as properties,
    
    -- Resumen de participantes
    jsonb_build_object(
        'total_participants', (SELECT COUNT(*) FROM participants_info),
        'clients_count', (SELECT COUNT(*) FROM participants_info WHERE person_type_id = 1),
        'investors_count', (SELECT COUNT(*) FROM participants_info WHERE person_type_id = 2),
        'witnesses_count', (SELECT COUNT(*) FROM participants_info WHERE person_type_id = 3),
        'notaries_count', (SELECT COUNT(*) FROM participants_info WHERE person_type_id = 7),
        'referrers_count', (SELECT COUNT(*) FROM participants_info WHERE person_type_id = 8),
        'has_loan', (SELECT COUNT(*) > 0 FROM loan_info),
        'properties_count', (SELECT COUNT(*) FROM properties_info)
    ) as summary

FROM contract_info ci; 