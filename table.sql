CREATE TABLE IF NOT EXISTS incubator_dashboard (
    project VARCHAR(50) COMMENT "Name of wiki projects e.g., wikipedia, wiktionary." ,
    language_code VARCHAR(10) COMMENT "Specifies the Language code.",         
    edit_count INT COMMENT "Total number of edits made.",                    
    actor_count INT COMMENT "Total numbers of distinct editors.",                
    pages_count INT COMMENT "Total number of distinct pages.",
    bytes_removed_30D INT COMMENT "Total bytes removed in the last 30 days.",             
    bytes_added_30D INT COMMENT "Total bytes added in the last 30 days.",               
    avg_edits_3M INT COMMENT "Average edits over the last 3 months.",                  
    avg_editors_3M INT COMMENT "Average editors over the last 3 months."                 
)
ENGINE=InnoDB
COMMENT = 'Metrics about wikis on Wikimedia Incubator.';