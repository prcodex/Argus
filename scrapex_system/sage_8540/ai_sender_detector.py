"""
AI-Powered Sender Detection - v2
Enhanced to separate WSJ Opinion from other WSJ content
"""

import anthropic
import re
from bs4 import BeautifulSoup

def extract_email_metadata(author, content_html, title):
    """Extract key metadata for sender identification"""
    
    # Email domain from author
    email_domain = ""
    if '@' in str(author):
        email_domain = str(author).split('@')[-1].strip().rstrip('>')
    
    # Extract footer/signature from HTML
    footer_text = ""
    if content_html:
        soup = BeautifulSoup(str(content_html), 'html.parser')
        
        # Look for common footer patterns
        footers = soup.find_all(['footer', 'div'], class_=re.compile(r'footer|signature|legal', re.I))
        if footers:
            footer_text = footers[0].get_text()[:500]
        else:
            # Get last few lines as potential footer
            all_text = soup.get_text()
            lines = all_text.split('\n')
            footer_text = '\n'.join(lines[-10:])[:500]
    
    return email_domain, footer_text

def detect_sender_with_ai(author, title, content_html, api_key):
    """
    Use Claude Haiku to identify the sender
    SPECIAL HANDLING: Separates WSJ Opinion from other WSJ content
    Returns: (sender_tag, confidence, reasoning)
    """
    
    email_domain, footer = extract_email_metadata(author, title, content_html)
    
    # Create detection prompt with WSJ Opinion distinction
    prompt = f"""You are identifying the sender/source of an email for categorization.

EMAIL METADATA:
- Author field: {author}
- Email domain: {email_domain}
- Title/Subject: {title}
- Footer/signature: {footer[:300]}

KNOWN SENDERS TO MATCH:
- WSJ Opinion (domains: @wsj.com, @barrons.com, @dowjones.com + "Opinion:" in title or opinion content)
- WSJ (domains: @wsj.com, @barrons.com, @dowjones.com - all other WSJ content)
- Goldman Sachs (domains: @gs.com, @email.amazonses.com, patterns: "Global Markets", "Economics")
- Bloomberg (domains: @bloomberg.com, @bloomberg.net)
- Business Insider (domains: @businessinsider.com, @email.businessinsider.com)
- Financial Times / FT (domains: @ft.com, @email.ft.com)
- Rosenberg_EM (domains: @rosenbergresearch.com + subject contains "Early Morning with Dave" OR content contains "Fundamental Recommendations")
- Rosenberg Research (domains: @rosenbergresearch.com - all other Rosenberg emails)
- Itau (Brazilian bank, Portuguese content)
- Estadão (Brazilian news, domains: @estadao.com.br)
- Folha (Brazilian news, domains: @folhadespaulo.com.br)
- Reuters (domains: @thomsonreuters.com)
- John Cochrane / The Grumpy Economist
- Adam Tooze (Chartbook)
- Torsten Slok (Apollo, @apollo.com)
- Matt Stoller (BIG Newsletter)
- Shadow Price Macro (Robin Brooks)
- MacroTourist (Kevin Muir)
- Macro Mornings
- Topdown Charts
- TKer (Sam Ro)

CRITICAL DISTINCTIONS:
- If WSJ/Barron's domain AND title contains "Opinion:" → Tag as "WSJ Opinion"
- If WSJ/Barron's domain but NO "Opinion:" → Tag as "WSJ"
- If Rosenberg domain AND (subject contains "Early Morning with Dave" OR content contains "Fundamental Recommendations") → Tag as "Rosenberg_EM"
- If Rosenberg domain but NOT "Early Morning" → Tag as "Rosenberg Research"

TASK:
Identify the most likely sender from the list above, or suggest a new sender name if it's clearly different.

Respond ONLY with this JSON format:
{{
    "sender_tag": "Exact name from list or new name",
    "confidence": "HIGH/MEDIUM/LOW",
    "reasoning": "One sentence why"
}}

Examples:
- @wsj.com + "Opinion: Trump Strikes" → {{"sender_tag": "WSJ Opinion", "confidence": "HIGH", "reasoning": "WSJ domain with Opinion prefix in title"}}
- @wsj.com + "The 10-Point" → {{"sender_tag": "WSJ", "confidence": "HIGH", "reasoning": "WSJ domain with news briefing content"}}
- @barrons.com + "Opinion: Nobody Ever Got Younger" → {{"sender_tag": "WSJ Opinion", "confidence": "HIGH", "reasoning": "Barron's (WSJ family) with Opinion content"}}
"""
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Cheap, fast
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        
        # Parse JSON response
        import json
        # Extract JSON from response (might have markdown)
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            result = json.loads(json_match.group(0))
            return (
                result.get('sender_tag', 'Unknown'),
                result.get('confidence', 'LOW'),
                result.get('reasoning', 'No reasoning provided')
            )
        
        return ('Unknown', 'LOW', 'Failed to parse AI response')
        
    except Exception as e:
        print(f"   ⚠️  AI detection error: {e}")
        return ('Unknown', 'LOW', str(e))

if __name__ == "__main__":
    print("AI Sender Detector v2 - WSJ Opinion separation enabled")
