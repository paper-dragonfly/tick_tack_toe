import psycopg2
from configparser import ConfigParser #to do with accesing .ini files


# Get connection data from config.ini 
def config(config_file:str='config/config.ini', section:str='postgresql') -> dict:
    # pdb.set_trace()
    parser = ConfigParser()
    parser.read(config_file)
    db = {}
    if parser.has_section(section):
        item_tups = parser.items(section)
        for tup in item_tups:
            db[tup[0]] = tup[1]
    else:
        raise Exception(f"Section {section} not found in file {config_file}")
    return db 

params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

####
name = 'db_tet'
sql = "SELECT * FROM saved_games WHERE saved_games.game_name = %s"
sql2 = "SELECT game_name FROM saved_games"
sql3 = "UPDATE ttt_users SET wins = 0 WHERE ttt_users.user_name = 'paper_dragonfly' "
sql4 = "INSERT INTO ttt_users(user_name) VALUES('nickleboo') ON CONFLICT (user_name) DO NOTHING"
sql5 = """SELECT MAX("rank") FROM ttt_users""" 

sql_get_summary_stats = """ 
    WITH 
    winner_tally AS(
        SELECT COUNT(*)::float AS ct, winner 
        FROM ttt_log
        GROUP BY winner),
        
    player1_tally AS(
        SELECT COUNT(*)::float as ct, player1 
        FROM ttt_log
        GROUP BY player1),
        
    player2_tally AS(
        SELECT COUNT(*) as ct, player2 
        FROM ttt_log
        GROUP BY player2),

    combo AS(
        Select
        CASE WHEN p1.player1 is NULL THEN 0 ELSE p1.ct END AS ct1,
        CASE WHEN p2.player2 is NULL THEN 0 ELSE p2.ct END AS ct2,
        CASE WHEN p2.player2 is NULL THEN p1.player1 ELSE p2.player2 END AS player  
        FROM player2_tally as p2
        FULL JOIN player1_tally as p1 ON p2.player2 = p1.player1)

    SELECT player, combo.ct1 + combo.ct2 AS "total_games", winner_tally.ct/(combo.ct1 + combo.ct2)AS percent_wins FROM combo
    FULL JOIN winner_tally ON combo.player = winner_tally.winner
    ORDER BY percent_wins DESC NULLS LAST;"""

cur.execute(sql_get_summary_stats)
summary_stats = cur.fetchall() # player name, total games, %wins


# create leader_board dict, populate with highest ranked player
highest_ranked_player = summary_stats[0][0]
leader_board = {'Player': ['Total Games', '%wins', 'Rank'],
highest_ranked_player:[summary_stats[0][1], summary_stats[0][2], 1]}


for i in range(1,len(summary_stats)):
    cur_player_tup = summary_stats[i]
    #add player to leader_board dict
    leader_board[cur_player_tup[0]] = [cur_player_tup[1], cur_player_tup[2]]
    prev_rank = leader_board[summary_stats[i-1][0]][2]
    prev_pwins = summary_stats[i-1][2]
    cur_pwins = cur_player_tup[2]
    if prev_pwins == cur_pwins: # same %wins -> same rank
        leader_board[cur_player_tup[0]].append(prev_rank)
    else: #lower %wins -> lower rank
        leader_board[cur_player_tup[0]].append(i+1)
print leader_board



#### 

conn.commit()
conn.close() 