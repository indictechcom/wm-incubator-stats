CREATE TABLE incubator_dashboard (
    project VARCHAR(50) ,                -- Project name, e.g., 'wikipedia', 'wiktionary'
    language_code VARCHAR(10),         -- Language code, e.g., 'en', 'fr'
    edit_count INT ,                    -- Total number of edits
    actor_count INT ,                   -- Total number of distinct editors
    pages_count INT ,                   -- Total number of distinct pages
    bytes_removed_30D INT ,             -- Total bytes removed in the last 30 days
    bytes_added_30D INT ,               -- Total bytes added in the last 30 days
    avg_edits_3M INT ,                  -- Average edits over the last 3 months
    avg_editors_3M INT                 -- Average editors over the last 3 months
);
