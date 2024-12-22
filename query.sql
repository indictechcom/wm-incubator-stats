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
    ON actor.actor_name = user.user_name
  WHERE 
    page_namespace IN (0, 1, 10, 11, 14, 15, 828, 829) AND
    page_is_redirect = 0 AND
    -- explicitly remove admins who often make edits across multiple incubating projects
    NOT user_name IN ('MF-Warburg', 'Jon Harald Søby', 'Minorax')
  HAVING 
    prefix <> ''
  ORDER BY 
    rev_id DESC
),

first_primary_metrics AS (
  SELECT 
      actor_id,
      COUNT(DISTINCT rev_id) AS edit_count
  FROM 
      base_table
  GROUP BY 
      actor_id
  HAVING 
      COUNT(DISTINCT rev_id) > 10
),

primary_metrics AS (
  SELECT 
      base_table.prefix, 
      SUM(CASE WHEN byte_diff < 0 THEN byte_diff ELSE 0 END) AS bytes_removed_30D,
      SUM(CASE WHEN byte_diff >= 0 THEN byte_diff ELSE 0 END) AS bytes_added_30D,
      COUNT(DISTINCT CASE WHEN first_primary_metrics.actor_id IS NOT NULL THEN base_table.actor_id ELSE NULL END) AS actor_count,
      COUNT(DISTINCT base_table.rev_id) AS edit_count,
      COUNT(DISTINCT base_table.page_id) AS pages_count
  FROM 
      base_table
  LEFT JOIN 
      first_primary_metrics 
      ON base_table.actor_id = first_primary_metrics.actor_id
  GROUP BY 
      base_table.prefix
),

last_3M AS (
  SELECT 
      base_table.*, 
      YEAR(rev_timestamp) AS year, 
      MONTH(rev_timestamp) AS month
  FROM 
      base_table
  WHERE 
      MONTH(rev_timestamp) >= MONTH(NOW()) - 3 AND 
      MONTH(rev_timestamp) < MONTH(NOW()) AND
      YEAR(rev_timestamp) = YEAR(NOW())
),

monthly_grouping_3M AS (
  SELECT 
      last_3M.prefix, 
      last_3M.month, 
      COUNT(DISTINCT last_3M.rev_id) AS edits_by_month,
      COUNT(DISTINCT CASE WHEN first_primary_metrics.actor_id IS NOT NULL THEN last_3M.actor_id ELSE NULL END) AS editors_by_month
  FROM 
      last_3M
  LEFT JOIN 
      first_primary_metrics 
      ON last_3M.actor_id = first_primary_metrics.actor_id
  GROUP BY 
      last_3M.prefix, 
      last_3M.month
),
    
avg_table_3M AS (
  SELECT 
      monthly_grouping_3M.prefix, 
      AVG(edits_by_month) AS avg_edits_3M, 
      AVG(editors_by_month) AS avg_editors_3M
  FROM 
      monthly_grouping_3M
  GROUP BY
      monthly_grouping_3M.prefix
),

-- Map the project and language_code
mapped_metrics AS (
  SELECT 
      REGEXP_SUBSTR(primary_metrics.prefix, 'W[a-z]') AS project_code,
      SUBSTRING_INDEX(primary_metrics.prefix, '/', -1) AS language_code,
      primary_metrics.edit_count,
      primary_metrics.actor_count,
      primary_metrics.bytes_added_30D, 
      primary_metrics.bytes_removed_30D, 
      primary_metrics.pages_count, 
      CAST(avg_table_3M.avg_edits_3M AS INT) AS avg_edits_3M, 
      CAST(avg_table_3M.avg_editors_3M AS INT) AS avg_editors_3M
  FROM 
      primary_metrics
  JOIN avg_table_3M 
      ON avg_table_3M.prefix = primary_metrics.prefix
),

-- Map project_code to project name
final_metrics AS (
  SELECT
      CASE 
          WHEN project_code = 'Wp' THEN 'wikipedia'
          WHEN project_code = 'Wq' THEN 'wikiquote'
          WHEN project_code = 'Wt' THEN 'wiktionary'
          WHEN project_code = 'Wy' THEN 'wikivoyage'
          WHEN project_code = 'Wb' THEN 'wikibooks'
          WHEN project_code = 'Wn' THEN 'wikinews'
          ELSE 'unknown'
      END AS project,
      language_code,
      edit_count,
      actor_count,
      bytes_added_30D, 
      bytes_removed_30D, 
      pages_count, 
      avg_edits_3M, 
      avg_editors_3M
  FROM 
      mapped_metrics
)

SELECT 
    project,
    language_code,
    edit_count AS edits,
    actor_count AS editors,
    pages_count AS pages, 
    bytes_removed_30D, 
    bytes_added_30D, 
    avg_edits_3M AS avg_monthly_edits, 
    avg_editors_3M AS avg_monthly_editors 
FROM 
    final_metrics
ORDER BY 
    avg_editors_3M DESC;
