-- Deploy seattleflu/schema:receiving/fhir to pg
-- requires: receiving/schema

begin;

set local search_path to receiving;

create table fhir (
    fhir_id integer primary key generated by default as identity,

    -- Using json not jsonb because we want to keep the exact text around for
    -- debugging purposes.
    document json not null
        constraint fhir_document_is_object
            check (json_typeof(document) = 'object'),

    received timestamp with time zone not null default now(),

    processing_log jsonb not null default '[]'
        constraint fhir_processing_log_is_array
            check (jsonb_typeof(processing_log) = 'array')
);

comment on table fhir is
    'Append-only set of FHIR documents';

comment on column fhir.fhir_id is
    'Internal id of this record';

comment on column fhir.document is
    'JSON document in FHIR format';

comment on column fhir.received is
    'When the document was received';

comment on column fhir.processing_log is
    'Event log recording details of ETL into the warehouse';

commit;