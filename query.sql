WITH base_table AS (
  SELECT DISTINCT 
  	rev_id, 
    rev_actor, 
    rev_timestamp, 
    rev_len, 
    rev_parent_id,
  	page_namespace, 
    page_id, 
    actor_id,
  	REGEXP_SUBSTR(page_title, 'W[a-z]/[a-z]+') AS prefix,
  	rc_new_len - rc_old_len AS byte_diff
  FROM 
    revision rev
  JOIN 
    page 
    ON rev.rev_page = page.page_id
  JOIN 
    actor
    ON rev.rev_actor = actor.actor_id
  LEFT OUTER JOIN 
    recentchanges rc 
    ON rev.rev_id = rc.rc_this_oldid
  JOIN
  	user
  	ON actor.actor_id = user.user_id
  WHERE 
    page_namespace IN (0, 1, 10, 11, 14, 15, 828, 829) AND
  	-- explicity remove admins who often make edits across multiple incubating projects
  	NOT user_name IN ('MF-Warburg', 'Jon Harald Søby', 'Minorax')
  HAVING 
    prefix <> ''
  ORDER BY 
    rev_id DESC),

  primary_metrics AS (
    SELECT 
        prefix, 
        SUM(CASE WHEN byte_diff < 0 THEN byte_diff ELSE 0 END) AS bytes_removed_30D,
        SUM(CASE WHEN byte_diff >= 0 THEN byte_diff ELSE 0 END) AS bytes_added_30D,
    	COUNT(DISTINCT actor_id) AS actor_count,
    	COUNT(DISTINCT rev_id) AS edit_count,
    	COUNT(DISTINCT page_id) AS pages_count
    FROM 
        base_table
    GROUP BY 
        prefix),
  
  last_3M AS (
    SELECT 
        *, 
        YEAR(rev_timestamp) AS year, 
        MONTH(rev_timestamp) AS month
    FROM 
        base_table
    WHERE 
        MONTH(rev_timestamp) >= MONTH(NOW()) - 3 AND 
        MONTH(rev_timestamp) < MONTH(NOW()) AND
        YEAR(rev_timestamp) = YEAR(NOW())),
  
  monthly_grouping_3M AS (
    SELECT 
        prefix, 
        month, 
    	COUNT(DISTINCT rev_id) AS edits_by_month,
    	COUNT(DISTINCT actor_id) AS editors_by_month
    FROM 
        last_3M
    GROUP BY 
        prefix, 
        month),
    
  avg_table_3M AS (
    SELECT 
        prefix, 
    	AVG(edits_by_month) AS avg_edits_3M, 
    	AVG(editors_by_month) AS avg_editors_3M
    FROM 
        monthly_grouping_3M
    GROUP BY
        prefix)

SELECT 
    pm.prefix, 
    edit_count, 
    actor_count,
    bytes_added_30D, 
    bytes_removed_30D, 
    pages_count, 
    CAST(avg_edits_3M AS INT) AS avg_edits_3M, 
    CAST(avg_editors_3M AS INT) AS avg_editors_3M
FROM 
    primary_metrics pm
    JOIN avg_table_3M avg_3M ON avg_3M.prefix = pm.prefix
ORDER BY 
    avg_editors_3M DESC