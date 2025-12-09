# Manual System Prompt Update Guide

## 🔧 Issues to Fix

Your agent has these problems:
1. ❌ Not asking for name verification
2. ❌ Not stating candidate's name  
3. ❌ Auto-marking as declined when wrong person answers

## ✅ Solution: Update System Prompt Manually

Since the API update failed, you need to update the prompt manually in Bolna Dashboard.

## 📋 Steps to Update

### Step 1: Go to Bolna Dashboard

1. Visit: https://platform.bolna.ai/
2. Log in
3. Navigate to your agent settings
4. Find agent: `aeb6eee0-20f2-4b23-b6ad-fe57bb0adf34`

### Step 2: Update Welcome Message

Find **"Welcome Message"** or **"Agent Welcome Message"** section:

**Current (WRONG):**
```
Hello! I'm Ava from Dharwin, calling regarding your job application.
```

**Change To (CORRECT):**
```
Hello, this is Ava calling from Dharwin.
```

### Step 3: Update System Prompt

Find **"System Prompt"** or **"Agent Prompts"** section and update with the content from `system_prompt.py`.

**Key Sections to Verify:**

1. **Name Verification (Section 2)** - Must be at the top:
   - Should say: "⭐ CRITICAL: NAME VERIFICATION IS REQUIRED FIRST"
   - Should say: "You MUST ask for name verification using the candidate's name"
   - Should say: "Hello, may I speak with {name} please?"

2. **Wrong Person Handling (Section 7)**:
   - Should say: "Wrong number ≠ Declined/Rejected"
   - Should say: "DO NOT mark as declined" for wrong person

3. **Decline Handling (Section 4)**:
   - Should require explicit confirmation
   - Should NOT assume decline from uncertain responses

### Step 4: Save Configuration

Click **"Save"** or **"Update Agent"** and wait for processing.

## 🎯 What the Fixed Prompt Does

### ✅ Correct Flow Now:
1. Welcome: "Hello, this is Ava calling from Dharwin."
2. **Name Verification**: "Hello, may I speak with Prakhar Sharma please?"
3. Wait for confirmation
4. If correct: Proceed with interview details
5. If wrong person: End gracefully without marking as declined

### ✅ Wrong Person Scenario:
- Agent: "Hello, may I speak with Prakhar Sharma please?"
- User: "I'm Tucker"
- Agent: "I apologize for the confusion. I'm trying to reach Prakhar Sharma. Thank you for your time."
- **Result**: Call ends, NO decline/rejection extracted ✅

### ✅ Decline Scenario:
- Agent: "Hello, may I speak with Prakhar Sharma please?"
- User: "Yes, this is Prakhar"
- Agent: [Discusses interview]
- User: "I'm not interested anymore"
- Agent: "Just to confirm - you're no longer interested, is that correct?"
- User: "Yes"
- **Result**: Extracted as REJECTED ✅

## 📝 Full System Prompt

The complete updated system prompt is in `system_prompt.py`. Copy the entire `SYSTEM_PROMPT` variable content and paste it into the Bolna Dashboard System Prompt field.

## ⚠️ Important Notes

1. **Name Variable**: The prompt uses `{name}` - this will be filled from `user_data` context automatically
2. **Welcome Message**: Keep it short - "Hello, this is Ava calling from Dharwin."
3. **Name Verification**: Agent will ask for name verification immediately after welcome message
4. **Context Variables**: Make sure `{name}` and `{candidate_name}` are in user_data (they already are in your code)

## 🧪 Testing After Update

1. Make a test call
2. Verify agent asks: "Hello, may I speak with [Name] please?"
3. Test with wrong person scenario
4. Verify it doesn't get marked as declined

---

**The prompt fixes are in `system_prompt.py` - copy the SYSTEM_PROMPT content to Bolna Dashboard!**

