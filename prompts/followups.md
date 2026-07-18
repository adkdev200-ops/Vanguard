════════════════════════════════════════════════════════════════
POST-EXECUTION FOLLOW-UP
════════════════════════════════════════════════════════════════

Your task is to determine if the requested information is temporarily unavailable but is expected to become available at a known future date or time.

You MUST use the structured output tool provided to record this assessment.

Rules:
• If the information is urgent/time-sensitive and a reliable future time is known, set `needs_followup` to true.
• If no reliable retry time exists (e.g., evergreen information, speculation, unknown dates, or the information was already successfully found), set `needs_followup` to false.
• Use the exact query, not a generic description.
• `research_time` must be the current execution time.
• Do not invent dates or times.
• Keep `attempts` concise (1–3 items).

Example logic:
If searching for "Official Nepal election results" and they are not yet published but expected at 15:00 NPT, set needs_followup=true and populate next_check accordingly.
If the information is already found, or it's a general topic like "Weekly dose of AI", set needs_followup=false.

CRITICAL INSTRUCTION: You must output ONLY valid JSON. Do not include any markdown formatting, code blocks (like ```json), backticks, or explanatory text before or after the JSON object.