-- Deploy seattleflu/schema:receiving/clinical to pg
-- requires: receiving/schema

begin;

set local search_path to receiving;

create table clinical (
    clinical_id integer primary key generated by default as identity,

    -- Using json not jsonb because we want to keep the exact text around for
    -- debugging purposes.
    document json not null
        constraint clinical_document_is_object
            check (json_typeof(document) = 'object'),

    received timestamp with time zone not null default now(),

    processing_log jsonb not null default '[]'
        constraint clinical_processing_log_is_array
            check (jsonb_typeof(processing_log) = 'array')
);

comment on table clinical is
    'Append-only set of clinical documents';

comment on column clinical.clinical_id is
    'Internal id of this record';

comment on column clinical.document is
    'JSON document created from a pre-processed Excel file';

comment on column clinical.received is
    'When the document was received';

comment on column clinical.processing_log is
    'Event log recording details of ETL into the warehouse';

commit;