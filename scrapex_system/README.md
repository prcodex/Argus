# 🎯 SCRAPEX Complete System Backup
**Date:** October 31, 2025  
**System:** ARGUS Intelligence Platform - Complete Production Environment

---

## 📋 System Overview

This backup contains the complete SCRAPEX intelligent email processing system with:
- **Multi-tier adaptive enrichment** (11 specialized handlers)
- **AI-powered sender detection**
- **Admin interface for rule management**
- **Real-time email intelligence feed**

---

## 🚀 Services Architecture

### Port 8540: SAGE Main Interface ⭐
**Primary intelligence feed with AI enrichment**

**Files:**
- `sage4_interface_fixed.py` - Flask web interface (37KB)
- `sage4_gmail_robust.py` - Gmail fetcher with pattern-based tagging (23KB)
- `ai_sender_detector.py` - Claude Haiku AI fallback detection (5KB)
- `templates/sage_4.0_interface.html` - Frontend UI (79KB)
- `start_sage4.sh` - Service startup script

**Features:**
- Real-time email feed from Gmail IMAP
- Pattern-based sender detection (21 senders)
- AI-powered tagging fallback
- User rating system
- Sender blocking
- HTML email display
- Auto-refresh every 15 minutes

**Access:** `http://44.225.226.126:8540`

**Database:** LanceDB on S3 (`s3://sage-unified-feed-lance/sage4/`)

---

### Port 8542: Chart Intelligence Dashboard 📊
**AI-powered chart analysis and visualization**

**Files:**
- `chart_intelligence_dashboard_fixed.py` - Chart analysis service

**Purpose:** Processes and enriches emails containing charts/graphs

**Access:** `http://44.225.226.126:8542`

---

### Port 8543: SCRAPEX Admin Interface ⚙️
**Production rule management dashboard**

**Files:**
- `scrapex_admin.py` - Flask admin application (8.1KB)
- `templates/admin_dashboard.html` - Admin UI (23KB)
- `start_scrapex_admin.sh` - Service startup script

**Features:**
1. **Allowed Senders Tab**
   - View all 21 authorized senders
   - See email patterns (e.g., `*@bloomberg.com`)
   - Edit sender tags and descriptions

2. **Tag Mappings Tab** ✅
   - Edit 41 tag-to-handler mappings
   - Assign handlers to sender tags
   - Examples: `Rosenberg_EM` → `rosenberg_deep_research_handler.py`

3. **Detection Rules Tab** ✅
   - Visual rule builder
   - Email-specific format:
     - Sender dropdown (from allowlist)
     - Subject contains field
     - Body contains field
     - AND/OR logic selector
   - **Test Rule** feature (shows matching emails from 8540)
   - 16 pre-configured rules

4. **Handlers Tab**
   - View all 25 enrichment handlers
   - See handler descriptions and trigger conditions

5. **Blocked Senders Tab**
   - Manage spam/unwanted senders
   - Pattern-based blocking

**Access:** `http://44.225.226.126:8543`

**Data Storage:**
- `configs/allowed_senders.json` - Sender whitelist
- `configs/tag_detection_rules.json` - Tagging conditions
- `configs/tag_to_rule_mapping.py` - Handler assignments
- `configs/blocked_senders.json` - Blocklist

---

### Port 8544: Test Senders Editor 🧪
**Testing environment for Allowed Senders features**

**Files:**
- `test_senders_admin.py` - Test Flask app (2.9KB)
- `templates/test_senders.html` - Test UI (12KB)

**Purpose:**
- Safe testing of Allowed Senders editor
- Email pattern editing (wildcards like `*@domain.com`)
- Isolated from production

**Access:** `http://44.225.226.126:8544`

---

## 🎨 Enrichment Handlers (25 Total)

### Priority Chain:
1. **aaa_universal_handler.py** - Universal fallback (16KB)
2. **gold_standard_enhanced_handler.py** - Deep thematic analysis (7.3KB)
3. **rosenberg_deep_research_handler.py** - Detailed 5-7 bullets (7.8KB)
4. **itau_daily_handler.py** - Portuguese summaries (7KB)
5. **cochrane_detailed_summary_handler.py** - Academic analysis (3.9KB)
6. **newsbrief_with_links_handler.py** - Briefing format (3.4KB)
7. **javier_blas_handler.py** - Bloomberg columnist (4.1KB)
8. **breakfast_with_dave_handler.py** - Headlines list (4.2KB)
9. **bloomberg_breaking_news_handler.py** - Title-only (1.9KB)
10. **wsj_teaser_handler.py** - Opinion alerts (2.1KB)

### Specialized Handlers:
- **ubs_research_handler.py** - UBS reports (14KB)
- **macrocharts_handler.py** - Chart-heavy emails (7.3KB)
- **gsrates_handler.py** - Goldman Sachs rates (6.5KB)
- **drive_research_handler.py** - Google Drive PDFs (12KB)
- **video_handler.py** - YouTube transcripts (12KB)
- **unstructured_pdf_handler.py** - PDF extraction (13KB)
- **shadow_handler.py** - Special format (13KB)
- **tony_pasquariello_handler.py** - Goldman analyst (3.7KB)
- **elerian_rep_handler.py** - Mohamed El-Erian (7KB)
- **joe_handler.py** - Specific author (4KB)
- **pilula_handler.py** - Brazilian content (4.5KB)
- **simple_corrections_handler.py** - Text cleanup (9.2KB)

### Orchestrator:
- **unified_adaptive_enrichment.py** - Routes to appropriate handler (11KB)

---

## 📊 Configuration Files

### `allowed_senders.json` (5.7KB)
21 authorized email senders with patterns:

```json
[
  {
    "email": "*@bloomberg.com",
    "sender_tag": "Bloomberg",
    "description": "Bloomberg News and Analysis"
  },
  {
    "email": "subscriptions@rosenbergresearch.com",
    "sender_tag": "Rosenberg_EM",
    "description": "Rosenberg Early Morning Research"
  }
]
```

### `tag_detection_rules.json` (3.2KB)
16 detailed detection conditions:

```json
{
  "Rosenberg_EM": {
    "sender": "subscriptions@rosenbergresearch.com",
    "subject_contains": ["Early Morning with Dave", "Fundamental Recommendations"],
    "body_contains": [],
    "logic": "OR",
    "description": "Deep research with 5-7 analytical bullets"
  }
}
```

### `tag_to_rule_mapping.py` (1.8KB)
41 tag-to-handler assignments:

```python
TAG_TO_HANDLER = {
    'Rosenberg_EM': 'rosenberg_deep_research_handler.py',
    'Rosenberg Research': 'rosenberg_headlines_handler.py',
    'Bloomberg': 'gold_standard_enhanced_handler.py',
    # ... 38 more mappings
}
```

### `blocked_senders.json` (1.1KB)
Spam prevention patterns

---

## 🔄 Data Flow

```
📧 Gmail IMAP
    ↓
sage4_gmail_robust.py (Pattern Detection)
    ↓
ai_sender_detector.py (AI Fallback)
    ↓
tag_detection_rules.json (Rule Matching)
    ↓
tag_to_rule_mapping.py (Handler Selection)
    ↓
unified_adaptive_enrichment.py (Orchestration)
    ↓
[Specialized Handler] (Content Analysis)
    ↓
LanceDB S3 (Storage)
    ↓
sage4_interface_fixed.py (Display)
    ↓
🌐 User Browser (8540)
```

---

## 🛠️ October 30-31 Improvements

### Fixed Issues:
1. **Rosenberg Tagging** ✅
   - "Early Morning with Dave" now correctly tagged as `Rosenberg_EM`
   - Added "Fundamental Recommendations" detection
   - Triggers deep research handler (5-7 bullets)

2. **Admin Interface** ✅
   - Complete rule management system
   - Visual editor for detection rules
   - Test Rule feature (preview matches)
   - Clean email-specific format

3. **Database Schema** ✅
   - Removed `updated_at`, `synced_at`, `author_email` fields
   - Fixed LanceDB schema mismatches
   - Prevented 404 errors

4. **AI Detection** ✅
   - Updated AI prompt to recognize `Rosenberg_EM`
   - Prevents AI override of pattern detection

### New Features:
- **Test Rule Button**: Preview emails matching conditions
- **Sender Dropdown**: Select from allowlist in rule editor
- **Subject/Body Fields**: Dedicated input fields
- **AND/OR Logic**: Simple logic selector
- **16 Pre-configured Rules**: All existing logic documented

---

## 📈 System Metrics

- **Total Senders:** 21 authorized
- **Total Handlers:** 25 specialized
- **Tag Mappings:** 41 configurations
- **Detection Rules:** 16 defined
- **Database:** LanceDB on S3
- **Enrichment Coverage:** ~95% of emails
- **Processing Speed:** 1-2 seconds per email

---

## 🚀 Quick Start

### Start All Services:
```bash
cd /home/ubuntu/newspaper_project

# Start SAGE (8540)
./start_sage4.sh

# Start Admin (8543)
./start_scrapex_admin.sh

# Check status
ps aux | grep -E "sage4|scrapex|chart"
netstat -tlnp | grep -E "8540|8542|8543|8544"
```

### Access Points:
- **Main Feed:** http://44.225.226.126:8540
- **Chart Dashboard:** http://44.225.226.126:8542
- **Admin:** http://44.225.226.126:8543
- **Test Environment:** http://44.225.226.126:8544

---

## 📝 Maintenance

### Cron Jobs:
```bash
# Gmail fetcher - every 30 minutes
*/30 * * * * /home/ubuntu/newspaper_project/sage4_gmail_robust.py

# AI enrichment - every 15 minutes
*/15 * * * * /home/ubuntu/newspaper_project/unified_adaptive_enrichment.py
```

### Logs:
```bash
tail -f /home/ubuntu/logs/sage4.log
tail -f /home/ubuntu/logs/enrichment.log
tail -f /home/ubuntu/logs/scrapex_admin.log
```

### Backups:
```bash
# Automatic daily backups to:
/home/ubuntu/backups/scrapex_daily_*.tar.gz

# Configuration backups:
/home/ubuntu/newspaper_project/*.json.backup_*
```

---

## 🔒 Security

- **AWS EC2 Instance:** i-06360d2516ecd4a35
- **Security Group:** sg-0f7792b4f0b5b1888
- **Allowed Ports:** 8540, 8542, 8543, 8544
- **S3 Bucket:** sage-unified-feed-lance (private)
- **API Keys:** Stored in environment variables

---

## 📚 Documentation

- `ROSENBERG_EM_COMPLETE_FIX.md` - Tagging fix details
- `VISUAL_RULE_BUILDER_GUIDE.md` - Admin interface guide
- `TEST_RULE_FEATURE.md` - Test functionality
- `ADMIN_QUICK_START.md` - Getting started
- `EXISTING_RULES_CONVERTED.md` - Rule migration

---

## 🎯 Key Achievements

✅ **Multi-tier adaptive enrichment** - 11 specialized handlers  
✅ **AI-powered tagging** - Pattern + AI hybrid  
✅ **Complete admin interface** - Full rule management  
✅ **Test environment** - Safe feature testing  
✅ **Comprehensive documentation** - Every component documented  
✅ **Production-ready** - Running 24/7 on AWS  

---

**System Status:** ✅ FULLY OPERATIONAL  
**Last Updated:** October 31, 2025  
**Version:** SCRAPEX 2.8 Complete

---

*This represents the complete SCRAPEX intelligent email processing system with all recent improvements and production-ready features.*
