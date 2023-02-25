WITH base_table AS (
  SELECT DISTINCT 
  	rev_id, rev_actor, rev_timestamp, rev_len, rev_parent_id,
  	page_namespace, page_id, actor_id,
  	REGEXP_SUBSTR(page_title, 'W[a-z]/[a-z]+') AS prefix,
  	rc_new_len - rc_old_len AS byte_diff
  FROM revision rev
  JOIN page ON rev.rev_page = page.page_id
  JOIN actor ON rev.rev_actor = actor.actor_id
  LEFT OUTER JOIN recentchanges rc ON rev.rev_id = rc.rc_this_oldid
  WHERE page_namespace IN (0, 1, 10, 11, 14, 15, 828, 829)
  HAVING prefix <> ''
  ORDER BY rev_id DESC),
  
  edits_table AS (
  SELECT prefix, COUNT(DISTINCT rev_id) AS edit_count
  FROM base_table
  GROUP BY prefix),

  actor_table AS (
  SELECT prefix, COUNT(DISTINCT actor_id) AS actor_count
  FROM base_table
  GROUP BY prefix),

  byte_table AS (
  SELECT prefix, 
      SUM(CASE WHEN byte_diff < 0 THEN byte_diff ELSE 0 END) AS bytes_removed_30D,
      SUM(CASE WHEN byte_diff >= 0 THEN byte_diff ELSE 0 END) AS bytes_added_30D
  FROM base_table
  GROUP BY prefix),

  page_table AS (
  SELECT prefix, COUNT(DISTINCT page_id) AS pages_count
  FROM base_table
  GROUP BY prefix),
  
  last_3M AS (
    SELECT *, YEAR(rev_timestamp) AS year, MONTH(rev_timestamp) AS month
    FROM base_table
    WHERE MONTH(rev_timestamp) >= MONTH(NOW()) - 3
    AND MONTH(rev_timestamp) < MONTH(NOW())
  AND YEAR(rev_timestamp) = YEAR(NOW())),
  
  monthly_grouping AS (
    SELECT prefix, month, 
    	COUNT(DISTINCT rev_id) AS edits_by_month,
    	COUNT(DISTINCT actor_id) AS editors_by_month
    FROM last_3M
    GROUP BY prefix, month),
    
  avg_table AS (
    SELECT prefix, 
    	AVG(edits_by_month) AS avg_edits_3M, 
    	AVG(editors_by_month) AS avg_editors_3M
    FROM monthly_grouping
    GROUP BY prefix)

SELECT e.prefix, edit_count, actor_count, bytes_added_30D, bytes_removed_30D, pages_count, 
CAST(avg_edits_3M AS INT) AS avg_edits_3M, CAST(avg_editors_3M AS INT) AS avg_editors_3M
FROM edits_table e
JOIN actor_table a ON a.prefix = e.prefix
JOIN byte_table b  ON b.prefix = e.prefix
JOIN page_table p ON p.prefix = e.prefix
JOIN avg_table ON avg_table.prefix = e.prefix
ORDER BY e.edit_count DESC