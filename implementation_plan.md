# Dynamic Language Selection (Hinglish Plan)

## Goal (Kya karna hai)
Aap chahte hain ki Language button click karne par ek menu khule jisme saari available languages hon. Aur sabse khaas baat: `Senpai/locales` folder mein jo bhi nayi `.json` file daali jaye (jaise `es.json`), wo automatically us menu mein button ban kar aa jaye. Iske alawa, group mein select ki gayi language ko yaad rakhna hoga taaki bot usi language mein reply kare.

## User Review Required
> [!IMPORTANT]
> Abhi bot ko nahi pata ki kis group ne kaunsi language chuni hai (kyunki ye database mein save nahi hota). Is feature ke liye humein database mein language save karne ka system banana hoga. 

## Proposed Changes (Kaise banayenge)

### 1. Database (MongoDB) Updates
- `Senpai/core/mongo.py` mein `get_chat_lang(chat_id)` aur `set_chat_lang(chat_id, lang)` functions add karenge.
- Isse har group ya user ki language `groups` collection mein save hogi.

### 2. Localization Files (`en.json`, `hi.json`)
- In files ke andar ek naya naam daalenge, jaise `"language_name": "English"` aur `"language_name": "हिन्दी (Hindi)"`.
- Isse bot ko pata chal jayega ki button par kaunsa naam dikhana hai.

### 3. Contextual Language (Smart Reply System)
- Abhi bot ke code mein hazaron jagah `get_string()` likha hai jo humesha English uthata hai.
- Ek-ek jagah change karne ke bajaye, hum Python ka ek smart feature (`contextvars`) use karenge.
- Jab bhi kisi group mein message aayega, bot automatically us group ki saved language ko "yaad" kar lega aur us message ke reply ke liye wahi language use karega.

### 4. Naya Plugin (`language.py`)
- Ek nayi file `Senpai/plugins/language.py` banayenge.
- Jab koi `/start` wale menu mein "Language" button dabayega, toh ye plugin saari `.json` files padhega aur unke buttons bana dega.
- Jaise hi koi language select hogi, ye use database mein save kar dega aur naye language mein success message bhej dega.

## Verification Plan (Check kaise karenge)
### Manual Verification
- Group mein "Language" button dabayenge.
- Dekhenge ki "English" aur "हिन्दी" dono button aa rahe hain ya nahi.
- "हिन्दी" select karke check karenge ki uske baad ke sabhi commands (jaise `/ping`, `/profile`) Hindi mein aa rahe hain ya nahi.
- Kisi dusre group mein jaakar check karenge ki wahan default (English) hi chal rahi ho.
