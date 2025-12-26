# LayerX Feature Testing Guide
**Test Date:** December 26, 2025

## Test Setup
- **Sender:** H:\LAYERX (alice - 7C4603E60D94F196)
- **Receiver:** H:\Layerx TEST (bob - 28610F905F277487)

---

## 📋 TEST CASES

### **Test Case 1: Basic Message (No Self-Destruct)**
**Steps:**
1. In sender terminal (H:\LAYERX): Type `send`
2. Select recipient: `bob`
3. Enter message: `Test 1: Basic message without self-destruct`
4. Self-destruct option: `1` (None)
5. Wait for successful transmission

**Expected Result:**
- ✅ Message sent successfully
- ✅ File created: `bob_TIMESTAMP_IP.png` + `.json`
- ✅ PSNR > 50 dB

---

### **Test Case 2: Self-Destruct Timer (5 minutes)**
**Steps:**
1. In sender: Type `send`
2. Select: `bob`
3. Message: `Test 2: Self-destruct in 5 minutes - Timer test`
4. Self-destruct: `3` (Timer)
5. Minutes: `5`

**Expected Result:**
- ✅ Timer starts when message revealed
- ✅ Countdown visible in viewer status bar
- ✅ Warning dialog before deletion
- ✅ Files deleted after 5 minutes

---

### **Test Case 3: Self-Destruct View Count (1 view)**
**Steps:**
1. In sender: Type `send`
2. Select: `bob`
3. Message: `Test 3: One-time view only - READ CAREFULLY!`
4. Self-destruct: `2` (After 1 view)

**Expected Result:**
- ✅ Message visible only once
- ✅ Files deleted after first reveal
- ✅ Warning shown: "1 view remaining"

---

### **Test Case 4: Self-Destruct View Count (3 views)**
**Steps:**
1. In sender: Type `send`
2. Select: `bob`
3. Message: `Test 4: You can read this 3 times`
4. Self-destruct: `4` (After N views)
5. Views: `3`

**Expected Result:**
- ✅ Counter decrements: 3→2→1→0
- ✅ Warning updates each time
- ✅ Deleted after 3rd view

---

### **Test Case 5: Long Message Test**
**Steps:**
1. In sender: Type `send`
2. Select: `bob`
3. Message: `Test 5: This is a very long message to test the embedding capacity and PSNR quality. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.`
4. Self-destruct: `1`

**Expected Result:**
- ✅ Long message embedded successfully
- ✅ PSNR still > 40 dB
- ✅ Full message readable in viewer

---

## 🎨 VIEWER FEATURE TESTS

### **Test Case 6: Keyboard Shortcuts**
**Test in Receiver Directory (H:\Layerx TEST):**

1. **Ctrl+O** - Open image
   - ✅ File dialog appears
   
2. **Ctrl+M** - Load metadata  
   - ✅ Metadata loads automatically (if paired with image)
   
3. **Ctrl+I** - Image Metadata Inspector
   - ✅ Terminal shows: File size, dimensions, EXIF, embedding stats, capacity
   
4. **Ctrl+T** - Toggle theme
   - ✅ Switches dark/light mode
   
5. **F5** - Refresh thumbnails
   - ✅ Reloads recent files list
   
6. **Ctrl+R** - Reveal message
   - ✅ Prompts for PIN (1234)
   
7. **Ctrl+Q** - Quit
   - ✅ Application closes

---

### **Test Case 7: PSNR Quality Indicator**
**Steps:**
1. Load any stego image + metadata
2. Check status bar (bottom right)

**Expected Result:**
- ✅ Shows: "PSNR: XX.X dB (Excellent/Good/Fair)"
- ✅ Color coded:
  - Green (>50 dB) = Excellent
  - Yellow (40-50 dB) = Good
  - Red (<40 dB) = Fair

---

### **Test Case 8: Drag & Drop**
**Steps:**
1. Open viewer
2. Drag `bob_TIMESTAMP_IP.png` from explorer
3. Drop on window

**Expected Result:**
- ✅ Image loads
- ✅ Auto-detects and loads matching JSON
- ✅ Status updates

---

### **Test Case 9: Image Metadata Inspector (Terminal)**
**Steps:**
1. Load image + metadata in viewer
2. Press `Ctrl+I`
3. Check terminal output

**Expected Result:**
```
============================================================
   IMAGE METADATA INSPECTOR
============================================================

📁 FILE: bob_20251226_120000_169_254_88_214.png
📏 Size: 245.67 KB
🖼️  Dimensions: 800 x 600 pixels
🎨 Mode: RGB
📊 Format: PNG

📝 EXIF DATA: None

🔐 EMBEDDING STATISTICS:
   Payload Size: 156 bytes (1248 bits)
   Total Capacity: ~28800 bytes
   Used: 0.5%
   Remaining: ~28644 bytes

📊 QUALITY METRICS:
   PSNR: 52.45 dB (Excellent)

============================================================
```

---

### **Test Case 10: PIN Authentication**
**Steps:**
1. Load image + metadata
2. Hover over "MESSAGE INFO" header
3. Click invisible button (top-right area)
4. Test wrong PIN: `0000`
5. Test correct PIN: `1234`

**Expected Result:**
- ❌ Wrong PIN: Error message, no decryption
- ✅ Correct PIN: Message decrypts and displays

---

### **Test Case 11: Self-Destruct Countdown Visual**
**Steps:**
1. Send message with 5-minute timer (Test Case 2)
2. Load in viewer and reveal with PIN
3. Watch status bar

**Expected Result:**
- ✅ Timer label appears: "⏱️ Self-Destruct: 04:59"
- ✅ Counts down every second
- ✅ Warning dialog before deletion

---

### **Test Case 12: Recent Files List**
**Steps:**
1. Send multiple messages (at least 5)
2. Press F5 in viewer

**Expected Result:**
- ✅ Terminal shows: "Found X recent messages"
- ✅ List loads PNG+JSON pairs

---

## 🔬 ADVANCED TESTS

### **Test Case 13: Multiple Rapid Messages**
**Steps:**
Send 3 messages in quick succession (< 30 seconds apart)

**Expected Result:**
- ✅ All messages received
- ✅ Unique filenames (different timestamps)
- ✅ No file conflicts

---

### **Test Case 14: Capacity Limit Test**
**Steps:**
Try sending a very large message (>500 characters)

**Expected Result:**
- ⚠️ May show warning if exceeds capacity
- ✅ PSNR may drop but still readable

---

### **Test Case 15: File Naming Verification**
**Steps:**
1. Check receiver directory after each message
2. Verify format: `{username}_{timestamp}_{ip}.png` + `.json`

**Expected Result:**
- ✅ Format: `bob_20251226_143055_169_254_88_214.png`
- ✅ Matching JSON has same base name

---

## ✅ SUCCESS CRITERIA

**All features working if:**
- [x] All 15 test cases pass
- [x] No errors in terminal
- [x] PSNR > 40 dB for all messages
- [x] Self-destruct works correctly
- [x] Keyboard shortcuts functional
- [x] PIN authentication secure
- [x] Metadata inspector shows accurate data

---

## 🐛 KNOWN LIMITATIONS
- Timer countdown runs in separate thread
- Windows Hello biometric (if available) uses PIN fallback
- EXIF data may not be present in PNG files
- Drag & drop requires tkinterdnd2 (optional)

---

## 📊 TEST RESULTS

### Test Execution Date: _____________

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1 - Basic Message | ⬜ | |
| TC2 - Timer Destruct | ⬜ | |
| TC3 - 1 View Destruct | ⬜ | |
| TC4 - N View Destruct | ⬜ | |
| TC5 - Long Message | ⬜ | |
| TC6 - Keyboard Shortcuts | ⬜ | |
| TC7 - PSNR Display | ⬜ | |
| TC8 - Drag & Drop | ⬜ | |
| TC9 - Metadata Inspector | ⬜ | |
| TC10 - PIN Auth | ⬜ | |
| TC11 - Timer Visual | ⬜ | |
| TC12 - Recent Files | ⬜ | |
| TC13 - Rapid Messages | ⬜ | |
| TC14 - Capacity Test | ⬜ | |
| TC15 - File Naming | ⬜ | |

---

**Tested By:** _____________  
**Overall Result:** ⬜ PASS / ⬜ FAIL
