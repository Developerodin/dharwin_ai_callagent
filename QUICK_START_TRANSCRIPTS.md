# Quick Guide: Using Transcript Storage

## 📝 What Changed

Transcripts are now stored **separately** in `data/transcripts.json` with candidate metadata (name, position, caller ID) for easy reading.

## 🚀 Usage

### View All Transcripts
```bash
python view_transcripts.py
```

### List Candidates with Transcripts
```bash
python view_transcripts.py --list
```

### View Transcripts for Specific Candidate
```bash
python view_transcripts.py --candidate=1
```

### View Specific Transcript by Execution ID
```bash
python view_transcripts.py --execution=2b822c24-991e-485c-b427-695be186d04f
```

## 📊 What's Stored

Each transcript includes:
- ✅ Candidate Name
- ✅ Position
- ✅ Candidate Phone & Email
- ✅ Caller ID (agent's phone number)
- ✅ Full Transcript
- ✅ Call Status & Duration
- ✅ Timestamp

## 🔄 Automatic Storage

Transcripts are automatically saved when:
- Webhook receives call completion data
- Transcript is available in the payload

No manual action needed - it happens automatically! 🎉

## 📁 File Location

- **Transcripts**: `data/transcripts.json`
- **Webhook Data**: `data/webhook_data.json` (unchanged)

Transcripts are organized by candidate ID for easy access.

