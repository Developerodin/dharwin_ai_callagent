# Voice Processing Fix Guide

## 🔧 Issue: Agent Not Processing Voice

If the agent isn't able to process your voice, here are the fixes and improvements:

## 🎯 Common Causes

1. **Language/Accent Mismatch** - Agent only configured for English
2. **Aggressive Endpointing** - Cutting off speech too early
3. **Audio Quality Issues** - Sampling rate or encoding problems
4. **Model Version** - Using older transcription model

## ✅ Solutions Applied

### 1. Updated Transcriber Configuration

**Changes made:**
- ✅ Language: Changed from `"en"` to `"en-US"` (more specific)
- ✅ Endpointing: Increased from `100ms` to `500ms` (less aggressive)
- ✅ Smart Formatting: Enabled
- ✅ Punctuation: Enabled
- ✅ Interim Results: Enabled (faster response)

### 2. Updated Task Configuration

**Improvements:**
- ✅ Hangup after silence: `10s` → `15s`
- ✅ Number of words for interruption: `2` → `1` (more responsive)
- ✅ Trigger user online message: `10s` → `8s` (check sooner)
- ✅ Generate precise transcript: Enabled

## 🚀 How to Apply Fixes

### Option 1: Use the Fix Script (Recommended)

```bash
python fix_voice_processing.py
```

This will:
1. Fetch your current agent configuration
2. Update transcriber settings
3. Save changes to Bolna API

### Option 2: Update via Bolna Dashboard

1. Go to https://platform.bolna.ai/
2. Navigate to your agent settings
3. Find "Transcriber" configuration section
4. Update settings:
   - Model: `nova-2` (or `nova-3` if available)
   - Language: `en-US` (or your language)
   - Endpointing: `500ms`
   - Enable: Smart Format, Punctuation, Interim Results

### Option 3: Update Code and Recreate Agent

If you recreate the agent, the updated configuration in `bolna_agent.py` will be used.

## 🌐 Multi-Language Support

If you need to support multiple languages (English + Hindi):

### Option A: Enable Language Detection

Update transcriber config:
```json
{
  "language": null,  // null enables auto-detection
  "language_detection": true
}
```

Update task config:
```json
{
  "language_detection_turns": 3  // Detect language after 3 turns
}
```

### Option B: Create Separate Agents

Create separate agents for:
- English-only agent
- Hindi-only agent
- Or use language codes: `"en"`, `"hi"`, `"en-IN"`, etc.

## 🎤 Audio Quality Improvements

### If Voice Still Not Processing:

1. **Check Phone Line Quality**
   - Use a good connection (WiFi/4G/5G)
   - Reduce background noise
   - Speak clearly

2. **Adjust Endpointing**
   - Too low (100ms): Cuts off speech
   - Too high (1000ms+): Slow responses
   - Recommended: 500ms (balanced)

3. **Try Different Models**
   - `nova-2`: Latest, best accuracy
   - `nova-1`: Fallback option
   - `whisper`: Alternative provider

## 🔍 Testing Voice Processing

### Test with Simple Phrases

1. **Clear Speech Test**
   - Say: "Hello, this is a test"
   - Check if agent responds

2. **Accent Test**
   - Speak naturally with your accent
   - Agent should still understand

3. **Background Noise Test**
   - Test in quiet environment first
   - Then test with normal background noise

### Check Transcripts

After a call, check the transcript:
```bash
python view_webhook_data.py --execution-id <execution_id> --full
```

Look for:
- ✅ Complete sentences transcribed
- ✅ Correct words recognized
- ✅ No missing audio

## 📊 Current Configuration

Your current transcriber settings (after fix):

```json
{
  "provider": "deepgram",
  "model": "nova-2",
  "language": "en-US",
  "stream": true,
  "sampling_rate": 16000,
  "encoding": "linear16",
  "endpointing": 500,
  "smart_format": true,
  "punctuate": true,
  "interim_results": true
}
```

## 🆘 Troubleshooting

### Issue: Still Not Processing Voice

1. **Check Agent Status**
   ```bash
   python verify_webhook_config.py
   ```

2. **Test with Different Voice**
   - Try speaking slower
   - Try speaking louder
   - Check if microphone works

3. **Check Execution Logs**
   - View call execution details
   - Check for transcription errors
   - Look at execution logs

4. **Contact Support**
   - Check Bolna AI documentation
   - Contact Bolna support with execution ID
   - Provide sample of problematic audio

## ✅ Success Indicators

After applying fixes, you should see:
- ✅ Agent responds to your voice
- ✅ Transcripts are accurate
- ✅ No missing words in transcription
- ✅ Faster response times
- ✅ Better handling of pauses

## 🔄 Next Steps

1. **Apply the fix**: `python fix_voice_processing.py`
2. **Test with a call**: Make a test call
3. **Check transcripts**: Verify accuracy
4. **Adjust if needed**: Fine-tune endpointing/other settings

---

**Need more help?** Check execution logs or contact Bolna AI support!

