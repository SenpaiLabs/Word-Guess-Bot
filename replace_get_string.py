import os, re
files = [
    'Senpai/plugins/userprofile.py',
    'Senpai/plugins/stats.py',
    'Senpai/plugins/start.py',
    'Senpai/plugins/ping.py',
    'Senpai/plugins/leaderboard.py',
    'Senpai/plugins/guess.py',
    'Senpai/plugins/game.py'
]

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace get_string("key") with get_string(m.chat.id, "key")
    # For _format_block in userprofile.py, we might need a special fix
    content = re.sub(r'get_string\("([^"]+)"\)', r'get_string(m.chat.id, "\1")', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Replaced get_string in plugins')
